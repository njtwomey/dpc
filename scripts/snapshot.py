"""Take a compressed, consistent snapshot of the database and push it offsite.

``backups/sql`` is not a backup of the archive. It keeps the ~7,000 comments
that granted an award; the other 3.6 million exist only in the local SQLite
file, and nothing in the repository can reconstruct them. This is what protects
them.

``VACUUM INTO`` rather than copying the file: it is SQLite's own snapshot
mechanism, so it is safe to run while something else is writing, and it drops
free pages on the way out. Copying a live database can tear a page and produce a
file that only fails later, when you need it.

Runs locally only. CI has no comment corpus to snapshot -- it rebuilds from
``backups/sql`` -- so wiring this into a workflow would faithfully back up the
0.2% that is already in git.

Usage::

    uv run python scripts/snapshot.py                # local snapshot only
    uv run python scripts/snapshot.py --push         # ...and copy it offsite
    uv run python scripts/snapshot.py --push --remote gdrive:dpc-backups
"""

from __future__ import annotations

import argparse
import gzip
import shutil
import sqlite3
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from loguru import logger
from tqdm import tqdm

from dpc.config import Settings
from dpc.log import configure

CHUNK = 8 * 1024 * 1024


def vacuum_into(source: Path, destination: Path) -> None:
    """SQLite's own consistent-snapshot mechanism. Refuses an existing target."""
    destination.unlink(missing_ok=True)
    connection = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    try:
        # The path is a bound parameter, so a quote in it cannot break out.
        connection.execute("VACUUM INTO ?", (str(destination),))
    finally:
        connection.close()


def compress(source: Path, destination: Path) -> None:
    """gzip, with a progress bar. Deliberately not xz: this is the only copy of
    the corpus, and gzip opens anywhere without installing anything."""
    total = source.stat().st_size
    with (
        source.open("rb") as raw,
        gzip.open(destination, "wb", compresslevel=6) as out,
        tqdm(total=total, unit="B", unit_scale=True, desc="compressing", disable=None) as bar,
    ):
        while chunk := raw.read(CHUNK):
            out.write(chunk)
            bar.update(len(chunk))


def verify(archive: Path) -> int:
    """Read the whole archive back. Returns the uncompressed size.

    A backup nobody has read is a hope, not a backup. Decompressing end to end
    checks gzip's CRC over every byte.
    """
    size = 0
    with gzip.open(archive, "rb") as handle:
        while chunk := handle.read(CHUNK):
            size += len(chunk)
    return size


def prune(directory: Path, keep: int) -> list[Path]:
    """Delete all but the newest ``keep`` snapshots. Returns what was removed."""
    if keep <= 0:
        return []
    snapshots = sorted(directory.glob("dpc-*.sqlite.gz"))
    doomed = snapshots[:-keep]
    for path in doomed:
        logger.info("pruning {}", path.name)
        path.unlink()
    return doomed


def push(archive: Path, remote: str) -> None:
    """Copy the snapshot to an rclone remote."""
    if not shutil.which("rclone"):
        msg = "rclone is not installed. `brew install rclone`, then `rclone config`."
        raise SystemExit(msg)

    logger.info("uploading {} -> {}", archive.name, remote)
    result = subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["rclone", "copy", "--progress", str(archive), remote],  # noqa: S607
        check=False,
    )
    if result.returncode != 0:
        msg = f"rclone exited {result.returncode}; the local snapshot is kept at {archive}"
        raise SystemExit(msg)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None, help="Snapshot directory")
    parser.add_argument("--push", action="store_true", help="Upload via rclone")
    parser.add_argument("--remote", default=None, help="Override DPC_BACKUP_REMOTE")
    parser.add_argument("--keep", type=int, default=None, help="Local snapshots to keep")
    args = parser.parse_args()
    configure(verbose=False)

    settings = Settings()
    source = args.database or settings.database_path
    if not source.is_file():
        logger.error("no database at {}", source)
        return 1

    directory = args.out or settings.snapshot_dir
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y-%m-%d")
    archive = directory / f"dpc-{stamp}.sqlite.gz"

    staged = directory / f"dpc-{stamp}.sqlite.staging"
    try:
        logger.info("snapshotting {} ({:,} bytes)", source, source.stat().st_size)
        vacuum_into(source, staged)
        compress(staged, archive)
    finally:
        staged.unlink(missing_ok=True)

    restored = verify(archive)
    packed = archive.stat().st_size
    logger.success(
        "{}  {:,} bytes ({:.0%} of {:,} restored)",
        archive.name,
        packed,
        packed / restored,
        restored,
    )

    prune(directory, args.keep if args.keep is not None else settings.backup_keep)

    remote = args.remote if args.remote is not None else settings.backup_remote
    if args.push:
        if not remote:
            msg = "no remote configured. Set DPC_BACKUP_REMOTE or pass --remote."
            raise SystemExit(msg)
        push(archive, remote)
        logger.success("offsite copy in {}", remote)
    elif remote:
        logger.info("not pushed. --push would copy it to {}", remote)

    return 0


if __name__ == "__main__":
    sys.exit(main())
