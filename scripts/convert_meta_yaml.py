"""One-shot: turn the legacy ``meta.yaml`` into ``awards.yaml``.

Renames the misleading ``urls`` key to ``markers`` and normalises the numeric
image ids that YAML had been handing back as ints. Run once; then delete
``meta.yaml``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from dpc.awards.catalog import AwardCatalog


def convert(source: Path, destination: Path) -> AwardCatalog:
    legacy = yaml.safe_load(source.read_text(encoding="utf-8"))

    awarders = [
        {
            "name": awarder["name"],
            "user_id": awarder["user_id"],
            **({"thumb": awarder["thumb"]} if awarder.get("thumb") else {}),
            "awards": [
                {
                    "name": award["name"],
                    "description": " ".join(award.get("description", "").split()),
                    "image": award.get("image", ""),
                    "markers": [str(marker) for marker in award["urls"]],
                }
                for award in awarder["awards"]
            ],
        }
        for awarder in legacy
    ]

    catalog = AwardCatalog.model_validate({"awarders": awarders})

    destination.write_text(
        yaml.safe_dump(
            {"awarders": awarders},
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            width=100,
        ),
        encoding="utf-8",
    )
    return catalog


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    catalog = convert(root / "meta.yaml", root / "awards.yaml")
    print(f"wrote awards.yaml: {len(catalog.awarders)} awarders, {len(catalog.pairs())} awards")
    return 0


if __name__ == "__main__":
    sys.exit(main())
