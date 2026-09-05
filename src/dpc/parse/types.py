"""Records produced by the parsers.

These are plain frozen dataclasses with no database, network or filesystem
dependency. A parser turns an HTML string into one of these; the storage layer
turns one of these into a row. Keeping the two apart is what makes the parsers
testable against checked-in fixture HTML.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

VOTE_BUCKETS = 10
"""Vote breakdowns are always the ten buckets for scores 1..10."""


@dataclass(frozen=True, slots=True)
class MemberRecord:
    id: int
    name: str
    join_date: date | None
    cancelled: bool = False
    """True when the profile page reports a cancelled membership.

    The old scraper stamped cancelled members with ``arrow.now().date()``, which
    silently wrote a fabricated join date that drifted every run. A cancelled
    member now honestly has ``join_date is None``.
    """


@dataclass(frozen=True, slots=True)
class ChallengeRecord:
    id: int
    name: str
    description: str
    submission_start: date
    submission_end: date
    voting_start: date
    voting_end: date
    num_submissions: int
    num_disqualifications: int
    num_votes: int
    num_comments: int
    average_score: float
    highest_score: float
    median_score: float
    lowest_score: float


@dataclass(frozen=True, slots=True)
class ImageStats:
    votes: tuple[int, ...]
    disqualified: bool
    position: int | None = None
    average_all: float | None = None
    average_commenters: float | None = None
    average_participants: float | None = None
    average_non_participants: float | None = None
    num_views: int | None = None
    num_votes: int | None = None

    def __post_init__(self) -> None:
        if self.votes and len(self.votes) != VOTE_BUCKETS:
            msg = f"expected {VOTE_BUCKETS} vote buckets, got {len(self.votes)}"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class ImageRecord:
    id: int
    challenge_id: int
    photographer_id: int
    name: str
    stats: ImageStats


@dataclass(frozen=True, slots=True)
class CommentRecord:
    id: int
    image_id: int
    commenter_id: int
    commenter_name: str
    raw_comment: str
    """The comment's inner HTML. Award matching runs against this, because the
    award markers are image/anchor URLs that do not survive text extraction."""
    comment: str
    date: datetime
    edited: datetime | None
    made_during_challenge: bool
