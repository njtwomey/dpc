"""Authenticated HTTP client for dpchallenge."""

from __future__ import annotations

import logging
import time
from types import TracebackType

import httpx

from dpc.config import Credentials, Settings
from dpc.scrape.encoding import decode_html

log = logging.getLogger(__name__)

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
        self._last_request_at = 0.0

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

        log.info("logging in as %s", self._credentials.username)
        response = self._request("POST", LOGIN_PATH, data=self._credentials.as_login_form())
        if self._credentials.username not in response:
            # Deliberately does not echo the response body -- it can contain the
            # submitted form values.
            msg = "login failed: the response did not show a logged-in session"
            raise LoginError(msg)

    def get(self, path: str) -> str:
        return self._request("GET", path)

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
                log.warning(
                    "%s %s failed (attempt %d/%d): %s; retrying in %.1fs",
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
        elapsed = time.monotonic() - self._last_request_at
        remaining = self._settings.request_delay - elapsed
        if remaining > 0:
            time.sleep(remaining)
        self._last_request_at = time.monotonic()
