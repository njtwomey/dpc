from __future__ import annotations

import time

import httpx
import pytest

from dpc.config import Settings
from dpc.scrape.client import DpcClient


def _client(**overrides) -> DpcClient:
    options = {"request_delay": 0.0, "max_retries": 1, **overrides}
    settings = Settings(_env_file=None, **options)
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            404 if "missing" in str(request.url) else 200,
            text=f"page for {request.url.path}",
        )
    )
    return DpcClient(settings, None, client=httpx.Client(transport=transport, base_url="http://x"))


class TestGetMany:
    def test_returns_every_page_keyed_by_path(self):
        with _client() as client:
            pages = client.get_many(["/a", "/b", "/c"], workers=4)
        assert set(pages) == {"/a", "/b", "/c"}
        assert "page for /a" in pages["/a"]

    def test_empty_input_makes_no_requests(self):
        with _client() as client:
            assert client.get_many([]) == {}

    def test_one_worker_takes_the_serial_path(self):
        with _client() as client:
            assert len(client.get_many(["/a", "/b"], workers=1)) == 2

    def test_a_failing_page_is_absent_rather_than_fatal(self):
        # One bad page must not sink the batch; the caller decides what a gap means.
        with _client() as client:
            pages = client.get_many(["/a", "/missing", "/b"], workers=4)
        assert set(pages) == {"/a", "/b"}


class TestPacing:
    def test_each_worker_paces_itself(self):
        # The delay is per worker, so N workers issue roughly N times the rate.
        # Eight pages at 0.05s across four workers should take about two slots,
        # not eight.
        with _client(request_delay=0.05) as client:
            start = time.monotonic()
            client.get_many([f"/p{i}" for i in range(8)], workers=4)
            elapsed = time.monotonic() - start
        assert elapsed < 8 * 0.05

    def test_a_single_worker_still_waits_between_requests(self):
        with _client(request_delay=0.05) as client:
            start = time.monotonic()
            client.get("/a")
            client.get("/b")
            elapsed = time.monotonic() - start
        assert elapsed >= 0.05


class TestLogin:
    def test_without_credentials_it_refuses(self):
        from dpc.scrape.client import LoginError

        with _client() as client, pytest.raises(LoginError, match="no credentials"):
            client.login()

    def test_settings_are_readable_for_pool_sizing(self):
        with _client() as client:
            assert client.settings.fetch_workers >= 1
