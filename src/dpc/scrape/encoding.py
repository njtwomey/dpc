"""Turn dpchallenge's response bytes into correct text.

dpchallenge serves pages with the charset meta tag commented out, so nothing
declares an encoding and every consumer has to guess. The pages are actually
windows-1252. Guessing latin-1 or utf-8-with-replacement is what put
``Hidden Gem VI \\x97 Mid-Term Quiz`` into the published site: 0x97 is an em dash
in windows-1252 and an unassigned control character in latin-1.
"""

from __future__ import annotations

FALLBACK_ENCODING = "cp1252"


def decode_html(raw: bytes, declared: str | None = None) -> str:
    """Decode response bytes to text.

    Tries, in order: the encoding the server declared (when it declared one and
    it is not the useless ``ISO-8859-1`` default), then strict UTF-8, then
    windows-1252. Strict UTF-8 first is safe because genuinely UTF-8 pages
    decode cleanly while windows-1252 pages carrying bytes like 0x97 raise, and
    fall through to the codec that reads them correctly.
    """
    if declared and declared.lower() not in {"iso-8859-1", "latin-1", "latin1"}:
        try:
            return raw.decode(declared)
        except (UnicodeDecodeError, LookupError):
            pass

    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode(FALLBACK_ENCODING, errors="replace")
