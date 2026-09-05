"""Write the site dataset as deterministic JSON."""

from __future__ import annotations

import json
from pathlib import Path

from dpc.export.model import SiteData

FILENAMES = ("meta", "awarders", "awards", "challenges", "recipients", "images")


def write_site_data(data: SiteData, destination: Path) -> list[Path]:
    """Write one JSON file per collection. Returns the paths written.

    Sorted keys and a trailing newline, so re-exporting an unchanged database
    produces an empty ``git diff``.
    """
    destination.mkdir(parents=True, exist_ok=True)

    payloads = {
        "meta": data.meta,
        "awarders": data.awarders,
        "awards": data.awards,
        "challenges": data.challenges,
        "recipients": data.recipients,
        "images": data.images,
    }

    written: list[Path] = []
    for name in FILENAMES:
        path = destination / f"{name}.json"
        path.write_text(_dumps(payloads[name]), encoding="utf-8")
        written.append(path)
    return written


def _dumps(payload: object) -> str:
    plain = payload.model_dump() if hasattr(payload, "model_dump") else _dump_container(payload)
    return json.dumps(plain, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _dump_container(payload: object) -> object:
    if isinstance(payload, list):
        return [item.model_dump() for item in payload]
    if isinstance(payload, dict):
        return {key: value.model_dump() for key, value in payload.items()}
    msg = f"cannot serialise {type(payload).__name__}"
    raise TypeError(msg)
