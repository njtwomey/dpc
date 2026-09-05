"""The award catalogue, matching, and the derived Asigmatic award."""

from dpc.awards.asigmatic import ASIGMATIC_SLUG, grant_asigmatics, most_divisive, vote_spread
from dpc.awards.catalog import AwardCatalog, AwardDefinition, AwarderDefinition
from dpc.awards.match import awards_in, matches
from dpc.awards.service import SyncReport, find_grants, sync_catalog

__all__ = [
    "ASIGMATIC_SLUG",
    "AwardCatalog",
    "AwardDefinition",
    "AwarderDefinition",
    "SyncReport",
    "awards_in",
    "find_grants",
    "grant_asigmatics",
    "matches",
    "most_divisive",
    "sync_catalog",
    "vote_spread",
]
