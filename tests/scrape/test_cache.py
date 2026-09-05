from __future__ import annotations

from dpc.scrape.cache import HtmlCache


def test_round_trips_as_utf8(tmp_path):
    cache = HtmlCache(tmp_path)
    cache.write("challenge", 3882, "Hidden Gem — Quiz")

    assert cache.read("challenge", 3882) == "Hidden Gem — Quiz"
    stored = cache.path_for("challenge", 3882).read_bytes()
    assert "—".encode() in stored


def test_missing_entry_reads_as_none(tmp_path):
    assert HtmlCache(tmp_path).read("challenge", 1) is None
    assert HtmlCache(tmp_path).has("challenge", 1) is False


def test_creates_parent_directories(tmp_path):
    cache = HtmlCache(tmp_path / "deep" / "nested")
    cache.write("image", 500, "<html></html>")
    assert cache.has("image", 500)
