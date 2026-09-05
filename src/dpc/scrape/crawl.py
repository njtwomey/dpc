"""Orchestration: fetch, parse, store.

Each step is a call into a layer that knows nothing about the others, which is
the difference from the old ``get_challenge``: that one function downloaded,
scraped, wrote to the database and recursed into images, so none of it could be
exercised without a live session and a live database.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session
from tqdm import tqdm

from dpc.db.models import Challenge, ChallengeProbe, Image, Member
from dpc.parse import challenge as challenge_parser
from dpc.parse import history as history_parser
from dpc.parse import image as image_parser
from dpc.parse import member as member_parser
from dpc.parse.image import ImageStatsUnavailableError
from dpc.parse.member import MemberProfileUnavailableError
from dpc.parse.types import MemberRecord
from dpc.scrape.cache import HtmlCache
from dpc.scrape.client import DpcClient
from dpc.scrape.store import (
    record_probe,
    upsert_challenge,
    upsert_comments,
    upsert_image,
    upsert_member,
)

CHALLENGE_PATH = "/challenge_results.php?CHALLENGE_ID={id}&show_full=1"
IMAGE_PATH = "/image.php?IMAGE_ID={id}"
MEMBER_PATH = "/profile.php?USER_ID={id}"
HISTORY_PATH = "/challenge_history.php?show_all=1"


@dataclass
class CrawlStats:
    challenges: int = 0
    images: int = 0
    comments: int = 0
    members: int = 0
    skipped_invalid: int = 0
    skipped_unfinished: int = 0
    failures: list[int] = field(default_factory=list)


class Crawler:
    def __init__(
        self,
        client: DpcClient,
        session: Session,
        cache: HtmlCache,
        *,
        refresh: bool = False,
    ) -> None:
        self._client = client
        self._session = session
        self._cache = cache
        self._refresh = refresh
        self._known_members: set[int] = set()

    # ---------------------------------------------------------------- fetch

    def _page(self, kind: str, key: int, path: str, *, cacheable: bool = True) -> str:
        """Return a page, from cache when allowed, otherwise from the network."""
        if cacheable and not self._refresh:
            cached = self._cache.read(kind, key)
            if cached is not None:
                return cached

        html = self._client.get(path)
        if cacheable:
            self._cache.write(kind, key, html)
        return html

    # ------------------------------------------------------------ discovery

    def challenge_ids_from_history(self) -> tuple[int, ...]:
        return history_parser.parse_challenge_ids(self._client.get(HISTORY_PATH))

    def pending_challenge_ids(self, candidates: list[int]) -> list[int]:
        """Drop ids already stored, and ids previously found to be invalid.

        An ``unfinished`` probe is deliberately *not* skipped: that challenge
        becomes a results page once voting closes.
        """
        stored = set(self._session.scalars(select(Challenge.id)))
        invalid = set(
            self._session.scalars(
                select(ChallengeProbe.challenge_id).where(ChallengeProbe.kind == "invalid")
            )
        )
        return [cid for cid in candidates if cid not in stored and cid not in invalid]

    # ----------------------------------------------------------------- work

    def crawl_challenges(self, challenge_ids: list[int], *, with_images: bool = True) -> CrawlStats:
        stats = CrawlStats()
        bar = tqdm(challenge_ids, desc="challenges", unit="ch", disable=None)
        for challenge_id in bar:
            bar.set_postfix_str(f"#{challenge_id}")
            try:
                self._crawl_challenge(challenge_id, stats, with_images=with_images)
            except ImageStatsUnavailableError:
                # The voting-breakdown panel is served only to a logged-in
                # session. If it has gone missing the session has expired, and
                # every subsequent image would fail the same way -- so stop
                # rather than work through thousands of pointless requests.
                self._session.rollback()
                logger.error(
                    "challenge {}: no voting breakdown, so the session is no longer "
                    "logged in. Stopping.",
                    challenge_id,
                )
                raise
            except Exception:
                logger.exception("challenge {} failed", challenge_id)
                stats.failures.append(challenge_id)
                self._session.rollback()
                # The rollback also undoes any member inserted while this
                # challenge was being crawled, but _known_members would still
                # claim they exist -- so a later challenge referencing one would
                # skip fetching it and then violate the foreign key. It is only
                # a cache; dropping it costs a few repeated lookups.
                self._known_members.clear()
        return stats

    def _crawl_challenge(self, challenge_id: int, stats: CrawlStats, *, with_images: bool) -> None:
        path = CHALLENGE_PATH.format(id=challenge_id)

        # An unfinished page must never be cached, or it is read back forever.
        html = (
            self._client.get(path) if self._refresh else self._cached_or_fetch(challenge_id, path)
        )
        kind = challenge_parser.classify(html)

        if kind is challenge_parser.ChallengePage.INVALID:
            record_probe(self._session, challenge_id, "invalid")
            self._session.commit()
            stats.skipped_invalid += 1
            return

        if kind is challenge_parser.ChallengePage.UNFINISHED:
            record_probe(self._session, challenge_id, "unfinished")
            self._session.commit()
            stats.skipped_unfinished += 1
            logger.info("challenge {} is still open; will retry later", challenge_id)
            return

        self._cache.write("challenge", challenge_id, html)
        record = challenge_parser.parse_challenge(html, challenge_id)
        upsert_challenge(self._session, record)
        record_probe(self._session, challenge_id, "results")
        stats.challenges += 1

        if with_images:
            image_ids = challenge_parser.parse_image_ids(html)
            for image_id in tqdm(
                image_ids,
                desc=f"  images of {challenge_id}",
                unit="img",
                leave=False,
                disable=None,
            ):
                self._crawl_image(image_id, challenge_id, stats)

        self._session.commit()

    def _cached_or_fetch(self, challenge_id: int, path: str) -> str:
        cached = self._cache.read("challenge", challenge_id)
        if cached is not None:
            return cached
        return self._client.get(path)

    def _crawl_image(self, image_id: int, challenge_id: int, stats: CrawlStats) -> None:
        html = self._page("image", image_id, IMAGE_PATH.format(id=image_id))

        record = image_parser.parse_image(html, image_id, challenge_id)
        self._ensure_member(record.photographer_id)
        if self._session.get(Image, image_id) is None:
            stats.images += 1
        upsert_image(self._session, record)

        comments = image_parser.parse_comments(html, image_id)
        for comment in comments:
            self._ensure_member(comment.commenter_id, comment.commenter_name)
        stats.comments += upsert_comments(self._session, comments)

    def refresh_members(self, member_ids: list[int]) -> int:
        """Refetch profiles and overwrite what is stored. Returns how many changed.

        Used to repair members the old scraper recorded badly -- a blank name, or
        the join date it invented for cancelled accounts.
        """
        updated = 0
        for member_id in tqdm(member_ids, desc="members", unit="member", disable=None):
            try:
                html = self._page("member", member_id, MEMBER_PATH.format(id=member_id))
                record = member_parser.parse_member(html, member_id)
            except MemberProfileUnavailableError as error:
                logger.warning("member {}: {}", member_id, error)
                continue
            except Exception:
                logger.exception("member {} failed", member_id)
                self._session.rollback()
                continue

            before = self._session.get(Member, member_id)
            was = (before.name, before.join_date, before.cancelled) if before else None
            member = upsert_member(self._session, record, trust_dates=True)
            if was != (member.name, member.join_date, member.cancelled):
                updated += 1
            self._session.commit()
        return updated

    def _ensure_member(self, member_id: int, fallback_name: str = "") -> None:
        if member_id in self._known_members:
            return
        if self._session.get(Member, member_id) is not None:
            self._known_members.add(member_id)
            return

        html = self._page("member", member_id, MEMBER_PATH.format(id=member_id))
        try:
            record = member_parser.parse_member(html, member_id, fallback_name=fallback_name)
        except MemberProfileUnavailableError as error:
            # An unreadable profile must not abandon the image that referenced
            # it: record what the comment already told us and move on.
            logger.warning("member {}: {}; storing name only", member_id, error)
            record = MemberRecord(id=member_id, name=fallback_name, join_date=None)
        upsert_member(self._session, record)
        self._known_members.add(member_id)


def utcnow() -> datetime:
    return datetime.now(UTC)
