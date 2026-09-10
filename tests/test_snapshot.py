"""The snapshot is the only thing standing between a disk failure and the loss
of 3.6 million comments, so its parts are tested rather than assumed."""

from __future__ import annotations

import gzip
import importlib.util
import sqlite3
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


snapshot = _load("snapshot")


@pytest.fixture
def database(tmp_path: Path) -> Path:
    path = tmp_path / "source.sqlite"
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE comments (id INTEGER PRIMARY KEY, raw_comment TEXT)")
    connection.executemany(
        "INSERT INTO comments VALUES (?, ?)",
        [(i, f"comment {i} with a \r\n carriage return") for i in range(500)],
    )
    connection.commit()
    connection.close()
    return path


@pytest.mark.slow
def test_snapshot_round_trips_to_an_identical_database(database: Path, tmp_path: Path) -> None:
    staged = tmp_path / "staged.sqlite"
    snapshot.vacuum_into(database, staged)
    archive = tmp_path / "dpc-2026-09-10.sqlite.gz"
    snapshot.compress(staged, archive)

    restored = tmp_path / "restored.sqlite"
    with gzip.open(archive, "rb") as src:
        restored.write_bytes(src.read())

    connection = sqlite3.connect(restored)
    rows = connection.execute("SELECT id, raw_comment FROM comments ORDER BY id").fetchall()
    connection.close()
    assert len(rows) == 500
    assert rows[7][1] == "comment 7 with a \r\n carriage return"


@pytest.mark.slow
def test_vacuum_into_reads_a_database_that_is_being_written(database: Path, tmp_path: Path) -> None:
    # The point of VACUUM INTO over a file copy: an open writer must not produce
    # a torn snapshot.
    writer = sqlite3.connect(database)
    writer.execute("INSERT INTO comments VALUES (9999, 'mid-flight')")
    writer.commit()

    staged = tmp_path / "staged.sqlite"
    snapshot.vacuum_into(database, staged)
    writer.close()

    connection = sqlite3.connect(staged)
    total = connection.execute("SELECT COUNT(*) FROM comments").fetchone()[0]
    connection.close()
    assert total == 501


@pytest.mark.slow
def test_verify_reads_every_byte_back(database: Path, tmp_path: Path) -> None:
    archive = tmp_path / "a.sqlite.gz"
    snapshot.compress(database, archive)
    assert snapshot.verify(archive) == database.stat().st_size


@pytest.mark.slow
def test_verify_rejects_a_truncated_archive(database: Path, tmp_path: Path) -> None:
    archive = tmp_path / "a.sqlite.gz"
    snapshot.compress(database, archive)
    archive.write_bytes(archive.read_bytes()[:-64])
    with pytest.raises((OSError, EOFError, gzip.BadGzipFile)):
        snapshot.verify(archive)


def test_prune_keeps_the_newest(tmp_path: Path) -> None:
    for day in ("01", "02", "03", "04"):
        (tmp_path / f"dpc-2026-09-{day}.sqlite.gz").write_bytes(b"x")
    removed = snapshot.prune(tmp_path, keep=2)
    assert [p.name for p in removed] == ["dpc-2026-09-01.sqlite.gz", "dpc-2026-09-02.sqlite.gz"]
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "dpc-2026-09-03.sqlite.gz",
        "dpc-2026-09-04.sqlite.gz",
    ]


def test_prune_keeps_everything_when_keep_is_zero(tmp_path: Path) -> None:
    (tmp_path / "dpc-2026-09-01.sqlite.gz").write_bytes(b"x")
    assert snapshot.prune(tmp_path, keep=0) == []
    assert len(list(tmp_path.iterdir())) == 1


def test_push_without_rclone_says_how_to_get_it(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(snapshot.shutil, "which", lambda _: None)
    with pytest.raises(SystemExit) as excinfo:
        snapshot.push(tmp_path / "a.gz", "gdrive:dpc")
    assert "brew install rclone" in str(excinfo.value)
