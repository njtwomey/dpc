"""The Asigmatic award: highest vote variance in a challenge.

Derived rather than announced, so it carries no comment. The old implementation
manufactured a ``Comment`` whose primary key was the *challenge* id in order to
satisfy a NOT NULL foreign key -- silently colliding with real comment ids.
"""

from __future__ import annotations

from loguru import logger

from statistics import pstdev

from sqlalchemy import select
from sqlalchemy.orm import Session

from dpc.db.models import Award, AwardGrant, Image

ASIGMATIC_SLUG = "asigmatic"


def vote_spread(votes: list[int]) -> float:
    """Population standard deviation of a ten-bucket score histogram.

    ``votes[i]`` is how many voters gave a score of ``i + 1``.
    """
    expanded = [score for score, count in enumerate(votes, start=1) for _ in range(count)]
    if len(expanded) < 2:
        return 0.0
    return pstdev(expanded)


def most_divisive(session: Session, challenge_id: int) -> Image | None:
    """The eligible image with the widest vote spread, or None.

    Disqualified images and images with no votes are not eligible. Ties break on
    the lowest image id so the result is stable across runs.
    """
    candidates = [
        image
        for image in session.scalars(
            select(Image).where(Image.challenge_id == challenge_id).order_by(Image.id)
        )
        if not image.disqualified and image.votes and sum(image.votes) > 0
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda image: (vote_spread(image.votes), -image.id))


def grant_asigmatics(session: Session) -> int:
    """Award Asigmatic once per challenge. Returns the number of new grants."""
    award = session.scalars(select(Award).where(Award.slug == ASIGMATIC_SLUG)).one_or_none()
    if award is None:
        logger.warning("no {!r} award in the catalogue; skipping", ASIGMATIC_SLUG)
        return 0

    already = set(
        session.scalars(select(AwardGrant.challenge_id).where(AwardGrant.award_id == award.id))
    )
    challenge_ids = sorted(set(session.scalars(select(Image.challenge_id))) - already)

    created = 0
    for challenge_id in challenge_ids:
        image = most_divisive(session, challenge_id)
        if image is None:
            continue
        session.add(
            AwardGrant(
                award_id=award.id,
                recipient_id=image.photographer_id,
                comment_id=None,
                image_id=image.id,
                challenge_id=challenge_id,
            )
        )
        created += 1

    session.flush()
    return created
