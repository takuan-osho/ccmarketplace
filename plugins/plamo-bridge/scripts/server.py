#!/usr/bin/env python3
"""Local translation server: protect/restore + prompts to llama.cpp's llama-server (PLaMo 3 Translate GGUF). Stdlib only.

POST /translate {"text","src":"English","tgt":"Japanese", optional "form","context","mode" (default "whole")} -> {"text", "ms", "warnings"}
GET  /health -> {"ok":true,"llama":...}
"""
import argparse
import json
import re
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from protect import PH_RE, protect, restore

# Language names accepted in requests. Anything else is passed to the model as is, so ISO codes such as
# "fr" or "zh-hans" work too (PLaMo 3 Translate supports 53 languages; see the model card).
LANG = {"english": "en", "japanese": "ja", "chinese": "zh-hans", "korean": "ko", "french": "fr", "german": "de",
        "spanish": "es", "italian": "it", "russian": "ru", "vietnamese": "vi", "thai": "th",
        "indonesian": "id", "dutch": "nl", "arabic": "ar"}
STOPS = ("<|plamo:tag|>", "<|plamo:bos|>")
LINE_PREFIX = re.compile(r"^(\s*(?:#{1,6}\s+|>\s*|[-*+]\s+(?:\[[ xX]\]\s+)?|\d+[.)]\s+))")


class Translator:
    def __init__(self, llama_url, form="polite", glossary=None, model="plamo-3-translate"):
        self.llama_url = llama_url.rstrip("/")
        self.model = model
        self.form, self.glossary = form, glossary or []
        self.lock = threading.Lock()
        self.stats = {"truncated": 0, "fallbacks": 0, "mismatches": 0}

    def _post(self, path, body, timeout=600):
        req = urllib.request.Request(self.llama_url + path, json.dumps(body).encode(),
                                     {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)

    def llama_health(self):
        with urllib.request.urlopen(self.llama_url + "/health", timeout=3) as r:
            return json.load(r)

    def _gen(self, text, src, tgt, form, context):
        kw = {"target_lang": tgt}
        if src: kw["source_lang"] = src
        if context: kw["context"] = context
        if self.glossary: kw["glossary"] = self.glossary
        if tgt == "ja" and form: kw["form"] = form
        body = {"model": self.model, "messages": [{"role": "user", "content": text}],
                "temperature": 0, "stop": list(STOPS), "chat_template_kwargs": kw, "cache_prompt": False,
                "max_tokens": max(256, min(8192, len(text) * 2))}
        res = self._post("/v1/chat/completions", body)
        ch = res["choices"][0]
        if ch.get("finish_reason") == "length":
            self.stats["truncated"] += 1
        out = ch["message"]["content"] or ""
        for s in STOPS:
            out = out.split(s)[0]
        return out.strip()

    def translate_line(self, line, src, tgt, form, context, warnings):
        """Translate one prose line; keep markdown prefix; verify placeholders."""
        prefix = ""
        m = LINE_PREFIX.match(line)
        if m:
            prefix, line = m.group(1), line[m.end():]
        body = line.strip()
        stripped = PH_RE.sub("", body).strip(" \t|-*_:.,;()[]")
        if not stripped or not re.search(r"[A-Za-z]{2,}", stripped):
            return prefix + body  # only placeholders / symbols
        if body.startswith("|") and body.endswith("|"):  # table row: cell by cell
            cells = [c.strip() for c in body.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                return body
            return "| " + " | ".join(
                self.translate_line(c, src, tgt, form, context, warnings) if c else c for c in cells) + " |"
        tr = self._gen(body, src, tgt, form, context)
        want = sorted(PH_RE.findall(body))
        if sorted(PH_RE.findall(tr)) != want:
            warnings.append(f"placeholder mismatch, kept English: {body[:60]!r}")
            return prefix + body
        return prefix + tr

    def _lines(self, masked, s, t, form, ctx_lines, warnings):
        """V0/V1: line by line. ctx_lines=N passes the previous N source lines as context."""
        src_lines = masked.split("\n")
        out = []
        for i, line in enumerate(src_lines):
            if not line.strip():
                out.append(line)
                continue
            ctx = None
            if ctx_lines:
                prev = [x for x in src_lines[:i] if x.strip()][-ctx_lines:]
                ctx = "\n".join(prev) or None
            out.append(self.translate_line(line, s, t, form, ctx, warnings))
        return "\n".join(out)

    def _block(self, blk, s, t, form, context, warnings, whole=False):
        """Translate a multi-line chunk as ONE request. Returns None if placeholders do not match."""
        tr = self._gen(blk, s, t, form, context)
        if sorted(PH_RE.findall(tr)) != sorted(PH_RE.findall(blk)) or not tr:
            self.stats["mismatches"] += 1
            warnings.append(f"placeholder mismatch in {'whole message' if whole else 'block'}: {blk[:50]!r}")
            return None
        return tr

    def translate(self, text, src="English", tgt="Japanese", form=None, context=None, mode="whole"):
        """mode: whole (V3, default: whole message + `context`) | line (V0) | line_ctx (V1, previous 3 lines as context) |
        block (V2, one request per blank-line separated block)."""
        s, t = LANG.get(src.lower(), src.lower()), LANG.get(tgt.lower(), tgt.lower())
        form = form or self.form
        masked, rmap = protect(text)
        warnings = []
        with self.lock:
            self.stats = {"truncated": 0, "fallbacks": 0, "mismatches": 0}
            if mode == "line":
                out = self._lines(masked, s, t, form, 0, warnings)
            elif mode == "line_ctx":
                out = self._lines(masked, s, t, form, 3, warnings)
            elif mode == "block":
                parts = re.split(r"(\n\s*\n)", masked)
                res = []
                for part in parts:
                    if not part.strip() or re.fullmatch(r"\n\s*\n", part):
                        res.append(part)
                        continue
                    only_ph = not re.search(r"[A-Za-z]{2,}", PH_RE.sub("", part))
                    if only_ph:
                        res.append(part)
                        continue
                    tr = self._block(part, s, t, form, context, warnings)
                    if tr is None:
                        self.stats["fallbacks"] += 1
                        tr = self._lines(part, s, t, form, 0, warnings)
                    res.append(tr)
                out = "".join(res)
            elif mode == "whole":
                tr = self._block(masked, s, t, form, context, warnings, whole=True)
                if tr is None or self.stats["truncated"]:
                    self.stats["fallbacks"] += 1
                    warnings.append("whole-message request failed or truncated; fell back to line-by-line")
                    tr = self._lines(masked, s, t, form, 0, warnings)
                out = tr
            else:
                raise ValueError(f"unknown mode {mode}")
            stats = dict(self.stats)
        return restore(out, rmap), warnings, stats


def make_handler(tr):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass

        def _send(self, code, obj):
            b = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            if self.path == "/health":
                try:
                    self._send(200, {"ok": True, "llama": tr.llama_health(), "llama_url": tr.llama_url})
                except Exception as e:  # noqa: BLE001 - report any failure as unhealthy
                    self._send(503, {"ok": False, "error": f"llama-server unreachable: {e!r}"})
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/translate":
                return self._send(404, {"error": "not found"})
            try:
                req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                t0 = time.perf_counter()
                text, warns, stats = tr.translate(req["text"], req.get("src", "English"), req.get("tgt", "Japanese"),
                                                  req.get("form"), req.get("context"), req.get("mode", "whole"))
                self._send(200, {"text": text, "ms": round((time.perf_counter() - t0) * 1000), "warnings": warns,
                                 "stats": stats})
            except Exception as e:  # noqa: BLE001 - return any failure to the client as HTTP 500
                self._send(500, {"error": repr(e)})
    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--llama-url", default="http://127.0.0.1:8766", help="base URL of llama-server (see start-llama.sh)")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--form", choices=["polite", "plain"], default="polite")
    ap.add_argument("--glossary", help="JSON file: [{\"source\":..., \"target\":...}]")
    a = ap.parse_args()
    gl = json.loads(Path(a.glossary).read_text()) if a.glossary else []
    tr = Translator(a.llama_url, a.form, gl)
    print(f"llama-server at {a.llama_url}; listening on 127.0.0.1:{a.port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(tr)).serve_forever()


if __name__ == "__main__":
    main()
