"""The award catalogue and comment matching."""

from dpc.awards.catalog import AwardCatalog, AwardDefinition, AwarderDefinition
from dpc.awards.match import awards_in, matches, strip_quotes
from dpc.awards.service import SyncReport, find_grants, sync_catalog

__all__ = [
    "AwardCatalog",
    "AwardDefinition",
    "AwarderDefinition",
    "SyncReport",
    "awards_in",
    "find_grants",
    "matches",
    "strip_quotes",
    "sync_catalog",
]
