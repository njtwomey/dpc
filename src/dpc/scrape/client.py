"""Authenticated HTTP client for dpchallenge."""

from __future__ import annotations

import threading
import time
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from types import TracebackType

import httpx
from loguru import logger

from dpc.config import Credentials, Settings
from dpc.scrape.encoding import decode_html

BASE_URL = "https://www.dpchallenge.com"
LOGIN_PATH = "/login.php"


class LoginError(RuntimeError):
    """The login POST did not produce a logged-in session."""


class DpcClient:
    """A logged-in session, with polite pacing and bounded retries."""

    def __init__(
        self,
        settings: Settings,
        credentials: Credentials | None = None,
        *,
        client: httpx.Client | None = None,
    ) -> None:
        self._settings = settings
        self._credentials = credentials
        self._client = client or httpx.Client(
            base_url=BASE_URL,
            timeout=settings.request_timeout,
            follow_redirects=True,
            headers={"User-Agent": "dpc-parser (+personal archive; authorised)"},
        )
        # Per worker, so each thread paces its own requests. httpx.Client is
        # safe to share across threads.
        self._pacing = threading.local()

    @property
    def settings(self) -> Settings:
        return self._settings

    def __enter__(self) -> DpcClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def login(self) -> None:
        """Authenticate. Never logs the credentials."""
        if self._credentials is None:
            msg = "no credentials configured; set DPC_USERNAME and DPC_PASSWORD"
            raise LoginError(msg)

        logger.info("logging in as {}", self._credentials.username)
        response = self._request("POST", LOGIN_PATH, data=self._credentials.as_login_form())
        if self._credentials.username not in response:
            # Deliberately does not echo the response body -- it can contain the
            # submitted form values.
            msg = "login failed: the response did not show a logged-in session"
            raise LoginError(msg)

    def get(self, path: str) -> str:
        return self._request("GET", path)

    def get_many(self, paths: Iterable[str], *, workers: int | None = None) -> dict[str, str]:
        """Fetch many pages concurrently. Returns ``{path: html}``.

        A page that fails after its retries is simply absent from the result, so
        one bad page does not sink the batch; the caller decides what that means.
        """
        paths = list(paths)
        if not paths:
            return {}

        count = workers if workers is not None else self._settings.fetch_workers
        if count <= 1:
            return {path: self.get(path) for path in paths}

        results: dict[str, str] = {}
        with ThreadPoolExecutor(max_workers=count) as pool:
            for path, html in zip(paths, pool.map(self._get_or_none, paths), strict=True):
                if html is not None:
                    results[path] = html
        return results

    def _get_or_none(self, path: str) -> str | None:
        try:
            return self.get(path)
        except Exception:
            logger.exception("failed to fetch {}", path)
            return None

    def _request(self, method: str, path: str, **kwargs: object) -> str:
        last_error: Exception | None = None

        for attempt in range(1, self._settings.max_retries + 1):
            self._wait_turn()
            try:
                response = self._client.request(method, path, **kwargs)  # type: ignore[arg-type]
                response.raise_for_status()
            except (httpx.TransportError, httpx.HTTPStatusError) as error:
                last_error = error
                backoff = min(2.0**attempt, 30.0)
                logger.warning(
                    "{} {} failed (attempt {}/{}): {}; retrying in {:.1f}s",
                    method,
                    path,
                    attempt,
                    self._settings.max_retries,
                    type(error).__name__,
                    backoff,
                )
                time.sleep(backoff)
                continue

            return decode_html(response.content, response.charset_encoding)

        msg = f"{method} {path} failed after {self._settings.max_retries} attempts"
        raise ConnectionError(msg) from last_error

    def _wait_turn(self) -> None:
        last = getattr(self._pacing, "last_request_at", 0.0)
        remaining = self._settings.request_delay - (time.monotonic() - last)
        if remaining > 0:
            time.sleep(remaining)
        self._pacing.last_request_at = time.monotonic()
