#!/usr/bin/env python3
"""Print the --yarn-beta-fast and --yarn-beta-slow values for a PLaMo 3 GGUF file (standard library only).

Port of yarn_range_arguments() in pfnet/plamo-translate-cli
(src/plamo_translate/servers/llama_cpp/server.py, lines 52-80, commit c70e3a1).

Usage: yarn_args.py model.gguf [-v]
"""

import math
import struct
import sys
from enum import IntEnum
from pathlib import Path
from typing import BinaryIO

# GGUF metadata value types that map to one struct format character.
FMT = {0: "B", 1: "b", 2: "H", 3: "h", 4: "I", 5: "i", 6: "f", 7: "?", 10: "Q", 11: "q", 12: "d"}


class GgufType(IntEnum):
    """GGUF metadata value types that need more than one struct read."""

    STRING = 8
    ARRAY = 9


class _MetaReader:
    """Read the key-value metadata at the start of a GGUF file."""

    def __init__(self, f: BinaryIO) -> None:
        self.f = f

    def scalar(self, fmt: str) -> int | float | bool:
        return struct.unpack("<" + fmt, self.f.read(struct.calcsize("<" + fmt)))[0]

    def uint(self, fmt: str = "Q") -> int:
        return int(self.scalar(fmt))

    def string(self) -> str:
        return self.f.read(self.uint()).decode()

    def value(self, t: int) -> object:
        match t:
            case _ if t in FMT:
                return self.scalar(FMT[t])
            case GgufType.STRING:
                return self.string()
            case GgufType.ARRAY:
                elem = self.uint("I")
                return [self.value(elem) for _ in range(self.uint())]
            case _:
                raise ValueError(t)

    def read(self) -> dict[str, object]:
        if self.f.read(4) != b"GGUF":
            raise ValueError("not a GGUF file")
        self.uint("I")  # version
        self.uint()  # tensor count
        meta: dict[str, object] = {}
        for _ in range(self.uint()):
            key = self.string()
            meta[key] = self.value(self.uint("I"))
        return meta


def read_meta(path: str | Path) -> dict[str, object]:
    """Return the metadata of a GGUF file.

    Args:
        path: Path to the GGUF file.

    Returns:
        A map from metadata key to value.
    """
    with Path(path).open("rb") as f:
        return _MetaReader(f).read()


def _num(m: dict[str, object], key: str, default: float | None = None) -> float:
    """Return a numeric metadata value as float."""
    v = m.get(key, default)
    if not isinstance(v, (int, float)):
        raise TypeError(f"{key}: expected a number, got {v!r}")
    return float(v)


def yarn_args(m: dict[str, object]) -> list[str]:
    """Return llama-server flags that reproduce yarn_truncate=false, or an empty list if they are not needed.

    Args:
        m: GGUF metadata from `read_meta()`.

    Returns:
        The ``--yarn-beta-fast`` and ``--yarn-beta-slow`` flags with their values.
    """
    arch = m.get("general.architecture")
    sc = f"{arch}.rope.scaling."
    if m.get(sc + "type") != "yarn" or m.get(sc + "yarn_truncate", True):
        return []
    dim_key = f"{arch}.rope.dimension_count"
    dims = _num(m, dim_key if m.get(dim_key) else f"{arch}.attention.key_length")
    orig = _num(m, sc + "original_context_length")
    scale = dims / (2 * math.log(_num(m, f"{arch}.rope.freq_base")))
    low = round(scale * math.log(orig / (_num(m, sc + "yarn_beta_fast", 32.0) * 2 * math.pi))) + 0.001
    high = round(scale * math.log(orig / (_num(m, sc + "yarn_beta_slow", 1.0) * 2 * math.pi))) - 0.001

    def beta(d: float) -> float:
        return orig / (2 * math.pi * math.exp(d / scale))

    return ["--yarn-beta-fast", f"{beta(low):.8g}", "--yarn-beta-slow", f"{beta(high):.8g}"]


def main() -> None:
    """Print the flags for the GGUF file named on the command line."""
    meta = read_meta(sys.argv[1])
    if "-v" in sys.argv:
        rope = {k: v for k, v in meta.items() if "rope" in k or k == "general.architecture"}
        sys.stderr.write(f"{rope}\n")
    sys.stdout.write(" ".join(yarn_args(meta)) + "\n")


if __name__ == "__main__":
    main()
