"""SQLAlchemy 2.0 models.

Naming note: the old schema had ``Bling`` (an award's *definition*) and
``Awards`` (a single *grant* of one). Those two names were near-impossible to
tell apart at a call site, so they are now :class:`Award` and
:class:`AwardGrant`.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base with a JSON type map for list columns."""

    type_annotation_map = {  # noqa: RUF012
        list[int]: JSON,
        list[str]: JSON,
        datetime: DateTime,
        date: Date,
        bool: Boolean,
        float: Float,
        int: Integer,
        str: String,
    }


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    """The site's USER_ID, not a surrogate key."""

    name: Mapped[str] = mapped_column(String(128), index=True)
    join_date: Mapped[date | None] = mapped_column(default=None)
    cancelled: Mapped[bool] = mapped_column(default=False)
    """A cancelled member has no join date, rather than a fabricated one."""

    images: Mapped[list[Image]] = relationship(back_populates="photographer")
    comments: Mapped[list[Comment]] = relationship(back_populates="commenter")

    def __repr__(self) -> str:
        return f"<Member {self.id} {self.name!r}>"


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(256), index=True)
    description: Mapped[str] = mapped_column(Text, default="")

    submission_start: Mapped[date]
    submission_end: Mapped[date]
    voting_start: Mapped[date]
    voting_end: Mapped[date]

    num_submissions: Mapped[int]
    num_disqualifications: Mapped[int]
    num_votes: Mapped[int]
    num_comments: Mapped[int]

    average_score: Mapped[float]
    highest_score: Mapped[float]
    median_score: Mapped[float]
    lowest_score: Mapped[float]

    images: Mapped[list[Image]] = relationship(back_populates="challenge")

    def __repr__(self) -> str:
        return f"<Challenge {self.id} {self.name!r}>"


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"), index=True
    )
    photographer_id: Mapped[int] = mapped_column(
        ForeignKey("members.id", ondelete="CASCADE"), index=True
    )

    name: Mapped[str] = mapped_column(String(256))

    votes: Mapped[list[int]] = mapped_column(JSON, default=list)
    """The ten-bucket score histogram. Was a Postgres ARRAY; JSON is portable."""

    disqualified: Mapped[bool] = mapped_column(default=False)
    position: Mapped[int | None] = mapped_column(default=None)
    average_all: Mapped[float | None] = mapped_column(default=None)
    average_commenters: Mapped[float | None] = mapped_column(default=None)
    average_participants: Mapped[float | None] = mapped_column(default=None)
    average_non_participants: Mapped[float | None] = mapped_column(default=None)
    num_views: Mapped[int | None] = mapped_column(default=None)
    num_votes: Mapped[int | None] = mapped_column(default=None)

    challenge: Mapped[Challenge] = relationship(back_populates="images")
    photographer: Mapped[Member] = relationship(back_populates="images")
    comments: Mapped[list[Comment]] = relationship(back_populates="image")

    __table_args__ = (Index("ix_images_challenge_score", "challenge_id", "average_all"),)

    def __repr__(self) -> str:
        return f"<Image {self.id} {self.name!r}>"


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id", ondelete="CASCADE"), index=True)
    commenter_id: Mapped[int] = mapped_column(
        ForeignKey("members.id", ondelete="CASCADE"), index=True
    )

    raw_comment: Mapped[str] = mapped_column(Text)
    """Comment HTML. Award markers are URLs, so matching needs the markup."""
    comment: Mapped[str] = mapped_column(Text)

    date: Mapped[datetime]
    edited: Mapped[datetime | None] = mapped_column(default=None)
    made_during_challenge: Mapped[bool] = mapped_column(default=False)

    image: Mapped[Image] = relationship(back_populates="comments")
    commenter: Mapped[Member] = relationship(back_populates="comments")
    grants: Mapped[list[AwardGrant]] = relationship(back_populates="comment")

    def __repr__(self) -> str:
        return f"<Comment {self.id} on image {self.image_id}>"


class Award(Base):
    """The *definition* of an award, loaded from ``config/awards.yaml``."""

    __tablename__ = "awards"

    id: Mapped[int] = mapped_column(primary_key=True)
    awarder_id: Mapped[int] = mapped_column(
        ForeignKey("members.id", ondelete="CASCADE"), index=True
    )

    name: Mapped[str] = mapped_column(String(128), index=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    image_src: Mapped[str] = mapped_column(String(512), default="")

    markers: Mapped[list[str]] = mapped_column(JSON, default=list)
    """Substrings that identify this award in a comment's HTML.

    Called ``regex`` in the old schema, which it never was -- matching has
    always been a plain substring test.
    """

    awarder: Mapped[Member] = relationship()
    grants: Mapped[list[AwardGrant]] = relationship(back_populates="award")

    __table_args__ = (UniqueConstraint("awarder_id", "name", name="uq_award_awarder_name"),)

    def __repr__(self) -> str:
        return f"<Award {self.slug!r}>"


class AwardGrant(Base):
    """One award, given once, in one comment."""

    __tablename__ = "award_grants"

    id: Mapped[int] = mapped_column(primary_key=True)
    award_id: Mapped[int] = mapped_column(ForeignKey("awards.id", ondelete="CASCADE"), index=True)
    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("members.id", ondelete="CASCADE"), index=True
    )
    comment_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), index=True, default=None
    )
    """The comment that granted it, or NULL for a derived award.

    Asigmatic is computed from vote variance rather than announced in a comment.
    The old code forced it into this column by minting a fake comment whose
    primary key was the *challenge* id, which collided with real comment ids."""
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id", ondelete="CASCADE"), index=True)
    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"), index=True
    )

    award: Mapped[Award] = relationship(back_populates="grants")
    recipient: Mapped[Member] = relationship()
    comment: Mapped[Comment | None] = relationship(back_populates="grants")
    image: Mapped[Image] = relationship()
    challenge: Mapped[Challenge] = relationship()

    __table_args__ = (
        # The real invariant: one award reaches a given image at most once.
        UniqueConstraint("award_id", "image_id", name="uq_grant_award_image"),
        UniqueConstraint("award_id", "comment_id", name="uq_grant_award_comment"),
    )

    def __repr__(self) -> str:
        return f"<AwardGrant award={self.award_id} comment={self.comment_id}>"


class ChallengeProbe(Base):
    """What the last look at a challenge id found.

    Replaces the old habit of caching error pages to disk forever. An ``invalid``
    id is settled and never refetched; an ``unfinished`` one is revisited,
    because it becomes a results page once voting closes.
    """

    __tablename__ = "challenge_probes"

    challenge_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    kind: Mapped[str] = mapped_column(String(16))
    checked_at: Mapped[datetime] = mapped_column(default=_utcnow)

    def __repr__(self) -> str:
        return f"<ChallengeProbe {self.challenge_id} {self.kind}>"
