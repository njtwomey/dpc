"""On-disk cache of fetched HTML.

Always stored as UTF-8, whatever the origin sent, so a cached page and a fresh
one parse identically.

The old cache wrote whatever came back, including error pages, and every later
run read the error back from disk. That is how a challenge that happened to be
mid-voting when it was first seen could never be picked up again.
"""

from __future__ import annotations

from pathlib import Path


class HtmlCache:
    def __init__(self, root: Path) -> None:
        self.root = root

    def path_for(self, kind: str, key: int | str) -> Path:
        return self.root / kind / f"{key}.html"

    def read(self, kind: str, key: int | str) -> str | None:
        path = self.path_for(kind, key)
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8")

    def write(self, kind: str, key: int | str, html: str) -> Path:
        path = self.path_for(kind, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        return path

    def has(self, kind: str, key: int | str) -> bool:
        return self.path_for(kind, key).is_file()
