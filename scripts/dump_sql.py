"""Dump the database as one SQL file per table, plus a schema file.

Unlike a SQLite snapshot this is text: diffable, portable, and readable without
the database to hand.

Two scopes:

``full``
    Every row, except that ``comments`` is filtered to those that actually
    granted an award -- around 7,000 rather than 3.6 million. A backup of the
    archive minus the comment corpus, and too large to keep in git.

``awards``
    Only rows an award touches. About 1 MB gzipped, small enough to commit, and
    enough to rebuild the site's database from nothing. Not a backup of the
    archive: the other 380,000 images and 3.6M comments are not in it.

Restore with ``scripts/restore_sql.py``, or ``make restore``.

Usage::

    uv run python scripts/dump_sql.py                          # full, to backups/sql/
    uv run python scripts/dump_sql.py --scope awards --gzip
    uv run python scripts/dump_sql.py --scope full --all-comments
"""

from __future__ import annotations

import argparse
import gzip
import sqlite3
import sys
from collections.abc import Iterator
from contextlib import AbstractContextManager
from pathlib import Path
from typing import IO, Any

from loguru import logger
from tqdm import tqdm

from dpc.config import Settings
from dpc.log import configure

# Written in dependency order, so replaying them in sequence satisfies the
# foreign keys without deferring anything.
TABLES: tuple[str, ...] = (
    "members",
    "challenges",
    "images",
    "comments",
    "awards",
    "award_grants",
    "challenge_probes",
)

# Rows reachable from an award, per table. Ordered by primary key so the dump is
# stable and its diffs readable.
AWARD_SCOPED: dict[str, str] = {
    "comments": """
        SELECT * FROM comments
        WHERE id IN (SELECT comment_id FROM award_grants WHERE comment_id IS NOT NULL)
        ORDER BY id
    """,
    "images": """
        SELECT * FROM images
        WHERE id IN (SELECT image_id FROM award_grants)
        ORDER BY id
    """,
    "challenges": """
        SELECT * FROM challenges
        WHERE id IN (SELECT challenge_id FROM award_grants)
        ORDER BY id
    """,
    # Everyone an award touches: who won it, who gives it, who wrote the
    # comment, and who took the picture.
    "members": """
        SELECT * FROM members WHERE id IN (
            SELECT recipient_id FROM award_grants
            UNION SELECT awarder_id FROM awards
            UNION SELECT photographer_id FROM images
                  WHERE id IN (SELECT image_id FROM award_grants)
            UNION SELECT commenter_id FROM comments
                  WHERE id IN (SELECT comment_id FROM award_grants WHERE comment_id IS NOT NULL)
        )
        ORDER BY id
    """,
}

ROWS_PER_INSERT = 200


def queries_for(scope: str) -> dict[str, str]:
    """Which rows each table contributes, for the requested scope."""
    if scope == "awards":
        return dict(AWARD_SCOPED)
    return {"comments": AWARD_SCOPED["comments"]}


def _literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, int | float):
        return repr(value)
    if isinstance(value, bytes):
        return "X'" + value.hex() + "'"
    return "'" + str(value).replace("'", "''") + "'"


def _open(path: Path, *, compress: bool) -> AbstractContextManager[IO[str]]:
    if compress:
        return gzip.open(path, "wt", encoding="utf-8")
    return path.open("w", encoding="utf-8")


def _count(connection: sqlite3.Connection, select: str) -> int:
    """How many rows ``select`` will return, for the progress bar."""
    return int(connection.execute(f"SELECT COUNT(*) FROM ({select})").fetchone()[0])  # noqa: S608


def dump_schema(connection: sqlite3.Connection, destination: Path, *, compress: bool) -> Path:
    """Every CREATE statement, so the dump can be replayed into an empty file."""
    path = destination / ("schema.sql.gz" if compress else "schema.sql")
    rows = connection.execute(
        "SELECT type, name, sql FROM sqlite_master "
        "WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' "
        "ORDER BY CASE type WHEN 'table' THEN 0 ELSE 1 END, name"
    ).fetchall()

    with _open(path, compress=compress) as out:
        out.write("-- schema for the dpc archive\n")
        out.write("PRAGMA foreign_keys=OFF;\nBEGIN TRANSACTION;\n\n")
        for kind, name, sql in rows:
            out.write(f"-- {kind}: {name}\n{sql};\n\n")
        out.write("COMMIT;\n")
    return path


def _batched(rows: Iterator[tuple[Any, ...]], size: int) -> Iterator[list[tuple[Any, ...]]]:
    batch: list[tuple[Any, ...]] = []
    for row in rows:
        batch.append(row)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def dump_table(
    connection: sqlite3.Connection,
    table: str,
    destination: Path,
    *,
    query: str | None = None,
    compress: bool,
) -> tuple[Path, int]:
    """Write one table's rows as multi-row INSERT statements."""
    columns = [r[1] for r in connection.execute(f"PRAGMA table_info({table})")]
    if not columns:
        msg = f"no such table: {table}"
        raise SystemExit(msg)

    # Resolved once and used for both the count and the rows, so they cannot
    # disagree. Table names come from TABLES and queries from AWARD_SCOPED, both
    # literals in this file; nothing here is caller-supplied.
    select = query or f"SELECT * FROM {table} ORDER BY rowid"  # noqa: S608
    total = _count(connection, select)
    cursor = connection.execute(select)
    column_list = ", ".join(f'"{c}"' for c in columns)
    path = destination / (f"{table}.sql.gz" if compress else f"{table}.sql")

    written = 0
    with (
        _open(path, compress=compress) as out,
        tqdm(
            total=total,
            desc=f"{table:<16}",
            unit="row",
            unit_scale=True,
            leave=False,
            disable=None,  # auto-off when stderr is not a terminal
        ) as bar,
    ):
        out.write(f"-- {table}\nPRAGMA foreign_keys=OFF;\nBEGIN TRANSACTION;\n")
        for batch in _batched(iter(cursor), ROWS_PER_INSERT):
            values = ",\n".join("(" + ", ".join(_literal(v) for v in row) + ")" for row in batch)
            out.write(f"INSERT INTO {table} ({column_list}) VALUES\n{values};\n")
            written += len(batch)
            bar.update(len(batch))
        out.write("COMMIT;\n")

    return path, written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=Path("backups/sql"))
    parser.add_argument("--gzip", action="store_true", help="Compress each file")
    parser.add_argument(
        "--scope",
        choices=("full", "awards"),
        default="full",
        help="full: every row, comments filtered to award-granting. "
        "awards: only rows an award touches, small enough to commit.",
    )
    parser.add_argument(
        "--all-comments",
        action="store_true",
        help="With --scope full, dump every comment too (large)",
    )
    args = parser.parse_args()
    configure(verbose=False)

    target = args.database
    if target is None:
        target = Path(Settings().database_url.split(":///", 1)[1])
    if not target.is_file():
        logger.error("no database at {}", target)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)

    queries = queries_for(args.scope)
    if args.all_comments and args.scope == "full":
        queries.pop("comments", None)

    logger.info("dumping {} ({} scope) -> {}", target, args.scope, args.out)
    total_bytes = dump_schema(connection, args.out, compress=args.gzip).stat().st_size

    for table in TABLES:
        query = queries.get(table)
        path, rows = dump_table(connection, table, args.out, query=query, compress=args.gzip)
        size = path.stat().st_size
        total_bytes += size
        logger.info(
            "{:<16} {:>9,} rows  {:>12,} bytes{}",
            table,
            rows,
            size,
            "  (scoped)" if query else "",
        )

    connection.close()
    logger.success("wrote {:,} bytes to {}", total_bytes, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
