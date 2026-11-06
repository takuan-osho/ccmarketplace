#!/usr/bin/env python3
"""Local translation server for plamo-bridge (standard library only).

Masks code and paths, sends the text to llama.cpp's llama-server (PLaMo 3 Translate GGUF), and restores the masked
parts in the result.

    POST /translate {"text", "src": "English", "tgt": "Japanese", optional "form", "context", "mode"}
        -> {"text", "ms", "warnings", "stats"}   (needs "Authorization: Bearer <token>")
    GET  /health[?nonce=N] -> {"ok": true, "llama": ..., "proof": HMAC(token, N)}

The token comes from --token-file (see auth.py). The same token is sent to llama-server, which runs with
--api-key-file.
"""

import argparse
import hmac
import json
import re
import threading
import time
import urllib.request
from collections.abc import Mapping
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

from auth import proof, read_token
from protect import PH_RE, protect, restore

type Json = dict[str, Any]  # parsed JSON from llama-server

# Language names accepted in requests. Anything else is passed to the model as is, so ISO codes such as
# "fr" or "zh-hans" work too (PLaMo 3 Translate supports 53 languages; see the model card).
LANG = {
    "english": "en",
    "japanese": "ja",
    "chinese": "zh-hans",
    "korean": "ko",
    "french": "fr",
    "german": "de",
    "spanish": "es",
    "italian": "it",
    "russian": "ru",
    "vietnamese": "vi",
    "thai": "th",
    "indonesian": "id",
    "dutch": "nl",
    "arabic": "ar",
}
MODES = ("whole", "line", "line_ctx", "block")
STOPS = ("<|plamo:tag|>", "<|plamo:bos|>")
LINE_PREFIX = re.compile(r"^(\s*(?:#{1,6}\s+|>\s*|[-*+]\s+(?:\[[ xX]\]\s+)?|\d+[.)]\s+))")
TABLE_RULE = re.compile(r":?-{2,}:?")
BLANK_LINES = re.compile(r"(\n\s*\n)")
WORD = re.compile(r"[A-Za-z]{2,}")
CONTEXT_LINES = 3


def _has_words(text: str) -> bool:
    """Return True if the text has something to translate besides placeholders and symbols."""
    return bool(WORD.search(PH_RE.sub("", text)))


def _same_placeholders(a: str, b: str) -> bool:
    return sorted(PH_RE.findall(a)) == sorted(PH_RE.findall(b))


class Translator:
    """Send masked text to llama-server and check that every placeholder comes back."""

    def __init__(
        self,
        llama_url: str,
        token: str,
        form: str = "polite",
        glossary: list[dict[str, str]] | None = None,
        model: str = "plamo-3-translate",
    ) -> None:
        """Set up a translator for one llama-server.

        Args:
            llama_url: Base URL of llama-server.
            token: Shared token. Sent to llama-server, and required from clients.
            form: Japanese politeness, "polite" or "plain". Used only when the target is Japanese.
            glossary: Term pairs, each {"source": ..., "target": ...}.
            model: Model alias that llama-server serves.
        """
        self.llama_url = llama_url.rstrip("/")
        self.token = token
        self.model = model
        self.form = form
        self.glossary = glossary or []
        self.lock = threading.Lock()
        self.stats = {"truncated": 0, "fallbacks": 0, "mismatches": 0}

    def _post(self, path: str, body: Mapping[str, object], timeout: float = 600) -> Json:
        req = urllib.request.Request(
            self.llama_url + path,
            json.dumps(body).encode(),
            {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)

    def llama_health(self) -> Json:
        """Return llama-server's health response. Raises an error if it does not answer."""
        with urllib.request.urlopen(self.llama_url + "/health", timeout=3) as r:
            return json.load(r)

    def _gen(self, text: str, src: str, tgt: str, form: str | None, context: str | None) -> str:
        kw: dict[str, object] = {"target_lang": tgt}
        if src:
            kw["source_lang"] = src
        if context:
            kw["context"] = context
        if self.glossary:
            kw["glossary"] = self.glossary
        if tgt == "ja" and form:
            kw["form"] = form
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": text}],
            "temperature": 0,
            "stop": list(STOPS),
            "chat_template_kwargs": kw,
            "cache_prompt": False,
            "max_tokens": max(256, min(8192, len(text) * 2)),
        }
        choice = self._post("/v1/chat/completions", body)["choices"][0]
        if choice.get("finish_reason") == "length":
            self.stats["truncated"] += 1
        out = choice["message"]["content"] or ""
        for s in STOPS:
            out = out.split(s)[0]
        return out.strip()

    def translate_line(
        self, line: str, src: str, tgt: str, form: str | None, context: str | None, warnings: list[str]
    ) -> str:
        """Translate one line of prose. Keeps the Markdown prefix, and translates table rows cell by cell.

        Returns:
            The translated line, or the original line if a placeholder got lost.
        """
        prefix = ""
        if m := LINE_PREFIX.match(line):
            prefix, line = m.group(1), line[m.end() :]
        body = line.strip()
        if not _has_words(body):
            return prefix + body  # only placeholders or symbols
        if body.startswith("|") and body.endswith("|"):
            cells = [c.strip() for c in body.strip("|").split("|")]
            if all(TABLE_RULE.fullmatch(c) for c in cells if c):
                return body
            translated = [self.translate_line(c, src, tgt, form, context, warnings) if c else c for c in cells]
            return "| " + " | ".join(translated) + " |"
        tr = self._gen(body, src, tgt, form, context)
        if not _same_placeholders(body, tr):
            warnings.append(f"placeholder mismatch, kept the original: {body[:60]!r}")
            return prefix + body
        return prefix + tr

    def _lines(self, masked: str, src: str, tgt: str, form: str | None, ctx_lines: int, warnings: list[str]) -> str:
        """Translate line by line. With ctx_lines=N, pass the previous N source lines as context."""
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
            out.append(self.translate_line(line, src, tgt, form, ctx, warnings))
        return "\n".join(out)

    def _block(
        self, blk: str, src: str, tgt: str, form: str | None, context: str | None, warnings: list[str]
    ) -> str | None:
        """Translate a multi-line chunk in one request. Returns None if the placeholders do not match."""
        tr = self._gen(blk, src, tgt, form, context)
        if not tr or not _same_placeholders(blk, tr):
            self.stats["mismatches"] += 1
            warnings.append(f"placeholder mismatch in a block: {blk[:50]!r}")
            return None
        return tr

    def _by_blocks(
        self, masked: str, src: str, tgt: str, form: str | None, context: str | None, warnings: list[str]
    ) -> str:
        res = []
        for part in BLANK_LINES.split(masked):
            if not part.strip() or not _has_words(part):
                res.append(part)
                continue
            tr = self._block(part, src, tgt, form, context, warnings)
            if tr is None:
                self.stats["fallbacks"] += 1
                tr = self._lines(part, src, tgt, form, 0, warnings)
            res.append(tr)
        return "".join(res)

    def translate(
        self,
        text: str,
        src: str = "English",
        tgt: str = "Japanese",
        form: str | None = None,
        context: str | None = None,
        mode: str = "whole",
    ) -> tuple[str, list[str], dict[str, int]]:
        """Translate text with code, URLs, and paths kept as they are.

        Args:
            text: The text to translate.
            src: Source language name or code.
            tgt: Target language name or code.
            form: Japanese politeness; defaults to the server setting.
            context: Text that helps the model, such as the user's prompt. Not translated.
            mode: "whole" (one request for the whole message, the default), "line", "line_ctx" (line by line with
                the previous lines as context), or "block" (one request per blank-line separated block).

        Returns:
            The translated text, warnings, and counters for truncations, fallbacks, and mismatches.
        """
        if mode not in MODES:
            raise ValueError(f"unknown mode {mode}")
        s, t = LANG.get(src.lower(), src.lower()), LANG.get(tgt.lower(), tgt.lower())
        form = form or self.form
        masked, rmap = protect(text)
        warnings: list[str] = []
        with self.lock:
            self.stats = {"truncated": 0, "fallbacks": 0, "mismatches": 0}
            match mode:
                case "line":
                    out = self._lines(masked, s, t, form, 0, warnings)
                case "line_ctx":
                    out = self._lines(masked, s, t, form, CONTEXT_LINES, warnings)
                case "block":
                    out = self._by_blocks(masked, s, t, form, context, warnings)
                case _:
                    tr = self._block(masked, s, t, form, context, warnings)
                    if tr is None or self.stats["truncated"]:
                        self.stats["fallbacks"] += 1
                        warnings.append("whole-message request failed or was truncated; fell back to line by line")
                        tr = self._lines(masked, s, t, form, 0, warnings)
                    out = tr
            stats = dict(self.stats)
        return restore(out, rmap), warnings, stats


def make_handler(tr: Translator) -> type[BaseHTTPRequestHandler]:
    """Return a request handler class bound to the given translator."""

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:  # noqa: A002 - name set by the base class
            pass

        def _send(self, code: int, obj: dict[str, object]) -> None:
            b = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def _authorized(self) -> bool:
            got = self.headers.get("Authorization", "")
            return hmac.compare_digest(got.encode(), f"Bearer {tr.token}".encode())

        def do_GET(self) -> None:
            url = urlsplit(self.path)
            if url.path != "/health":
                self._send(404, {"error": "not found"})
                return
            res: dict[str, object] = {"llama_url": tr.llama_url}
            if nonce := parse_qs(url.query).get("nonce", [""])[0]:
                res["proof"] = proof(tr.token, nonce)  # lets a client check this server without sending the token
            try:
                self._send(200, {"ok": True, "llama": tr.llama_health(), **res})
            except Exception as e:  # noqa: BLE001 - report any failure as unhealthy
                self._send(503, {"ok": False, "error": f"llama-server unreachable: {e!r}", **res})

        def do_POST(self) -> None:
            if self.path != "/translate":
                self._send(404, {"error": "not found"})
                return
            if not self._authorized():
                self._send(401, {"error": "missing or wrong token"})
                return
            try:
                req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                t0 = time.perf_counter()
                text, warns, stats = tr.translate(
                    req["text"],
                    req.get("src", "English"),
                    req.get("tgt", "Japanese"),
                    req.get("form"),
                    req.get("context"),
                    req.get("mode", "whole"),
                )
                ms = round((time.perf_counter() - t0) * 1000)
                self._send(200, {"text": text, "ms": ms, "warnings": warns, "stats": stats})
            except Exception as e:  # noqa: BLE001 - return any failure to the client as HTTP 500
                self._send(500, {"error": repr(e)})

    return Handler


def main() -> None:
    """Parse the command line and serve until stopped."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--llama-url", default="http://127.0.0.1:8766", help="base URL of llama-server")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--token-file", type=Path, required=True, help="shared token file (see auth.py)")
    ap.add_argument("--form", choices=["polite", "plain"], default="polite")
    ap.add_argument("--glossary", type=Path, help='JSON file: [{"source": ..., "target": ...}]')
    a = ap.parse_args()
    glossary = json.loads(a.glossary.read_text(encoding="utf-8")) if a.glossary else []
    tr = Translator(a.llama_url, read_token(a.token_file), a.form, glossary)
    print(f"llama-server at {a.llama_url}; listening on 127.0.0.1:{a.port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(tr)).serve_forever()


if __name__ == "__main__":
    main()
