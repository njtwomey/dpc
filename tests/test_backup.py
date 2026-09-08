"""The SQL dump and restore must round-trip byte-for-byte.

``backups/sql`` is committed, and an automated refresh would restore it, scrape
into it and dump it again on every run. If the round trip is not exact, every
run rewrites the archive and the diff drowns the change you actually care
about.
"""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _load(name: str) -> ModuleType:
    """Import a scripts/ module. They are entry points, not a package."""
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


dump_sql = _load("dump_sql")
restore_sql = _load("restore_sql")

# A carriage return, a newline, and a quote: the three things that survive
# neither naive escaping nor universal-newline translation. Real comment HTML
# holds all three -- the live archive carries 21,806 carriage returns.
AWKWARD = "line one\r\nline two\rbare cr\nbare lf 'quoted' \\ backslash"


@pytest.fixture
def seeded(tmp_path: Path) -> Path:
    """A database shaped like the real one, with one awkward comment in it."""
    path = tmp_path / "source.sqlite"
    connection = sqlite3.connect(path)
    connection.executescript("""
        CREATE TABLE members (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE challenges (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE images (id INTEGER PRIMARY KEY, challenge_id INTEGER, votes TEXT);
        CREATE TABLE comments (id INTEGER PRIMARY KEY, image_id INTEGER, raw_comment TEXT);
        CREATE TABLE awards (id INTEGER PRIMARY KEY, slug TEXT);
        CREATE TABLE award_grants (
            id INTEGER PRIMARY KEY, award_id INTEGER, image_id INTEGER, comment_id INTEGER
        );
        CREATE TABLE challenge_probes (challenge_id INTEGER PRIMARY KEY, kind TEXT);
    """)
    connection.execute("INSERT INTO members VALUES (1, 'someone')")
    connection.execute("INSERT INTO challenges VALUES (10, 'A Challenge')")
    connection.execute("INSERT INTO images VALUES (100, 10, '[1,2,3]')")
    connection.execute("INSERT INTO comments VALUES (1000, 100, ?)", (AWKWARD,))
    connection.execute("INSERT INTO awards VALUES (1, 'an-award')")
    connection.execute("INSERT INTO award_grants VALUES (1, 1, 100, 1000)")
    connection.commit()
    connection.close()
    return path


def _dump(source: Path, destination: Path, *, compress: bool = False) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(source)
    dump_sql.dump_schema(connection, destination, compress=compress)
    for table in dump_sql.TABLES:
        dump_sql.dump_table(connection, table, destination, compress=compress)
    connection.close()


@pytest.mark.slow
def test_dump_restore_dump_is_byte_identical(seeded: Path, tmp_path: Path) -> None:
    first = tmp_path / "first"
    _dump(seeded, first)

    rebuilt = tmp_path / "rebuilt.sqlite"
    restore_sql.restore(first, rebuilt)

    second = tmp_path / "second"
    _dump(rebuilt, second)

    for path in sorted(first.iterdir()):
        assert path.read_bytes() == (second / path.name).read_bytes(), (
            f"{path.name} changed on the way through a restore"
        )


@pytest.mark.slow
def test_carriage_returns_survive_a_restore(seeded: Path, tmp_path: Path) -> None:
    # The specific failure: read_text() defaults to universal newlines, which
    # rewrites every \r to \n on the way in. Silent, and it mutates the archive.
    out = tmp_path / "dump"
    _dump(seeded, out)
    assert out.joinpath("comments.sql").read_bytes().count(b"\r") > 0

    rebuilt = tmp_path / "rebuilt.sqlite"
    restore_sql.restore(out, rebuilt)

    connection = sqlite3.connect(rebuilt)
    stored = connection.execute("SELECT raw_comment FROM comments WHERE id = 1000").fetchone()[0]
    connection.close()
    assert stored == AWKWARD


@pytest.mark.slow
def test_gzipped_dumps_round_trip_too(seeded: Path, tmp_path: Path) -> None:
    out = tmp_path / "gz"
    _dump(seeded, out, compress=True)

    rebuilt = tmp_path / "rebuilt.sqlite"
    restore_sql.restore(out, rebuilt)

    connection = sqlite3.connect(rebuilt)
    stored = connection.execute("SELECT raw_comment FROM comments WHERE id = 1000").fetchone()[0]
    connection.close()
    assert stored == AWKWARD
