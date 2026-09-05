from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from dpc.awards.catalog import AwardCatalog, AwarderDefinition

REPO_ROOT = Path(__file__).resolve().parents[2]


def _awarder(**overrides):
    base = {
        "name": "someone",
        "user_id": 1,
        "awards": [{"name": "Blue", "markers": ["bluepost"]}],
    }
    return {**base, **overrides}


class TestRealCatalog:
    """The catalogue that actually ships must stay valid."""

    def test_awards_yaml_loads_and_validates(self):
        catalog = AwardCatalog.load(REPO_ROOT / "awards.yaml")
        assert len(catalog.awarders) == 18
        assert len(catalog.pairs()) == 38

    def test_every_award_has_a_unique_slug(self):
        catalog = AwardCatalog.load(REPO_ROOT / "awards.yaml")
        slugs = [award.slug for _, award in catalog.pairs()]
        assert len(slugs) == len(set(slugs))

    def test_lookup_by_slug(self):
        catalog = AwardCatalog.load(REPO_ROOT / "awards.yaml")
        awarder, award = catalog.by_slug("posthumous-blue")
        assert awarder.name == "posthumous"
        assert "blackyak.com/dpc/bluepost" in award.markers

    def test_unknown_slug_raises(self):
        catalog = AwardCatalog.load(REPO_ROOT / "awards.yaml")
        with pytest.raises(KeyError):
            catalog.by_slug("no-such-award")


class TestValidation:
    def test_numeric_markers_become_strings(self):
        # YAML returns bare 1077284 as an int; matching is a string operation.
        awarder = AwarderDefinition.model_validate(
            _awarder(awards=[{"name": "Blue", "markers": [1077284, "bluepost"]}])
        )
        assert awarder.awards[0].markers == ("1077284", "bluepost")

    def test_an_award_needs_at_least_one_marker(self):
        with pytest.raises(ValidationError):
            AwarderDefinition.model_validate(_awarder(awards=[{"name": "Blue", "markers": []}]))

    def test_blank_markers_are_rejected(self):
        with pytest.raises(ValidationError, match="must not be blank"):
            AwarderDefinition.model_validate(_awarder(awards=[{"name": "Blue", "markers": ["  "]}]))

    def test_overlapping_markers_within_one_awarder_are_rejected(self):
        # vlado's MUAIMHO marker is the bare "Copyrighted_Image_Reuse_Prohibited_"
        # prefix, which matches every embedded image. That is only safe while
        # vlado has exactly one award; adding a second must fail loudly.
        with pytest.raises(ValidationError, match="both awards would match"):
            AwarderDefinition.model_validate(
                _awarder(
                    awards=[
                        {"name": "Broad", "markers": ["Copyrighted_Image_Reuse_Prohibited_"]},
                        {"name": "Narrow", "markers": ["Copyrighted_Image_Reuse_Prohibited_123"]},
                    ]
                )
            )

    def test_overlap_across_different_awarders_is_allowed(self):
        # Harmless: matching is scoped to the comment's author.
        catalog = AwardCatalog.model_validate(
            {
                "awarders": [
                    _awarder(name="a", user_id=1, awards=[{"name": "A", "markers": ["post"]}]),
                    _awarder(name="b", user_id=2, awards=[{"name": "B", "markers": ["bluepost"]}]),
                ]
            }
        )
        assert len(catalog.pairs()) == 2

    def test_duplicate_slugs_across_awarders_are_rejected(self):
        # Slugs become URLs; a collision silently merged two awards before.
        with pytest.raises(ValidationError, match="must be unique"):
            AwardCatalog.model_validate(
                {
                    "awarders": [
                        _awarder(name="a", user_id=1, awards=[{"name": "Blue", "markers": ["x"]}]),
                        _awarder(name="b", user_id=2, awards=[{"name": "blue", "markers": ["y"]}]),
                    ]
                }
            )

    def test_description_whitespace_is_normalised(self):
        awarder = AwarderDefinition.model_validate(
            _awarder(awards=[{"name": "Blue", "description": "a\n  b   c", "markers": ["x"]}])
        )
        assert awarder.awards[0].description == "a b c"
