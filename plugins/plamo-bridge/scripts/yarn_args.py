#!/usr/bin/env python3
"""Print the --yarn-beta-fast/--yarn-beta-slow values for a PLaMo 3 GGUF (stdlib only).

Port of yarn_range_arguments() in pfnet/plamo-translate-cli
(src/plamo_translate/servers/llama_cpp/server.py, lines 52-80, commit c70e3a1). Usage: yarn_args.py model.gguf
"""
import math
import struct
import sys

FMT = {0: "B", 1: "b", 2: "H", 3: "h", 4: "I", 5: "i", 6: "f", 7: "?", 10: "Q", 11: "q", 12: "d"}


def read_meta(path):
    with open(path, "rb") as f:
        return _read_meta(f)


def _read_meta(f):
    rd = lambda fmt: struct.unpack("<" + fmt, f.read(struct.calcsize("<" + fmt)))[0]
    assert f.read(4) == b"GGUF"
    rd("I"); rd("Q"); n = rd("Q")
    string = lambda: f.read(rd("Q")).decode()

    def value(t):
        if t in FMT: return rd(FMT[t])
        if t == 8: return string()
        if t == 9:
            et, cnt = rd("I"), rd("Q")
            return [value(et) for _ in range(cnt)]
        raise ValueError(t)
    meta = {}
    for _ in range(n):
        k = string(); t = rd("I"); meta[k] = value(t)
    return meta


def yarn_args(m):
    arch = m.get("general.architecture"); sc = f"{arch}.rope.scaling."
    if m.get(sc + "type") != "yarn" or m.get(sc + "yarn_truncate", True): return []
    dims = m.get(f"{arch}.rope.dimension_count") or m.get(f"{arch}.attention.key_length")
    orig = m.get(sc + "original_context_length"); base = m.get(f"{arch}.rope.freq_base")
    scale = dims / (2 * math.log(base))
    low = round(scale * math.log(orig / (m.get(sc + "yarn_beta_fast", 32.0) * 2 * math.pi))) + 0.001
    high = round(scale * math.log(orig / (m.get(sc + "yarn_beta_slow", 1.0) * 2 * math.pi))) - 0.001
    beta = lambda d: orig / (2 * math.pi * math.exp(d / scale))
    return ["--yarn-beta-fast", f"{beta(low):.8g}", "--yarn-beta-slow", f"{beta(high):.8g}"]


if __name__ == "__main__":
    m = read_meta(sys.argv[1])
    if "-v" in sys.argv:
        print({k: v for k, v in m.items() if "rope" in k or k == "general.architecture"}, file=sys.stderr)
    print(" ".join(yarn_args(m)))
