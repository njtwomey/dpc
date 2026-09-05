"""The shape of the exported site dataset.

This is the contract between the local pipeline and the Hugo build. It stores
ids, not URLs: every dpchallenge asset URL is derivable from an id, and spelling
them out multiplied the old export to 38 MB of near-duplicate YAML.
"""

from __future__ import annotations

from pydantic import BaseModel

SCHEMA_VERSION = 1


class Count(BaseModel):
    """A per-award tally, ordered most-frequent first."""

    slug: str
    count: int


class ImageOut(BaseModel):
    id: int
    title: str
    challenge_id: int
    photographer_id: int
    awards: list[str]
    """Award slugs granted to this image, in catalogue order."""


class AwardOut(BaseModel):
    slug: str
    name: str
    description: str
    thumb: str
    awarder_id: int
    awarder_slug: str
    awarder_name: str
    num_granted: int
    num_recipients: int
    num_challenges: int
    image_ids: list[int]
    """Most recently awarded first."""


class AwarderOut(BaseModel):
    id: int
    name: str
    slug: str
    thumb: str | None
    num_granted: int
    award_slugs: list[str]


class ChallengeOut(BaseModel):
    id: int
    name: str
    slug: str
    num_granted: int
    award_counts: list[Count]
    image_ids: list[int]


class RecipientOut(BaseModel):
    id: int
    name: str
    slug: str
    num_granted: int
    num_awards: int
    num_challenges: int
    award_counts: list[Count]
    image_ids: list[int]


class Meta(BaseModel):
    schema_version: int = SCHEMA_VERSION
    num_awarders: int
    num_awards: int
    num_challenges: int
    num_recipients: int
    num_images: int
    num_grants: int
    # Deliberately no generated_at: an unchanged database must export
    # byte-identical files, so a diff means the data really changed.


class SiteData(BaseModel):
    meta: Meta
    awarders: list[AwarderOut]
    awards: list[AwardOut]
    challenges: list[ChallengeOut]
    recipients: list[RecipientOut]
    images: dict[str, ImageOut]
