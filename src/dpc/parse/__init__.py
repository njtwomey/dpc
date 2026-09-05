"""Pure HTML parsers.

Every function here takes an HTML string and returns a record. No network, no
database, no filesystem -- which is what makes them testable against the fixture
pages in ``tests/fixtures/html``.
"""

from dpc.parse.challenge import (
    ChallengeNotAvailableError,
    ChallengePage,
    classify,
    parse_challenge,
    parse_image_ids,
)
from dpc.parse.history import parse_challenge_ids
from dpc.parse.image import (
    ImageStatsUnavailableError,
    parse_comments,
    parse_image,
    parse_image_stats,
)
from dpc.parse.member import MemberProfileUnavailableError, parse_member
from dpc.parse.types import (
    ChallengeRecord,
    CommentRecord,
    ImageRecord,
    ImageStats,
    MemberRecord,
)

__all__ = [
    "ChallengeNotAvailableError",
    "ChallengePage",
    "ChallengeRecord",
    "CommentRecord",
    "ImageRecord",
    "ImageStats",
    "ImageStatsUnavailableError",
    "MemberProfileUnavailableError",
    "MemberRecord",
    "classify",
    "parse_challenge",
    "parse_challenge_ids",
    "parse_comments",
    "parse_image",
    "parse_image_ids",
    "parse_image_stats",
    "parse_member",
]
