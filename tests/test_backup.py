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


def _dump(source: Path, destination: Path, *, compress: bool = False, scoped: bool = False) -> None:
    """Write the table dumps. ``scoped`` applies the same filtering the real
    ``--scope full`` does, which is what keeps comments.sql to award-granting
    rows; the round-trip tests want everything and leave it off."""
    destination.mkdir(parents=True, exist_ok=True)
    queries = dump_sql.queries_for("full") if scoped else {}
    connection = sqlite3.connect(source)
    dump_sql.dump_schema(connection, destination, compress=compress)
    for table in dump_sql.TABLES:
        dump_sql.dump_table(
            connection, table, destination, query=queries.get(table), compress=compress
        )
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
    assert out.joinpath("award_comments.sql").read_bytes().count(b"\r") > 0

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


def _comment_count(path: Path) -> int:
    connection = sqlite3.connect(path)
    try:
        return int(connection.execute("SELECT COUNT(*) FROM comments").fetchone()[0])
    finally:
        connection.close()


def _add_comments(path: Path, n: int) -> None:
    connection = sqlite3.connect(path)
    connection.executemany(
        "INSERT INTO comments VALUES (?, 100, 'later')",
        [(2000 + i,) for i in range(n)],
    )
    connection.commit()
    connection.close()


@pytest.mark.slow
def test_refuses_to_restore_over_a_fuller_database(seeded: Path, tmp_path: Path) -> None:
    """The real hazard: backups/sql keeps only award-granting comments, so
    restoring it over the live archive would drop 3.6M rows on the floor."""
    out = tmp_path / "dump"
    _dump(seeded, out)
    _add_comments(seeded, 50)
    assert _comment_count(seeded) == 51

    with pytest.raises(SystemExit) as excinfo:
        restore_sql.restore(out, seeded, overwrite=True)

    assert "more rows than the dump" in str(excinfo.value)
    assert "comments" in str(excinfo.value)
    assert _comment_count(seeded) == 51, "the original must be left alone"


@pytest.mark.slow
def test_force_overrides_the_guard(seeded: Path, tmp_path: Path) -> None:
    out = tmp_path / "dump"
    _dump(seeded, out)
    _add_comments(seeded, 50)

    restore_sql.restore(out, seeded, overwrite=True, force=True)
    assert _comment_count(seeded) == 1


@pytest.mark.slow
def test_a_restore_that_grows_the_database_is_allowed(seeded: Path, tmp_path: Path) -> None:
    # Same size is fine too -- that is what an unchanged round trip looks like.
    out = tmp_path / "dump"
    _add_comments(seeded, 5)
    _dump(seeded, out)
    restore_sql.restore(out, seeded, overwrite=True)
    assert _comment_count(seeded) == 6


@pytest.mark.slow
def test_a_failed_restore_leaves_the_original_intact(seeded: Path, tmp_path: Path) -> None:
    # The old code unlinked the target first, so a dump that blew up half way
    # through took the archive with it.
    out = tmp_path / "dump"
    _dump(seeded, out)
    (out / "images.sql").write_text("this is not valid SQL;", encoding="utf-8")
    before = _comment_count(seeded)

    with pytest.raises(sqlite3.Error):
        restore_sql.restore(out, seeded, overwrite=True)

    assert _comment_count(seeded) == before
    assert not (seeded.parent / (seeded.name + ".partial")).exists(), "temp file left behind"


def test_shrinkage_only_reports_tables_that_lost_rows() -> None:
    before = {"comments": 3_656_434, "images": 399_485, "awards": 39}
    after = {"comments": 7_389, "images": 399_485, "challenge_probes": 469}
    assert restore_sql.shrinkage(before, after) == {"comments": (3_656_434, 7_389)}


@pytest.fixture
def multi_challenge(tmp_path: Path) -> Path:
    """Two challenges, each with comments, one of which granted an award."""
    path = tmp_path / "multi.sqlite"
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
        INSERT INTO members VALUES (1, 'someone');
        INSERT INTO challenges VALUES (10, 'Ten'), (2, 'Two');
        INSERT INTO images VALUES (100, 10, '[]'), (200, 2, '[]');
        INSERT INTO awards VALUES (1, 'an-award');
        INSERT INTO award_grants VALUES (1, 1, 100, 1000);
    """)
    connection.executemany(
        "INSERT INTO comments VALUES (?, ?, ?)",
        [(1000, 100, "granted it\r\nwith a CR")]
        + [(1001 + i, 100, f"chatter {i}") for i in range(30)]
        + [(2000 + i, 200, f"other challenge {i}") for i in range(12)],
    )
    connection.commit()
    connection.close()
    return path


def _dump_full(source: Path, destination: Path, *, compress: bool = False) -> None:
    """Everything `--scope full` writes: scoped tables plus the comment corpus."""
    _dump(source, destination, compress=compress, scoped=True)
    connection = sqlite3.connect(source)
    dump_sql.dump_challenge_comments(connection, destination, compress=compress)
    connection.close()


@pytest.mark.slow
def test_challenge_comments_are_one_file_per_challenge(multi_challenge: Path, tmp_path: Path):
    out = tmp_path / "dump"
    _dump_full(multi_challenge, out)
    names = sorted(p.name for p in (out / "challenge_comments").iterdir())
    assert names == ["10.sql", "2.sql"]


@pytest.mark.slow
def test_full_restore_brings_back_every_comment(multi_challenge: Path, tmp_path: Path):
    out = tmp_path / "dump"
    _dump_full(multi_challenge, out)

    partial = tmp_path / "partial.sqlite"
    restore_sql.restore(out, partial)
    assert _comment_count(partial) == 1, "the default restore stays award-only"

    whole = tmp_path / "whole.sqlite"
    counts = restore_sql.restore(out, whole, full=True)
    assert _comment_count(whole) == 43
    assert counts["comments"] == 43

    connection = sqlite3.connect(whole)
    text = connection.execute("SELECT raw_comment FROM comments WHERE id = 1000").fetchone()[0]
    connection.close()
    assert text == "granted it\r\nwith a CR", "carriage returns must survive the corpus too"


@pytest.mark.slow
def test_full_restore_does_not_collide_with_comments_sql(multi_challenge: Path, tmp_path: Path):
    # comments.sql is a subset of the corpus. Replaying both would hit the
    # primary key, so --full must substitute rather than add.
    out = tmp_path / "dump"
    _dump_full(multi_challenge, out)
    restore_sql.restore(out, tmp_path / "ok.sqlite", full=True)  # must not raise


@pytest.mark.slow
def test_full_restore_needs_the_corpus_to_exist(multi_challenge: Path, tmp_path: Path):
    out = tmp_path / "dump"
    _dump(multi_challenge, out)  # no challenge_comments/
    with pytest.raises(SystemExit, match="challenge_comments"):
        restore_sql.restore(out, tmp_path / "x.sqlite", full=True)


@pytest.mark.slow
def test_unchanged_challenges_redump_byte_identically(multi_challenge: Path, tmp_path: Path):
    # The whole reason for sharding: git must see nothing to store for a
    # challenge that did not change.
    first, second = tmp_path / "a", tmp_path / "b"
    _dump_full(multi_challenge, first)
    connection = sqlite3.connect(multi_challenge)
    connection.execute("INSERT INTO comments VALUES (2999, 200, 'brand new')")
    connection.commit()
    connection.close()
    _dump_full(multi_challenge, second)

    unchanged = "10.sql"
    changed = "2.sql"
    assert (first / "challenge_comments" / unchanged).read_bytes() == (
        second / "challenge_comments" / unchanged
    ).read_bytes()
    assert (first / "challenge_comments" / changed).read_bytes() != (
        second / "challenge_comments" / changed
    ).read_bytes()


@pytest.mark.slow
def test_stale_challenge_files_are_removed(multi_challenge: Path, tmp_path: Path):
    out = tmp_path / "dump"
    _dump_full(multi_challenge, out)
    connection = sqlite3.connect(multi_challenge)
    connection.execute("DELETE FROM comments WHERE image_id = 200")
    connection.commit()
    connection.close()
    _dump_full(multi_challenge, out)
    assert sorted(p.name for p in (out / "challenge_comments").iterdir()) == ["10.sql"]


@pytest.mark.slow
def test_a_partial_restore_then_dump_would_gut_the_corpus(multi_challenge: Path, tmp_path: Path):
    """Why the weekly workflow must restore with --full.

    The dump prunes challenge_comments/ files for challenges the database does
    not have. Restore award-only, dump, and the corpus for every challenge that
    had no award is deleted. This pins the shape of that failure so nobody
    'simplifies' the workflow back into it.
    """
    out = tmp_path / "dump"
    _dump_full(multi_challenge, out)
    assert len(list((out / "challenge_comments").iterdir())) == 2

    # The wrong way round: award-only restore, then dump over the same directory.
    partial = tmp_path / "partial.sqlite"
    restore_sql.restore(out, partial)
    _dump_full(partial, out)
    survivors = sorted(p.name for p in (out / "challenge_comments").iterdir())
    assert survivors == ["10.sql"], "challenge 2 had no award, so its comments are gone"

    # The right way round: --full in, --full out, nothing lost.
    out2 = tmp_path / "dump2"
    _dump_full(multi_challenge, out2)
    whole = tmp_path / "whole.sqlite"
    restore_sql.restore(out2, whole, full=True)
    _dump_full(whole, out2)
    assert sorted(p.name for p in (out2 / "challenge_comments").iterdir()) == ["10.sql", "2.sql"]
    assert _comment_count(whole) == 43
