"""Turn the database into the site dataset.

Assembled with a handful of bulk queries and in-memory grouping. The old builder
issued a fresh query per award, per challenge and per user -- several thousand
round trips per run.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from slugify import slugify
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from dpc.awards.catalog import AwardCatalog
from dpc.db.models import Award, AwardGrant, Challenge, Comment, Image, Member
from dpc.export.model import (
    AwarderOut,
    AwardOut,
    ChallengeOut,
    Count,
    ImageOut,
    Meta,
    RecipientOut,
    SiteData,
)
from dpc.export.urls import member_thumb_url


def build_site_data(session: Session, catalog: AwardCatalog) -> SiteData:
    awards = {a.id: a for a in session.scalars(select(Award))}
    members = {m.id: m for m in session.scalars(select(Member))}
    challenges = {c.id: c for c in session.scalars(select(Challenge))}

    # An OUTER join, because AwardGrant.comment_id is nullable: an inner join
    # would silently drop any grant without one instead of failing. Such a grant
    # is dated by its challenge's voting_end.
    grants = list(
        session.scalars(
            select(AwardGrant)
            .outerjoin(Comment, AwardGrant.comment_id == Comment.id)
            .join(Challenge, AwardGrant.challenge_id == Challenge.id)
            .order_by(
                func.coalesce(Comment.date, Challenge.voting_end).desc(),
                AwardGrant.id.desc(),
            )
        )
    )

    image_ids = {grant.image_id for grant in grants}
    images = {i.id: i for i in session.scalars(select(Image).where(Image.id.in_(image_ids)))}

    by_award: dict[int, list[AwardGrant]] = defaultdict(list)
    by_challenge: dict[int, list[AwardGrant]] = defaultdict(list)
    by_recipient: dict[int, list[AwardGrant]] = defaultdict(list)
    by_image: dict[int, list[AwardGrant]] = defaultdict(list)
    for grant in grants:
        by_award[grant.award_id].append(grant)
        by_challenge[grant.challenge_id].append(grant)
        by_recipient[grant.recipient_id].append(grant)
        by_image[grant.image_id].append(grant)

    catalogue_order = {award.slug: index for index, (_, award) in enumerate(catalog.pairs())}

    def slug_of(award_id: int) -> str:
        return awards[award_id].slug

    def sorted_slugs(items: list[AwardGrant]) -> list[str]:
        return sorted({slug_of(g.award_id) for g in items}, key=lambda s: catalogue_order.get(s, 0))

    def counts(items: list[AwardGrant]) -> list[Count]:
        tally = Counter(slug_of(g.award_id) for g in items)
        # Most common first, ties broken by slug so the output is stable.
        ordered = sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))
        return [Count(slug=slug, count=count) for slug, count in ordered]

    def ordered_image_ids(items: list[AwardGrant]) -> list[int]:
        seen: dict[int, None] = {}
        for grant in items:
            seen.setdefault(grant.image_id, None)
        return list(seen)

    awards_out = [
        AwardOut(
            slug=award.slug,
            name=award.name,
            description=award.description,
            thumb=award.image_src,
            awarder_id=award.awarder_id,
            awarder_slug=slugify(members[award.awarder_id].name),
            awarder_name=members[award.awarder_id].name,
            num_granted=len(by_award[award.id]),
            num_recipients=len({g.recipient_id for g in by_award[award.id]}),
            num_challenges=len({g.challenge_id for g in by_award[award.id]}),
            image_ids=ordered_image_ids(by_award[award.id]),
        )
        for award in sorted(awards.values(), key=lambda a: a.slug)
    ]

    grants_by_awarder: dict[int, list[AwardGrant]] = defaultdict(list)
    for award in awards.values():
        grants_by_awarder[award.awarder_id].extend(by_award[award.id])

    awarders_out = [
        AwarderOut(
            id=member_id,
            name=members[member_id].name,
            slug=slugify(members[member_id].name),
            thumb=member_thumb_url(member_id),
            num_granted=len(items),
            award_slugs=sorted(
                (a.slug for a in awards.values() if a.awarder_id == member_id),
                key=lambda s: catalogue_order.get(s, 0),
            ),
        )
        for member_id, items in sorted(
            grants_by_awarder.items(), key=lambda kv: slugify(members[kv[0]].name)
        )
    ]

    challenges_out = [
        ChallengeOut(
            id=challenge_id,
            name=challenges[challenge_id].name,
            slug=slugify(challenges[challenge_id].name),
            num_granted=len(items),
            award_counts=counts(items),
            image_ids=ordered_image_ids(items),
        )
        for challenge_id, items in sorted(
            by_challenge.items(),
            key=lambda kv: (challenges[kv[0]].voting_end, kv[0]),
            reverse=True,
        )
    ]

    recipients_out = [
        RecipientOut(
            id=member_id,
            name=members[member_id].name,
            slug=slugify(members[member_id].name),
            num_granted=len(items),
            num_awards=len({g.award_id for g in items}),
            num_challenges=len({g.challenge_id for g in items}),
            award_counts=counts(items),
            image_ids=ordered_image_ids(items),
        )
        for member_id, items in sorted(
            by_recipient.items(),
            key=lambda kv: (-len(kv[1]), slugify(members[kv[0]].name)),
        )
        # A member with no name renders an empty card and an empty URL. The old
        # builder skipped these silently; they are still skipped, but here it is
        # visible and testable.
        if members[member_id].name.strip()
    ]

    images_out = {
        str(image_id): ImageOut(
            id=image_id,
            title=images[image_id].name,
            challenge_id=images[image_id].challenge_id,
            challenge_name=challenges[images[image_id].challenge_id].name,
            challenge_slug=slugify(challenges[images[image_id].challenge_id].name),
            photographer_id=images[image_id].photographer_id,
            photographer_name=members[images[image_id].photographer_id].name,
            photographer_slug=slugify(members[images[image_id].photographer_id].name),
            awards=sorted_slugs(by_image[image_id]),
        )
        for image_id in sorted(by_image)
        if image_id in images
    }

    return SiteData(
        meta=Meta(
            num_awarders=len(awarders_out),
            num_awards=len(awards_out),
            num_challenges=len(challenges_out),
            num_recipients=len(recipients_out),
            num_images=len(images_out),
            num_grants=len(grants),
        ),
        awarders=awarders_out,
        awards=awards_out,
        challenges=challenges_out,
        recipients=recipients_out,
        images=images_out,
    )
