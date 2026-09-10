"""Rebuild a SQLite database from the SQL files written by ``dump_sql.py``.

Files are replayed in dependency order -- schema first, then each table -- so
foreign keys are satisfied as it goes. Plain and gzipped files are both
accepted; the directory can hold either.

Refuses to overwrite an existing database unless told to, because restoring
over a live archive is not something to do by accident. Even with
``--overwrite`` it refuses when the existing database holds *more* rows than
the dump would put back: without ``--full`` only ``award_comments.sql`` is
replayed, so restoring over a full archive would discard millions of comments.
``--force`` overrides that, and says so loudly.

The rebuild happens in a ``.partial`` file beside the target which is swapped
into place at the end, so a restore that dies halfway leaves the original
untouched rather than deleted.

``--full`` replays ``challenge_comments/`` -- the whole 3.6M-comment corpus --
in place of ``award_comments.sql``, which holds only the ones that granted an
award. In place of, not as well as: the second is a subset of the first, and
replaying both would collide on the primary key.

Usage::

    uv run python scripts/restore_sql.py --from backups/sql --to rebuilt.sqlite
    uv run python scripts/restore_sql.py --from backups/sql --full --overwrite
"""

from __future__ import annotations

import argparse
import gzip
import sqlite3
import sys
from collections.abc import Iterable
from pathlib import Path

from loguru import logger
from tqdm import tqdm

from dpc.config import Settings
from dpc.log import configure

# Same order dump_sql.py writes them in: file stems, which are not always the
# table they fill.
ORDER: tuple[str, ...] = (
    "schema",
    "members",
    "challenges",
    "images",
    "award_comments",
    "awards",
    "award_grants",
    "challenge_probes",
)

TABLE_FOR = {"award_comments": "comments"}


COMMENTS_DIR = "challenge_comments"


def challenge_comment_files(source: Path) -> list[Path]:
    """Every per-challenge comment dump, oldest challenge first."""
    directory = source / COMMENTS_DIR
    if not directory.is_dir():
        return []
    return sorted(
        (p for p in directory.iterdir() if p.name.endswith((".sql", ".sql.gz"))),
        key=lambda p: int(p.name.split(".", 1)[0]),
    )


def find(source: Path, name: str) -> Path | None:
    """The plain or gzipped file for ``name``, whichever is present."""
    for candidate in (source / f"{name}.sql", source / f"{name}.sql.gz"):
        if candidate.is_file():
            return candidate
    return None


def read(path: Path) -> str:
    """Read a dump verbatim.

    ``newline=""`` matters: comment HTML contains carriage returns, and the
    default universal-newline translation would rewrite every ``\r`` to ``\n``
    on the way in. That is invisible until you dump the restored database and
    diff it against the file you restored from -- 21,806 characters of the
    archive quietly changed.
    """
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
            return handle.read()
    # Path.read_text gained newline= only in 3.13; open() has always had it.
    with path.open(encoding="utf-8", newline="") as handle:
        return handle.read()


def row_counts(path: Path, tables: Iterable[str]) -> dict[str, int]:
    """Rows per table in an existing database.

    Tolerant on purpose: a target that is missing, empty, not SQLite at all or
    simply lacks a table contributes nothing, because this only ever feeds a
    safety comparison. Anything it cannot read is not evidence of loss.
    """
    if not path.is_file() or path.stat().st_size == 0:
        return {}

    counts: dict[str, int] = {}
    try:
        connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error:
        return {}
    try:
        for table in tables:
            try:
                counts[table] = int(
                    connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]  # noqa: S608
                )
            except sqlite3.Error:
                continue
    finally:
        connection.close()
    return counts


def shrinkage(existing: dict[str, int], rebuilt: dict[str, int]) -> dict[str, tuple[int, int]]:
    """Tables the restore would leave smaller, as ``{table: (before, after)}``."""
    return {
        table: (before, rebuilt[table])
        for table, before in existing.items()
        if table in rebuilt and before > rebuilt[table]
    }


def _build(present: list[tuple[str, Path]], into: Path) -> dict[str, int]:
    """Replay the dump files into a fresh database. Returns row counts."""
    connection = sqlite3.connect(into)
    try:
        for _, path in tqdm(present, desc="restoring", unit="file", disable=None):
            connection.executescript(read(path))
            connection.commit()

        counts = {
            name: int(connection.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0])  # noqa: S608
            for name in dict.fromkeys(name for name, _ in present)
            if name != "schema"
        }
        problems = connection.execute("PRAGMA foreign_key_check").fetchall()
    finally:
        connection.close()

    if problems:
        logger.error("{} foreign key violations after restore", len(problems))
    return counts


def restore(
    source: Path,
    target: Path,
    *,
    overwrite: bool = False,
    force: bool = False,
    full: bool = False,
) -> dict[str, int]:
    """Replay every dump file into ``target``. Returns row counts per table."""
    if target.exists() and not overwrite:
        msg = f"{target} already exists; pass --overwrite to replace it"
        raise SystemExit(msg)

    present = [
        (TABLE_FOR.get(stem, stem), path)
        for stem in ORDER
        if (path := find(source, stem)) is not None
    ]
    if not present:
        msg = f"no dump files found in {source}"
        raise SystemExit(msg)

    if full:
        corpus = challenge_comment_files(source)
        if not corpus:
            msg = f"--full needs {source / COMMENTS_DIR}, which does not exist"
            raise SystemExit(msg)
        # In place of comments.sql, not alongside it: comments.sql is a subset,
        # so replaying both would hit the primary key. Slotted in at the same
        # position so images are already there for the foreign key.
        expanded: list[tuple[str, Path]] = []
        for name, path in present:
            if name == "comments":
                expanded.extend(("comments", p) for p in corpus)
            else:
                expanded.append((name, path))
        present = expanded

    target.parent.mkdir(parents=True, exist_ok=True)

    # Built beside the target and swapped in at the end. The old code unlinked
    # the target first, so a restore that failed part-way through destroyed the
    # original and left a stump in its place.
    partial = target.with_name(target.name + ".partial")
    partial.unlink(missing_ok=True)
    try:
        counts = _build(present, partial)

        before = row_counts(target, counts)
        lost = shrinkage(before, counts)
        if lost and not force:
            detail = "\n".join(
                f"    {table:<18}{was:>12,} -> {now:<12,} ({now - was:+,})"
                for table, (was, now) in sorted(lost.items())
            )
            msg = (
                f"refusing to overwrite {target}: it holds more rows than the dump.\n"
                f"{detail}\n"
                "  The default dump keeps only award-granting comments, so restoring it "
                "over a full archive discards the rest.\n"
                "  Restore somewhere else with --to, or pass --force if losing those rows "
                "is genuinely what you want."
            )
            raise SystemExit(msg)

        if lost:
            for table, (was, now) in sorted(lost.items()):
                logger.warning("--force: {} {:,} -> {:,} rows", table, was, now)

        partial.replace(target)
    finally:
        partial.unlink(missing_ok=True)

    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="source", type=Path, default=Path("backups/sql"))
    parser.add_argument("--to", dest="target", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Replay challenge_comments/ -- every comment, not just award-granting ones",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite even when the existing database holds more rows than the dump",
    )
    args = parser.parse_args()
    configure(verbose=False)

    target = args.target
    if target is None:
        target = Path(Settings().database_url.split(":///", 1)[1])

    if not args.source.is_dir():
        logger.error("no such directory: {}", args.source)
        return 1

    logger.info("restoring {} -> {}", args.source, target)
    counts = restore(
        args.source, target, overwrite=args.overwrite, force=args.force, full=args.full
    )
    for table, count in counts.items():
        logger.info("{:<16} {:>9,} rows", table, count)
    logger.success("restored {} ({:,} bytes)", target, target.stat().st_size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
