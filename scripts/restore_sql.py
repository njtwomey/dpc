"""Rebuild a SQLite database from the SQL files written by ``dump_sql.py``.

Files are replayed in dependency order -- schema first, then each table -- so
foreign keys are satisfied as it goes. Plain and gzipped files are both
accepted; the directory can hold either.

Refuses to overwrite an existing database unless told to, because restoring
over a live archive is not something to do by accident.

Usage::

    uv run python scripts/restore_sql.py --from backups/sql --to rebuilt.sqlite
    uv run python scripts/restore_sql.py --from backups/sql --overwrite
"""

from __future__ import annotations

import argparse
import gzip
import sqlite3
import sys
from pathlib import Path

from loguru import logger
from tqdm import tqdm

from dpc.config import Settings
from dpc.log import configure

# Same order dump_sql.py writes them in.
ORDER: tuple[str, ...] = (
    "schema",
    "members",
    "challenges",
    "images",
    "comments",
    "awards",
    "award_grants",
    "challenge_probes",
)


def find(source: Path, name: str) -> Path | None:
    """The plain or gzipped file for ``name``, whichever is present."""
    for candidate in (source / f"{name}.sql", source / f"{name}.sql.gz"):
        if candidate.is_file():
            return candidate
    return None


def read(path: Path) -> str:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            return handle.read()
    return path.read_text(encoding="utf-8")


def restore(source: Path, target: Path, *, overwrite: bool = False) -> dict[str, int]:
    """Replay every dump file into ``target``. Returns row counts per table."""
    if target.exists():
        if not overwrite:
            msg = f"{target} already exists; pass --overwrite to replace it"
            raise SystemExit(msg)
        logger.warning("removing existing {}", target)
        target.unlink()

    present = [(name, path) for name in ORDER if (path := find(source, name)) is not None]
    if not present:
        msg = f"no dump files found in {source}"
        raise SystemExit(msg)

    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)

    for _, path in tqdm(present, desc="restoring", unit="file", disable=None):
        connection.executescript(read(path))
        connection.commit()

    counts: dict[str, int] = {}
    for name, _ in present:
        if name == "schema":
            continue
        counts[name] = int(connection.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0])  # noqa: S608

    problems = connection.execute("PRAGMA foreign_key_check").fetchall()
    connection.close()

    if problems:
        logger.error("{} foreign key violations after restore", len(problems))
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="source", type=Path, default=Path("backups/sql"))
    parser.add_argument("--to", dest="target", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    configure(verbose=False)

    target = args.target
    if target is None:
        target = Path(Settings().database_url.split(":///", 1)[1])

    if not args.source.is_dir():
        logger.error("no such directory: {}", args.source)
        return 1

    logger.info("restoring {} -> {}", args.source, target)
    counts = restore(args.source, target, overwrite=args.overwrite)
    for table, count in counts.items():
        logger.info("{:<16} {:>9,} rows", table, count)
    logger.success("restored {} ({:,} bytes)", target, target.stat().st_size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
