"""Repair windows-1252 mojibake in an already-migrated SQLite database.

Rows scraped before the fetch layer decoded correctly hold C1 control characters
where curly quotes, dashes and ellipses belong -- 949 image titles among them.
New scrapes come through clean, so this only ever touches historical data, and
it is idempotent: running it twice changes nothing the second time.

Usage::

    uv run python scripts/repair_mojibake.py                 # report only
    uv run python scripts/repair_mojibake.py --write         # apply
    uv run python scripts/repair_mojibake.py --write --comments   # include the
                                                            # 3.6M comment rows
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from loguru import logger
from tqdm import tqdm

from dpc.config import Settings
from dpc.log import configure
from dpc.parse.text import repair_cp1252_mojibake

# Everything except the comment bodies, which are large and optional.
CORE_COLUMNS: tuple[tuple[str, str], ...] = (
    ("challenges", "name"),
    ("challenges", "description"),
    ("images", "name"),
    ("members", "name"),
    ("awards", "name"),
    ("awards", "description"),
)

COMMENT_COLUMNS: tuple[tuple[str, str], ...] = (
    ("comments", "comment"),
    ("comments", "raw_comment"),
)


def repair_column(connection: sqlite3.Connection, table: str, column: str, *, write: bool) -> int:
    """Repair one column. Returns how many rows needed it."""
    rows = connection.execute(
        f"SELECT rowid, {column} FROM {table} "  # noqa: S608 - names are literals above
        f"WHERE {column} IS NOT NULL AND {column} GLOB '*[' || CHAR(128) || '-' || CHAR(159) || ']*'"
    ).fetchall()

    changed = [
        (repaired, rowid)
        for rowid, value in rows
        if (repaired := repair_cp1252_mojibake(value)) != value
    ]

    if changed and write:
        connection.executemany(
            f"UPDATE {table} SET {column} = ? WHERE rowid = ?",  # noqa: S608
            changed,
        )
        connection.commit()

    return len(changed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=None, help="SQLite file to repair")
    parser.add_argument("--write", action="store_true", help="Apply changes (default: report)")
    parser.add_argument(
        "--comments", action="store_true", help="Also repair the 3.6M comment rows (slow)"
    )
    args = parser.parse_args()

    configure(verbose=False)

    target = args.database
    if target is None:
        url = Settings().database_url
        target = Path(url.split(":///", 1)[1])
    if not target.is_file():
        logger.error("no database at {}", target)
        return 1

    columns = CORE_COLUMNS + (COMMENT_COLUMNS if args.comments else ())
    connection = sqlite3.connect(target)

    total = 0
    for table, column in tqdm(columns, desc="scanning", unit="column"):
        count = repair_column(connection, table, column, write=args.write)
        total += count
        if count:
            logger.info(
                "{}.{}: {:,} rows{}", table, column, count, "" if args.write else " (dry run)"
            )

    connection.close()

    verb = "repaired" if args.write else "would repair"
    logger.success("{} {:,} rows in {}", verb, total, target)
    if total and not args.write:
        logger.info("re-run with --write to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
