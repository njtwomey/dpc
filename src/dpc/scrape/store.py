"""Persisting parsed records. The only place parse results meet the database."""

from __future__ import annotations

from sqlalchemy.orm import Session

from dpc.db.models import Challenge, ChallengeProbe, Comment, Image, Member
from dpc.parse.types import ChallengeRecord, CommentRecord, ImageRecord, MemberRecord


def upsert_member(session: Session, record: MemberRecord) -> Member:
    member = session.get(Member, record.id)
    if member is None:
        # name is NOT NULL, and the guard below deliberately skips blank names.
        # Without a default that combination leaves the column unset on insert.
        member = Member(id=record.id, name="")
        session.add(member)

    # A cancelled profile hides the name, so never overwrite a known one with a
    # blank; and never overwrite a real join date with None.
    if record.name:
        member.name = record.name
    if record.join_date is not None:
        member.join_date = record.join_date
    member.cancelled = record.cancelled
    session.flush()
    return member


def upsert_challenge(session: Session, record: ChallengeRecord) -> Challenge:
    challenge = session.get(Challenge, record.id)
    if challenge is None:
        challenge = Challenge(id=record.id)
        session.add(challenge)

    challenge.name = record.name
    challenge.description = record.description
    challenge.submission_start = record.submission_start
    challenge.submission_end = record.submission_end
    challenge.voting_start = record.voting_start
    challenge.voting_end = record.voting_end
    challenge.num_submissions = record.num_submissions
    challenge.num_disqualifications = record.num_disqualifications
    challenge.num_votes = record.num_votes
    challenge.num_comments = record.num_comments
    challenge.average_score = record.average_score
    challenge.highest_score = record.highest_score
    challenge.median_score = record.median_score
    challenge.lowest_score = record.lowest_score
    session.flush()
    return challenge


def upsert_image(session: Session, record: ImageRecord) -> Image:
    image = session.get(Image, record.id)
    if image is None:
        image = Image(id=record.id)
        session.add(image)

    image.challenge_id = record.challenge_id
    image.photographer_id = record.photographer_id
    image.name = record.name
    image.votes = list(record.stats.votes)
    image.disqualified = record.stats.disqualified
    image.position = record.stats.position
    image.average_all = record.stats.average_all
    image.average_commenters = record.stats.average_commenters
    image.average_participants = record.stats.average_participants
    image.average_non_participants = record.stats.average_non_participants
    image.num_views = record.stats.num_views
    image.num_votes = record.stats.num_votes
    session.flush()
    return image


def upsert_comments(session: Session, records: list[CommentRecord]) -> int:
    """Insert comments that are not already stored. Returns how many were new."""
    if not records:
        return 0

    known = set(
        session.scalars(
            Comment.__table__.select()
            .with_only_columns(Comment.id)
            .where(Comment.id.in_([r.id for r in records]))
        )
    )

    created = 0
    for record in records:
        if record.id in known:
            continue
        session.add(
            Comment(
                id=record.id,
                image_id=record.image_id,
                commenter_id=record.commenter_id,
                raw_comment=record.raw_comment,
                comment=record.comment,
                date=record.date,
                edited=record.edited,
                made_during_challenge=record.made_during_challenge,
            )
        )
        created += 1

    session.flush()
    return created


def record_probe(session: Session, challenge_id: int, kind: str) -> None:
    """Remember what a challenge id turned out to be."""
    probe = session.get(ChallengeProbe, challenge_id)
    if probe is None:
        probe = ChallengeProbe(challenge_id=challenge_id, kind=kind)
        session.add(probe)
    else:
        probe.kind = kind
    session.flush()
