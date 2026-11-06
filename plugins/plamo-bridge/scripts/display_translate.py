#!/usr/bin/env python3
"""Claude Code MessageDisplay hook: show each assistant message in the user's language.

Claude writes in the source language (English by default). Claude Code calls this hook
once per batch of streamed lines. Non-final batches are buffered and hidden (empty
displayContent). On the final batch the whole message is translated in one request
(mode "whole", with the latest user prompt as context) and shown in place of that batch.

Display only: the transcript and what Claude sees stay in the source language.
If translation fails, the original text is shown, and the servers are started in the
background so that the next message can be translated.

Environment:
  PLAMO_BRIDGE_TARGET_LANG  language shown to the user (default: Japanese)
  PLAMO_BRIDGE_SOURCE_LANG  language Claude writes in (default: English)
  PLAMO_BRIDGE_PORT         port of the translation server (default: 8765)
  PLAMO_BRIDGE_CACHE        buffers and logs (default: ${XDG_CACHE_HOME:-~/.cache}/plamo-bridge)
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = f"http://127.0.0.1:{os.environ.get('PLAMO_BRIDGE_PORT', '8765')}/translate"
SRC = os.environ.get("PLAMO_BRIDGE_SOURCE_LANG", "English")
TGT = os.environ.get("PLAMO_BRIDGE_TARGET_LANG", "Japanese")
BASE = Path(os.environ.get("PLAMO_BRIDGE_CACHE")
            or Path(os.environ.get("XDG_CACHE_HOME") or "~/.cache") / "plamo-bridge").expanduser()
BUF = BASE / "buf"
LOG = BASE / "logs" / "display.log"


def last_user_prompt(transcript_path):
    """Latest typed user prompt from the transcript jsonl, used as translation context."""
    try:
        lines = Path(transcript_path).expanduser().read_text().splitlines()
    except (OSError, ValueError):
        return None
    for line in reversed(lines):
        try:
            o = json.loads(line)
        except ValueError:
            continue
        msg = o.get("message") or {}
        if o.get("type") == "user" and msg.get("role") == "user" and not o.get("isMeta"):
            c = msg.get("content")
            parts = [c] if isinstance(c, str) else [b.get("text", "") for b in c or [] if b.get("type") == "text"]
            text = "\n".join(p for p in parts if p).strip()
            if text:
                return text[:1000]
    return None


def emit(text):
    out = {"hookSpecificOutput": {"hookEventName": "MessageDisplay", "displayContent": text}}
    print(json.dumps(out, ensure_ascii=False))


def log(msg):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    except OSError:
        pass


def start_servers():
    """Start the servers in the background. Returns at once; the control script detaches them."""
    try:
        subprocess.Popen([str(ROOT / "bin" / "plamo-bridge"), "start"], stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        log("translation server unreachable; started the servers in the background")
    except OSError as e:
        log(f"could not start the servers: {e!r}")


def main():
    data = json.load(sys.stdin)
    mid = "".join(c for c in str(data.get("message_id", "")) if c.isalnum() or c == "-") or "unknown"
    delta = data.get("delta") or ""
    buf = BUF / f"{mid}.txt"
    BUF.mkdir(parents=True, exist_ok=True)

    first = data.get("index", 0) == 0  # a new pass over the message: drop any stale buffer
    if not data.get("final"):
        with open(buf, "w" if first else "a", encoding="utf-8") as f:
            f.write(delta)
        emit("")  # hide until the whole message is ready
        return

    text = ("" if first or not buf.exists() else buf.read_text(encoding="utf-8")) + delta
    buf.unlink(missing_ok=True)
    if not text.strip():
        emit(text)
        return
    t0 = time.time()
    try:
        body = json.dumps({"text": text, "src": SRC, "tgt": TGT, "mode": "whole",
                           "context": last_user_prompt(data.get("transcript_path") or "")}).encode()
        req = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
        res = json.load(urllib.request.urlopen(req, timeout=50))
        out = res["text"]
        if not out.endswith("\n") and text.endswith("\n"):
            out += "\n"
        log(f"ok msg={mid[:8]} batches={data.get('index')} chars={len(text)} ms={int((time.time() - t0) * 1000)}")
        emit(out)
    except urllib.error.URLError as e:
        if isinstance(e.reason, ConnectionRefusedError):
            start_servers()
        else:
            log(f"fail msg={mid[:8]} {e!r}")
        emit(text)  # show the original text so nothing is lost
    except Exception as e:  # noqa: BLE001 - a display hook must never fail; show the original text
        log(f"fail msg={mid[:8]} {e!r}")
        emit(text)


if __name__ == "__main__":
    main()
