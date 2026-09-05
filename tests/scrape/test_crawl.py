"""The crawler's transaction boundaries."""

from __future__ import annotations

from unittest.mock import MagicMock

from dpc.scrape.cache import HtmlCache
from dpc.scrape.crawl import Crawler


def _crawler(session, tmp_path) -> Crawler:
    return Crawler(MagicMock(), session, HtmlCache(tmp_path))


def test_a_failed_challenge_clears_the_member_cache(session, tmp_path):
    # A rollback undoes members inserted during the failed challenge, so the
    # cache that says "already stored" must not outlive it -- otherwise the next
    # challenge skips fetching a member that no longer exists and the foreign
    # key blows up.
    crawler = _crawler(session, tmp_path)
    crawler._known_members.update({1, 2, 3})

    def boom(*_args, **_kwargs):
        msg = "simulated failure"
        raise RuntimeError(msg)

    crawler._crawl_challenge = boom  # type: ignore[method-assign]
    stats = crawler.crawl_challenges([999])

    assert stats.failures == [999]
    assert crawler._known_members == set()


def test_a_successful_run_keeps_the_cache(session, tmp_path):
    crawler = _crawler(session, tmp_path)
    crawler._known_members.update({1, 2})
    crawler._crawl_challenge = lambda *_a, **_k: None  # type: ignore[method-assign]

    stats = crawler.crawl_challenges([1])

    assert stats.failures == []
    assert crawler._known_members == {1, 2}
