"""Protect text that must not be translated (code, URLs, paths).

Policy lives in `protect()`. Edit the patterns there to change what is kept.
"""

import re

# Placeholder format, such as [[X0]]. Plain ASCII so the translation model copies it as is.
# The letter changes when the text already contains a placeholder-shaped string, so the two cannot collide.
PH_FMT = "[[{}{}]]"
PH_RE = re.compile(r"\[\[[A-Z]\d+\]\]")
_MARKERS = "XQZJKVWY"

_FENCE = re.compile(
    r"^(?P<f>`{3,}|~{3,})[^\n]*\n.*?^(?P=f)[ \t]*$|^(?P<f2>`{3,}|~{3,})[^\n]*\n.*\Z",
    re.DOTALL | re.MULTILINE,
)
_INLINE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.DOTALL)
_URL = re.compile(r"\b(?:https?|ftp|file)://[^\s<>\"')\]]+[^\s<>\"')\].,;:!?]")
# Absolute, ~, ./ and ../ paths; relative paths with at least one slash and a file extension;
# bare file names with a known extension. Each may end with :line[:col].
_PATH = re.compile(
    r"(?<![\w/.:~-])(?:~|\.{1,2})?(?:/[\w.@+-]+)+/?(?::\d+(?::\d+)?)?"
    r"|(?<![\w/.:~-])[\w.@+-]+(?:/[\w.@+-]+)+\.\w+(?::\d+(?::\d+)?)?"
    r"|(?<![\w/.:~-])[\w@+-]+(?:\.[\w@+-]+)*"
    r"\.(?:py|ts|tsx|js|jsx|mjs|json|md|sh|toml|ya?ml|rs|go|rb|swift|html|css|txt|lock|sql)\b(?::\d+(?::\d+)?)?"
)


def protect(text: str) -> tuple[str, dict[str, str]]:
    """Replace untranslatable spans with placeholders such as ``[[X3]]``.

    Protected, in this order: fenced code blocks, inline code, URLs, and file paths
    (``/a/b.py``, ``src/x.ts:12``, ``config.toml``).

    Args:
        text: The text to mask.

    Returns:
        The masked text, and a map from each placeholder to the original span.
        ``restore(masked, rmap)`` reverses the masking.
    """
    rmap: dict[str, str] = {}
    marker = next((c for c in _MARKERS if f"[[{c}" not in text), None)
    if marker is None:
        return text, rmap  # every marker is in use: leave the text unmasked rather than risk a collision

    def repl(m: re.Match[str]) -> str:
        ph = PH_FMT.format(marker, len(rmap))
        rmap[ph] = m.group(0)
        return ph

    for pattern in (_FENCE, _INLINE, _URL, _PATH):
        text = pattern.sub(repl, text)
    return text, rmap


def restore(text: str, rmap: dict[str, str]) -> str:
    """Put the original spans back, in one pass.

    Restored spans are not scanned again, so placeholder-shaped text inside them stays as it is.

    Args:
        text: Text that contains placeholders.
        rmap: The map returned by `protect()`.

    Returns:
        The text with every known placeholder replaced by its original span.
    """
    if not rmap:
        return text
    keys = re.compile("|".join(re.escape(k) for k in sorted(rmap, key=len, reverse=True)))
    return keys.sub(lambda m: rmap[m.group(0)], text)
