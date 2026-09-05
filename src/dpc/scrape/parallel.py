"""Parsing fetched pages, optionally across processes.

Fetching and parsing want different kinds of concurrency: fetching is I/O-bound
and wants threads, parsing is CPU-bound (~14 ms/page) and wants processes.
Separating the two is what lets each use the right one.

The parse functions are pure and their results are plain dataclasses, so they
cross a process boundary without ceremony.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

from dpc.parse.image import ImageStatsUnavailableError, parse_comments, parse_image
from dpc.parse.types import CommentRecord, ImageRecord


@dataclass(frozen=True, slots=True)
class ParsedImage:
    image: ImageRecord
    comments: list[CommentRecord]


@dataclass(frozen=True, slots=True)
class FailedImage:
    image_id: int
    error: str
    unavailable_stats: bool
    """True when the statistics panel was missing, which means the page shape
    changed rather than this one image being odd -- the caller stops on it."""


def parse_one(html: str, image_id: int, challenge_id: int) -> ParsedImage | FailedImage:
    """Parse one image page. Never raises, so a pool never dies mid-map."""
    try:
        return ParsedImage(
            image=parse_image(html, image_id, challenge_id),
            comments=parse_comments(html, image_id),
        )
    except ImageStatsUnavailableError as error:
        return FailedImage(image_id, str(error), unavailable_stats=True)
    except Exception as error:
        return FailedImage(image_id, f"{type(error).__name__}: {error}", unavailable_stats=False)


def _parse_star(args: tuple[str, int, int]) -> ParsedImage | FailedImage:
    return parse_one(*args)


def parse_images(
    pages: list[tuple[str, int, int]], *, workers: int = 0
) -> list[ParsedImage | FailedImage]:
    """Parse ``(html, image_id, challenge_id)`` triples, in order.

    ``workers`` of 0 or 1 parses in-process, which is the right choice unless
    fetching has been made fast enough that parsing dominates.
    """
    if not pages:
        return []
    if workers <= 1:
        return [parse_one(*page) for page in pages]

    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_parse_star, pages, chunksize=8))
