#!/usr/bin/env python3
"""Claude Code MessageDisplay hook: show each assistant message in the user's language.

Claude writes in the source language (English by default). Claude Code calls this hook once per batch of streamed
lines. Non-final batches are buffered and hidden (empty displayContent). On the final batch the whole message is
translated in one request (mode "whole", with the latest user prompt as context) and shown in place of that batch.

Display only: the transcript and what Claude sees stay in the source language. If translation fails, the original
text is shown, and the servers are started in the background so that the next message can be translated.

Environment:
  PLAMO_BRIDGE_TARGET_LANG  language shown to the user (default: Japanese)
  PLAMO_BRIDGE_SOURCE_LANG  language Claude writes in (default: English)
  PLAMO_BRIDGE_PORT         port of the translation server (default: 8765)
  PLAMO_BRIDGE_CACHE        token, buffers, and logs (default: ${XDG_CACHE_HOME:-~/.cache}/plamo-bridge)

Files are created readable by the current user only (folders 0700, files 0600).
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from http import HTTPStatus
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = f"http://127.0.0.1:{os.environ.get('PLAMO_BRIDGE_PORT', '8765')}/translate"
SRC = os.environ.get("PLAMO_BRIDGE_SOURCE_LANG", "English")
TGT = os.environ.get("PLAMO_BRIDGE_TARGET_LANG", "Japanese")
BASE = Path(
    os.environ.get("PLAMO_BRIDGE_CACHE") or Path(os.environ.get("XDG_CACHE_HOME") or "~/.cache") / "plamo-bridge"
).expanduser()
TOKEN = BASE / "token"
BUF = BASE / "buf"
LOG = BASE / "logs" / "display.log"
CONTEXT_CHARS = 1000
TIMEOUT_S = 50  # below the hook timeout (60 s) so that the original text can still be shown


def last_user_prompt(transcript_path: str) -> str | None:
    """Return the latest typed user prompt from the transcript (JSON Lines), used as translation context."""
    try:
        lines = Path(transcript_path).expanduser().read_text(encoding="utf-8").splitlines()
    except OSError, ValueError:
        return None
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        msg = entry.get("message") or {}
        if entry.get("type") != "user" or msg.get("role") != "user" or entry.get("isMeta"):
            continue
        content = msg.get("content")
        if isinstance(content, str):
            parts = [content]
        else:
            parts = [b.get("text", "") for b in content or [] if b.get("type") == "text"]
        if text := "\n".join(p for p in parts if p).strip():
            return text[:CONTEXT_CHARS]
    return None


def emit(text: str) -> None:
    """Print the hook result that tells Claude Code what to display."""
    out = {"hookSpecificOutput": {"hookEventName": "MessageDisplay", "displayContent": text}}
    sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")


def log(msg: str) -> None:
    """Append one line to the display log. Never raises."""
    try:
        LOG.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    except OSError:
        pass


def start_servers() -> None:
    """Start the servers in the background. Returns at once; the control script detaches them."""
    try:
        subprocess.Popen(  # noqa: S603 - fixed path inside this plugin, no shell
            [str(ROOT / "bin" / "plamo-bridge"), "start"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        log("translation server unreachable; started the servers in the background")
    except OSError as e:
        log(f"could not start the servers: {e!r}")


def translate(text: str, transcript_path: str) -> str:
    """Return the translated text. Raises an error if the server fails."""
    body = json.dumps(
        {
            "text": text,
            "src": SRC,
            "tgt": TGT,
            "mode": "whole",
            "context": last_user_prompt(transcript_path),
        }
    ).encode()
    token = TOKEN.read_text(encoding="utf-8").strip()
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    req = urllib.request.Request(URL, body, headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
        out = json.load(r)["text"]
    if text.endswith("\n") and not out.endswith("\n"):
        out += "\n"
    return out


def collect(mid: str, index: int, delta: str, *, final: bool) -> str | None:
    """Buffer one batch. Return the whole message on the final batch, or None before it."""
    BUF.mkdir(mode=0o700, parents=True, exist_ok=True)
    buf = BUF / f"{mid}.txt"
    first = index == 0  # a new pass over the message: drop any stale buffer
    if not final:
        with buf.open("w" if first else "a", encoding="utf-8") as f:
            f.write(delta)
        return None
    text = ("" if first or not buf.exists() else buf.read_text(encoding="utf-8")) + delta
    buf.unlink(missing_ok=True)
    return text


def main() -> None:
    """Handle one MessageDisplay hook call read from stdin."""
    os.umask(0o077)
    data = json.load(sys.stdin)
    mid = "".join(c for c in str(data.get("message_id", "")) if c.isalnum() or c == "-") or "unknown"
    delta = data.get("delta") or ""
    final = bool(data.get("final"))
    try:
        text = collect(mid, data.get("index", 0), delta, final=final)
    except OSError as e:
        log(f"buffer error msg={mid[:8]} {e!r}")
        emit(delta)  # show this batch as is, so that it is not lost
        return
    if text is None:
        emit("")  # hide until the whole message is ready
        return
    if not text.strip():
        emit(text)
        return
    t0 = time.time()
    try:
        out = translate(text, data.get("transcript_path") or "")
    except urllib.error.HTTPError as e:
        if e.code == HTTPStatus.UNAUTHORIZED:
            log(f"fail msg={mid[:8]} the server on the port rejected our token; it may be another program")
        else:
            log(f"fail msg={mid[:8]} {e!r}")
        emit(text)  # show the original text so that nothing is lost
    except urllib.error.URLError as e:
        if isinstance(e.reason, ConnectionRefusedError):
            start_servers()
        else:
            log(f"fail msg={mid[:8]} {e!r}")
        emit(text)
    except FileNotFoundError:
        start_servers()  # no token file yet: the servers were never started
        emit(text)
    except Exception as e:  # noqa: BLE001 - a display hook must never fail; show the original text
        log(f"fail msg={mid[:8]} {e!r}")
        emit(text)
    else:
        ms = int((time.time() - t0) * 1000)
        log(f"ok msg={mid[:8]} batches={data.get('index')} chars={len(text)} ms={ms}")
        emit(out)


if __name__ == "__main__":
    main()
