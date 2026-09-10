"""Consistency checks over the archive.

Three kinds of problem, deliberately kept apart:

*Integrity*
    The database contradicts itself -- an image pointing at a challenge that is
    not there. Should never happen; an error, and the only kind that fails.

*Incomplete*
    Data that is missing rather than wrong, and can be fetched. The old scraper
    swallowed image failures with a bare `print`, so a number of challenges hold
    only some of their images.

*Inherited*
    Artefacts the migration carried across faithfully. Real, but history rather
    than corruption.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session
from tqdm import tqdm

# Below this, a shared join date is a coincidence. Above it, every member
# "joined" on the day someone ran the scraper: the old code stamped cancelled
# members with arrow.now().date() instead of leaving the date unknown.
FABRICATED_DATE_THRESHOLD = 50


@dataclass
class Finding:
    name: str
    count: int
    detail: str

    def __str__(self) -> str:
        return f"{self.name}: {self.count:,} -- {self.detail}"


@dataclass
class Health:
    integrity: list[Finding] = field(default_factory=list)
    incomplete: list[Finding] = field(default_factory=list)
    inherited: list[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when nothing contradicts itself.

        Missing data and inherited artefacts are reported but do not fail: they
        are things to go and fetch, not signs that the archive is broken.
        """
        return not self.integrity


_INTEGRITY: tuple[tuple[str, str, str], ...] = (
    (
        "images without a challenge",
        "SELECT COUNT(*) FROM images i "
        "LEFT JOIN challenges c ON c.id = i.challenge_id WHERE c.id IS NULL",
        "an image whose challenge is missing",
    ),
    (
        "images without a photographer",
        "SELECT COUNT(*) FROM images i "
        "LEFT JOIN members m ON m.id = i.photographer_id WHERE m.id IS NULL",
        "an image whose photographer is missing",
    ),
    (
        "comments without an image",
        "SELECT COUNT(*) FROM comments c "
        "LEFT JOIN images i ON i.id = c.image_id WHERE i.id IS NULL",
        "a comment on an image that is missing",
    ),
    (
        "comments without a commenter",
        "SELECT COUNT(*) FROM comments c "
        "LEFT JOIN members m ON m.id = c.commenter_id WHERE m.id IS NULL",
        "a comment by a member who is missing",
    ),
    (
        "grants without an image",
        "SELECT COUNT(*) FROM award_grants g "
        "LEFT JOIN images i ON i.id = g.image_id WHERE i.id IS NULL",
        "an award on an image that is missing",
    ),
    (
        "grants without a recipient",
        "SELECT COUNT(*) FROM award_grants g "
        "LEFT JOIN members m ON m.id = g.recipient_id WHERE m.id IS NULL",
        "an award to a member who is missing",
    ),
)

# A challenge is short only when it holds *fewer* images than it had
# submissions. Holding more is normal: the results page also lists disqualified
# entries, which num_submissions excludes -- so a challenge with two DQs stores
# num_submissions + 2. Counting those as gaps flagged 194 healthy challenges.
# Zero stored means it has not been crawled at all, which is not a gap either.
INCOMPLETE_CHALLENGES = (
    "SELECT COUNT(*) FROM challenges c WHERE c.num_submissions > 0 AND "
    "(SELECT COUNT(*) FROM images i WHERE i.challenge_id = c.id) "
    "BETWEEN 1 AND c.num_submissions - 1"
)


def check(session: Session, catalogue_slugs: Iterable[str] = ()) -> Health:
    """Run every check. Cheap enough to run after any scrape.

    ``catalogue_slugs`` enables the orphaned-award check; omit it and that one
    is skipped rather than reporting every award as an orphan.
    """
    health = Health()
    catalogue_slugs = list(catalogue_slugs)

    bar = tqdm(_INTEGRITY, desc="checking", unit="check", leave=False, disable=None)
    for name, sql, detail in bar:
        bar.set_postfix_str(name)
        count = int(session.execute(text(sql)).scalar_one())
        if count:
            health.integrity.append(Finding(name, count, detail))

    violations = len(session.execute(text("PRAGMA foreign_key_check")).fetchall())
    if violations:
        health.integrity.append(
            Finding("foreign key violations", violations, "reported by SQLite itself")
        )

    # Renaming an award changes its slug, and sync_catalog adds the new one
    # without removing the old: the grants are then duplicated under both, and
    # the site shows an image winning two awards that are the same award. This
    # happened once, to chromeydome's Post Lumy, and cost 758 duplicate grants.
    if catalogue_slugs:
        orphans = session.execute(
            text(
                "SELECT a.slug, COUNT(g.id) FROM awards a "
                "LEFT JOIN award_grants g ON g.award_id = a.id "
                "WHERE a.slug NOT IN :slugs GROUP BY a.id ORDER BY a.slug"
            ).bindparams(bindparam("slugs", expanding=True)),
            {"slugs": catalogue_slugs},
        ).all()
        for slug, count in orphans:
            # Only an orphan holding grants is a contradiction: those grants
            # duplicate whatever replaced it, and the site shows one image
            # winning the same award twice. An orphan with none is just clutter
            # left by an edit, so it reports without failing the run.
            finding = Finding(
                f"award not in the catalogue: {slug}",
                count,
                "left by a rename; its grants duplicate the replacement"
                if count
                else "in the database but not config/awards.yaml, and never granted",
            )
            (health.integrity if count else health.inherited).append(finding)

    partial = int(session.execute(text(INCOMPLETE_CHALLENGES)).scalar_one())
    if partial:
        health.incomplete.append(
            Finding(
                "challenges missing images",
                partial,
                "some but not all images stored; `dpc scrape --incomplete` refetches them",
            )
        )

    # A cancelled account legitimately hides its name, so only an unexplained
    # blank is worth reporting -- and refreshing turns the former into the latter.
    blank = int(
        session.execute(
            text("SELECT COUNT(*) FROM members WHERE (name = '' OR name IS NULL) AND cancelled = 0")
        ).scalar_one()
    )
    if blank:
        health.inherited.append(
            Finding(
                "members with no name",
                blank,
                "profile unreadable and not known cancelled; `dpc refresh-members` refetches them",
            )
        )

    fabricated = int(
        session.execute(
            text(
                "SELECT COALESCE(SUM(n), 0) FROM ("
                "  SELECT COUNT(*) AS n FROM members WHERE join_date IS NOT NULL"
                "  GROUP BY join_date HAVING COUNT(*) >= :threshold)"
            ),
            {"threshold": FABRICATED_DATE_THRESHOLD},
        ).scalar_one()
    )
    if fabricated:
        health.inherited.append(
            Finding(
                "members with a fabricated join date",
                fabricated,
                f"{FABRICATED_DATE_THRESHOLD}+ share one date: the old scraper stamped "
                "cancelled members with the day it ran",
            )
        )

    return health
