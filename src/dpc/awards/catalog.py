"""The award catalogue: who gives what, and how a comment is recognised.

Loaded from ``awards.yaml``. The old ``meta.yaml`` was read with
``yaml.safe_load`` and used unchecked, so a typo surfaced much later as a
missing award rather than as an error at load time.
"""

from __future__ import annotations

from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
from slugify import slugify


class AwardDefinition(BaseModel):
    """One award a member gives out."""

    model_config = {"frozen": True}

    name: str
    description: str = ""
    image: str = ""
    markers: tuple[str, ...] = Field(min_length=1)
    """Substrings identifying this award in a comment's HTML.

    Called ``urls`` and typed ``regex`` in the old schema; it has always been a
    plain substring test against the comment markup.
    """

    @field_validator("markers", mode="before")
    @classmethod
    def _coerce_markers(cls, value: object) -> object:
        # The old file mixed quoted and unquoted numeric ids, so YAML handed
        # back a mix of str and int.
        if isinstance(value, list):
            return tuple(str(item).strip() for item in value)
        return value

    @field_validator("markers")
    @classmethod
    def _reject_blank_markers(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not marker for marker in value):
            msg = "markers must not be blank"
            raise ValueError(msg)
        return value

    @field_validator("name", "description")
    @classmethod
    def _tidy(cls, value: str) -> str:
        return " ".join(value.split())

    @property
    def slug(self) -> str:
        return slugify(self.name)


class AwarderDefinition(BaseModel):
    """A member and the awards they give."""

    model_config = {"frozen": True}

    name: str
    user_id: int
    thumb: str | None = None
    awards: tuple[AwardDefinition, ...] = Field(min_length=1)

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @model_validator(mode="after")
    def _reject_overlapping_markers(self) -> Self:
        """Reject markers that would award two of this member's awards at once.

        Overlap only matters within a single awarder, because matching is scoped
        to the comment's author. A broad marker like
        ``Copyrighted_Image_Reuse_Prohibited_`` matches every embedded image and
        is only safe while its owner has exactly one award -- which is a property
        worth failing on rather than rediscovering.
        """
        flat = [(award.name, marker) for award in self.awards for marker in award.markers]
        for name_a, marker_a in flat:
            for name_b, marker_b in flat:
                if name_a != name_b and marker_a != marker_b and marker_a in marker_b:
                    msg = (
                        f"{self.name}: marker {marker_a!r} of {name_a!r} is contained in "
                        f"marker {marker_b!r} of {name_b!r}; both awards would match"
                    )
                    raise ValueError(msg)
        return self


class AwardCatalog(BaseModel):
    """Every awarder and award, validated as a whole."""

    model_config = {"frozen": True}

    awarders: tuple[AwarderDefinition, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _reject_duplicate_slugs(self) -> Self:
        seen: dict[str, str] = {}
        for awarder in self.awarders:
            for award in awarder.awards:
                if award.slug in seen:
                    msg = (
                        f"award slug {award.slug!r} is used by both {seen[award.slug]!r} "
                        f"and {awarder.name!r}; slugs become URLs and must be unique"
                    )
                    raise ValueError(msg)
                seen[award.slug] = awarder.name
        return self

    @classmethod
    def load(cls, path: Path) -> AwardCatalog:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls.model_validate({"awarders": raw} if isinstance(raw, list) else raw)

    def pairs(self) -> list[tuple[AwarderDefinition, AwardDefinition]]:
        return [(awarder, award) for awarder in self.awarders for award in awarder.awards]

    def by_slug(self, slug: str) -> tuple[AwarderDefinition, AwardDefinition]:
        for awarder, award in self.pairs():
            if award.slug == slug:
                return awarder, award
        msg = f"no award with slug {slug!r}"
        raise KeyError(msg)
