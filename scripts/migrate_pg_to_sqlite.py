"""One-shot migration of the legacy Postgres database into SQLite.

The old schema was created by peewee and stored ``images.votes`` as a Postgres
integer ARRAY; here it becomes a portable JSON column. Everything else maps
across unchanged apart from two deliberate corrections:

* ``bling``/``awards`` become ``awards``/``award_grants``
* cancelled members lose their fabricated join date

Usage::

    # restore the dump first, if it is not already loaded
    createdb dpcdb && psql -d dpcdb -f database-backup/backup.sql

    uv run python scripts/migrate_pg_to_sqlite.py \
        --source postgresql+psycopg://user@localhost:5432/dpcdb \
        --target sqlite+pysqlite:///dpc.sqlite

Re-runnable: the target is recreated from scratch each time.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from loguru import logger
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from tqdm import tqdm

from dpc.db.migrate import stamp
from dpc.db.models import Award, AwardGrant, Challenge, Comment, Image, Member
from dpc.db.session import create_all, create_db_engine
from dpc.log import configure

BATCH = 5_000


def _rows(engine: Engine, sql: str) -> Iterator[dict[str, Any]]:
    with engine.connect().execution_options(stream_results=True) as connection:
        result = connection.execute(text(sql))
        for partition in result.mappings().partitions(BATCH):
            yield from (dict(row) for row in partition)


def _copy(
    session: Session,
    source: Engine,
    sql: str,
    build: Any,
    label: str,
) -> int:
    total = 0
    pending: list[Any] = []
    with tqdm(
        desc=f"{label:<14}",
        unit="row",
        unit_scale=True,
        disable=None,  # auto-off when stderr is not a terminal
    ) as bar:
        for row in _rows(source, sql):
            pending.append(build(row))
            total += 1
            if len(pending) >= BATCH:
                session.bulk_save_objects(pending)
                session.commit()
                bar.update(len(pending))
                pending.clear()
        if pending:
            session.bulk_save_objects(pending)
            session.commit()
            bar.update(len(pending))
    logger.info("{:<14} {:>9,} rows", label, total)
    return total


def migrate(source_url: str, target_url: str, *, overwrite: bool = False) -> dict[str, int]:
    source = create_engine(source_url)

    target_file = Path(make_url(target_url).database or "")
    if overwrite and target_file.is_file():
        logger.warning("removing existing {}", target_file)
        target_file.unlink()
    elif target_file.is_file() and target_file.stat().st_size > 0:
        msg = (
            f"{target_file} already exists. A partial load cannot be resumed; "
            f"pass --overwrite to start again."
        )
        raise SystemExit(msg)

    target = create_db_engine(target_url)
    create_all(target)

    counts: dict[str, int] = {}
    with Session(target) as session:
        counts["members"] = _copy(
            session,
            source,
            "SELECT id, name, join_date FROM members ORDER BY id",
            lambda r: Member(
                id=r["id"],
                name=r["name"] or "",
                join_date=r["join_date"],
                cancelled=False,
            ),
            "members",
        )

        counts["challenges"] = _copy(
            session,
            source,
            """SELECT id, name, description, submission_start, submission_end,
                      voting_start, voting_end, num_submissions, num_disqualifications,
                      num_votes, num_comments, average_score, highest_score,
                      median_score, lowest_score
               FROM challenges ORDER BY id""",
            lambda r: Challenge(**dict(r)),
            "challenges",
        )

        counts["images"] = _copy(
            session,
            source,
            """SELECT id, challenge_id, photographer_id, name, votes,
                      average_all, average_comments, average_participants,
                      average_non_participants, num_views, num_votes, disqualified
               FROM images ORDER BY id""",
            lambda r: Image(
                id=r["id"],
                challenge_id=r["challenge_id"],
                photographer_id=r["photographer_id"],
                name=r["name"] or "",
                # Postgres ARRAY -> JSON list
                votes=list(r["votes"] or []),
                average_all=r["average_all"],
                # renamed: the parser always called these commenters
                average_commenters=r["average_comments"],
                average_participants=r["average_participants"],
                average_non_participants=r["average_non_participants"],
                num_views=r["num_views"],
                num_votes=r["num_votes"],
                disqualified=bool(r["disqualified"]),
            ),
            "images",
        )

        counts["comments"] = _copy(
            session,
            source,
            """SELECT id, commenter_id, image_id, raw_comment, comment,
                      date, edited, made_during_challenge
               FROM comments ORDER BY id""",
            lambda r: Comment(
                id=r["id"],
                commenter_id=r["commenter_id"],
                image_id=r["image_id"],
                raw_comment=r["raw_comment"] or "",
                comment=r["comment"] or "",
                date=r["date"],
                edited=r["edited"],
                made_during_challenge=bool(r["made_during_challenge"]),
            ),
            "comments",
        )

        # bling -> awards. `regex` was never a regex; it is a marker substring list.
        counts["awards"] = _copy(
            session,
            source,
            """SELECT id, awarder_id, name, slug, description, img_src, regex
               FROM bling ORDER BY id""",
            lambda r: Award(
                id=r["id"],
                awarder_id=r["awarder_id"],
                name=r["name"],
                slug=r["slug"],
                description=r["description"] or "",
                image_src=r["img_src"] or "",
                markers=[str(m) for m in (r["regex"] or [])],
            ),
            "awards",
        )

        # awards -> award_grants.
        #
        # DISTINCT ON collapses the handful of cases where an awarder mentioned
        # the same award on the same image in more than one comment. The award
        # was given once; the repeat is an artefact of matching on comments. The
        # earliest comment wins, which is exactly what awards.find_grants does,
        # so a migrated database matches one rebuilt from scratch.
        counts["award_grants"] = _copy(
            session,
            source,
            """SELECT DISTINCT ON (a.bling_id, a.image_id)
                      a.id, a.bling_id, a.user_id, a.comment_id,
                      a.image_id, a.challenge_id
               FROM awards a
               LEFT JOIN comments c ON c.id = a.comment_id
               ORDER BY a.bling_id, a.image_id, c.date NULLS LAST, a.comment_id""",
            lambda r: AwardGrant(
                id=r["id"],
                award_id=r["bling_id"],
                recipient_id=r["user_id"],
                comment_id=r["comment_id"],
                image_id=r["image_id"],
                challenge_id=r["challenge_id"],
            ),
            "award_grants",
        )

    source.dispose()
    target.dispose()

    # The schema came from create_all, so alembic has no record of it. Stamp it
    # as current, or the next `dpc db-init` would try to build it again.
    stamp(target_url)
    logger.info("stamped {} at the current alembic revision", target_url)

    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="SQLAlchemy URL of the Postgres database")
    parser.add_argument(
        "--target",
        default=f"sqlite+pysqlite:///{Path.cwd() / 'dpc.sqlite'}",
        help="SQLAlchemy URL of the SQLite file to create",
    )
    parser.add_argument("--overwrite", action="store_true", help="Delete an existing target first")
    args = parser.parse_args()

    configure(verbose=False)
    counts = migrate(args.source, args.target, overwrite=args.overwrite)
    for table, count in counts.items():
        logger.info("{:>14}: {:,}", table, count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
