"""Protect text that must not be translated (code, URLs, paths).

Policy lives in `protect()`. Edit the patterns there to change what is kept.
"""
import re

# Placeholder format. Plain ASCII so the translation model copies it as-is.
PH_FMT = "[[X{}]]"
PH_RE = re.compile(r"\[\[X(\d+)\]\]")

_FENCE = re.compile(r"^(?P<f>`{3,}|~{3,})[^\n]*\n.*?^(?P=f)[ \t]*$|^(?P<f2>`{3,}|~{3,})[^\n]*\n.*\Z",
                    re.DOTALL | re.MULTILINE)
_INLINE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.DOTALL)
_URL = re.compile(r"\b(?:https?|ftp|file)://[^\s<>\"')\]]+[^\s<>\"')\].,;:!?]")
# absolute / ~ / ./ ../ paths, or relative paths with at least one slash and a
# file extension; optional :line[:col] suffix.
_PATH = re.compile(
    r"(?<![\w/.:~-])(?:~|\.{1,2})?(?:/[\w.@+-]+)+/?(?::\d+(?::\d+)?)?"
    r"|(?<![\w/.:~-])[\w.@+-]+(?:/[\w.@+-]+)+\.\w+(?::\d+(?::\d+)?)?"
    r"|(?<![\w/.:~-])[\w@+-]+(?:\.[\w@+-]+)*\.(?:py|ts|tsx|js|jsx|mjs|json|md|sh|toml|ya?ml|rs|go|rb|swift|html|css|txt|lock|sql)\b(?::\d+(?::\d+)?)?"
)


def protect(text: str) -> tuple[str, dict[str, str]]:
    """Replace untranslatable spans with placeholders like ``[[X3]]``.

    Protected, in this order: fenced code blocks, inline `code`, URLs,
    file paths (``/a/b.py``, ``src/x.ts:12``, ``config.toml``).
    Returns ``(masked_text, restore_map)`` where restore_map maps each
    placeholder to the original bytes. ``restore(masked, map)`` inverts it.
    """
    rmap: dict[str, str] = {}

    def sub_with(pattern, s):
        def repl(m):
            ph = PH_FMT.format(len(rmap))
            rmap[ph] = m.group(0)
            return ph
        return pattern.sub(repl, s)

    for pat in (_FENCE, _INLINE, _URL, _PATH):
        text = sub_with(pat, text)
    return text, rmap


def restore(text: str, rmap: dict[str, str]) -> str:
    """Put the original spans back. Loops so nested placeholders resolve."""
    for _ in range(3):
        new = PH_RE.sub(lambda m: rmap.get(m.group(0), m.group(0)), text)
        if new == text:
            break
        text = new
    return text
