"""Write the site dataset as deterministic JSON.

One record per line, each record itself minified. That is within a few hundred
bytes of fully minified once git has compressed it, while keeping ``git diff
site/data/dpc`` readable: a changed challenge shows up as one changed line
rather than the whole file becoming a single altered blob.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from tqdm import tqdm

from dpc.export.model import SiteData

FILENAMES = ("meta", "awarders", "awards", "challenges", "recipients", "images")

_COMPACT = (",", ":")


def write_site_data(data: SiteData, destination: Path) -> list[Path]:
    """Write one JSON file per collection. Returns the paths written.

    Sorted keys and stable ordering throughout, so re-exporting an unchanged
    database produces an empty ``git diff``.
    """
    destination.mkdir(parents=True, exist_ok=True)

    payloads: dict[str, Any] = {
        "meta": data.meta,
        "awarders": data.awarders,
        "awards": data.awards,
        "challenges": data.challenges,
        "recipients": data.recipients,
        "images": data.images,
    }

    written: list[Path] = []
    for name in tqdm(FILENAMES, desc="writing", unit="file", leave=False, disable=None):
        path = destination / f"{name}.json"
        path.write_text(_dumps(payloads[name]), encoding="utf-8")
        written.append(path)
    return written


def _record(value: Any) -> str:
    return json.dumps(value, separators=_COMPACT, sort_keys=True, ensure_ascii=False)


def _dumps(payload: Any) -> str:
    if isinstance(payload, BaseModel):
        return _record(payload.model_dump()) + "\n"

    if isinstance(payload, list):
        if not payload:
            return "[]\n"
        body = ",\n".join(_record(item.model_dump()) for item in payload)
        return f"[\n{body}\n]\n"

    if isinstance(payload, dict):
        if not payload:
            return "{}\n"
        body = ",\n".join(
            f"{json.dumps(key)}:{_record(value.model_dump())}"
            for key, value in sorted(payload.items())
        )
        return f"{{\n{body}\n}}\n"

    msg = f"cannot serialise {type(payload).__name__}"
    raise TypeError(msg)
