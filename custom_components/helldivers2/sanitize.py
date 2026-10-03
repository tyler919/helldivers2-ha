"""Text sanitising for upstream API strings (kept free of HA imports so it can be unit tested)."""
from __future__ import annotations

import re

# Well-formed tags such as the game's <i=1>...</i> dispatch markup.
_TAG_RE = re.compile(r"<[^<>]*>")


def strip_markup(text: str | None) -> str:
    """Drop tag markup, then remove any '<' or '>' that is left.

    The second step is what makes this safe: an unclosed tag like
    '<img src=x onerror=...' survives the tag regex, but loses its '<'.
    """
    if not text:
        return ""
    text = _TAG_RE.sub("", str(text))
    return text.replace("<", "").replace(">", "")
