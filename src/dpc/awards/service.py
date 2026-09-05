"""Applying the catalogue to the database."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from dpc.awards.catalog import AwardCatalog, AwardDefinition, AwarderDefinition
from dpc.awards.match import awards_in
from dpc.db.models import Award, AwardGrant, Comment, Image, Member


@dataclass(frozen=True, slots=True)
class SyncReport:
    created: int
    updated: int
    unchanged: int


def sync_catalog(session: Session, catalog: AwardCatalog) -> SyncReport:
    """Upsert :class:`Award` rows from the catalogue.

    The old builder called ``award.update(**kwargs)`` on a peewee *instance*,
    which constructs a query object and discards it. Every edit made to the
    award metadata silently failed to persist, and a bare ``except:`` on the
    next line hid it.
    """
    existing = {a.slug: a for a in session.scalars(select(Award))}
    created = updated = unchanged = 0

    for awarder, definition in catalog.pairs():
        _ensure_member(session, awarder.user_id, awarder.name)

        fields = {
            "awarder_id": awarder.user_id,
            "name": definition.name,
            "description": definition.description,
            "image_src": definition.image,
            "markers": list(definition.markers),
        }

        award = existing.get(definition.slug)
        if award is None:
            session.add(Award(slug=definition.slug, **fields))
            created += 1
            continue

        changes = {k: v for k, v in fields.items() if getattr(award, k) != v}
        if changes:
            for key, value in changes.items():
                setattr(award, key, value)
            logger.info("award {}: updated {}", definition.slug, ", ".join(sorted(changes)))
            updated += 1
        else:
            unchanged += 1

    session.flush()
    return SyncReport(created=created, updated=updated, unchanged=unchanged)


def find_grants(session: Session, catalog: AwardCatalog) -> int:
    """Scan each awarder's comments for their award markers.

    Returns the number of new grants created. Idempotent: a second run over an
    unchanged database creates nothing.
    """
    awards_by_slug = {a.slug: a for a in session.scalars(select(Award))}
    granted = {
        (award_id, image_id)
        for award_id, image_id in session.execute(select(AwardGrant.award_id, AwardGrant.image_id))
    }

    created = 0
    for awarder, _ in _grouped_by_awarder(catalog):
        definitions = [d for a, d in catalog.pairs() if a.user_id == awarder.user_id]
        rows = session.execute(
            select(Comment, Image)
            .join(Image, Comment.image_id == Image.id)
            .where(Comment.commenter_id == awarder.user_id)
            .order_by(Comment.date, Comment.id)
        ).all()

        for comment, image in rows:
            for definition in awards_in(comment.raw_comment, definitions):
                award = awards_by_slug[definition.slug]
                key = (award.id, image.id)
                if key in granted:
                    continue
                granted.add(key)
                session.add(
                    AwardGrant(
                        award_id=award.id,
                        recipient_id=image.photographer_id,
                        comment_id=comment.id,
                        image_id=image.id,
                        challenge_id=image.challenge_id,
                    )
                )
                created += 1

    session.flush()
    return created


def _grouped_by_awarder(
    catalog: AwardCatalog,
) -> Iterator[tuple[AwarderDefinition, AwardDefinition]]:
    """One entry per distinct awarder, so their comments are scanned once."""
    seen: set[int] = set()
    for awarder, award in catalog.pairs():
        if awarder.user_id not in seen:
            seen.add(awarder.user_id)
            yield awarder, award


def _ensure_member(session: Session, member_id: int, name: str) -> Member:
    member = session.get(Member, member_id)
    if member is None:
        member = Member(id=member_id, name=name, join_date=None)
        session.add(member)
        session.flush()
    return member
