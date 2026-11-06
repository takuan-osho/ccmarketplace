"""Protect text that must not be translated (code, URLs, paths).

Policy lives in `protect()`. Edit the patterns there to change what is kept.
"""

import re

# Placeholder format. Plain ASCII so the translation model copies it as is.
PH_FMT = "[[X{}]]"
PH_RE = re.compile(r"\[\[X(\d+)\]\]")

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

    def repl(m: re.Match[str]) -> str:
        ph = PH_FMT.format(len(rmap))
        rmap[ph] = m.group(0)
        return ph

    for pattern in (_FENCE, _INLINE, _URL, _PATH):
        text = pattern.sub(repl, text)
    return text, rmap


def restore(text: str, rmap: dict[str, str]) -> str:
    """Put the original spans back. Loops so that nested placeholders resolve.

    Args:
        text: Text that contains placeholders.
        rmap: The map returned by `protect()`.

    Returns:
        The text with every known placeholder replaced by its original span.
    """
    for _ in range(3):
        new = PH_RE.sub(lambda m: rmap.get(m.group(0), m.group(0)), text)
        if new == text:
            break
        text = new
    return text
