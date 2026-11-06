#!/usr/bin/env python3
"""Shared-token helpers for plamo-bridge (standard library only).

One random token, kept in a 0600 file in the cache folder, protects both local hops:

- hook -> translation server: the hook sends ``Authorization: Bearer <token>``.
- translation server -> llama-server: llama-server runs with ``--api-key-file <token file>``.

The token does not change between runs, because the servers keep running after Claude Code exits. It protects
against other users on the same machine. It does not protect against programs that run as the same user, because
they can read the token file.

Command line (used by ``bin/plamo-bridge``):
    auth.py init TOKEN_FILE               create the token file if it does not exist
    auth.py check-server PORT TOKEN_FILE  exit 0: our server, 1: nothing answers, 2: another server
    auth.py check-llama PORT TOKEN_FILE   exit 0: llama-server with our key, 1: nothing answers, 2: another server,
                                          3: a llama-server that is still loading its model
"""

import hashlib
import hmac
import json
import os
import secrets
import sys
import urllib.error
import urllib.request
from http import HTTPStatus
from pathlib import Path

OURS, DOWN, FOREIGN, LOADING = 0, 1, 2, 3
TIMEOUT_S = 3


def init_token(path: Path) -> None:
    """Create the token file with mode 0600 if it does not exist yet."""
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        path.chmod(0o600)
        return
    with os.fdopen(fd, "w") as f:
        f.write(secrets.token_hex(32) + "\n")


def read_token(path: Path) -> str:
    """Return the token from the token file. Raises OSError if the file is missing."""
    return path.read_text(encoding="utf-8").strip()


def proof(token: str, nonce: str) -> str:
    """Return the value that shows a server knows the token, without sending the token itself."""
    return hmac.new(token.encode(), nonce.encode(), hashlib.sha256).hexdigest()


def _get(url: str, token: str | None = None) -> tuple[int, bytes]:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=TIMEOUT_S) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()  # keep the body: an unhealthy server (503) still sends its proof


def check_server(port: int, token: str) -> int:
    """Return OURS if the translation server on the port proves that it knows the token."""
    nonce = secrets.token_hex(16)
    try:
        _, body = _get(f"http://127.0.0.1:{port}/health?nonce={nonce}")
    except OSError:
        return DOWN
    try:
        got = json.loads(body).get("proof", "")
    except ValueError:
        return FOREIGN
    return OURS if hmac.compare_digest(str(got), proof(token, nonce)) else FOREIGN


def check_llama(port: int, token: str) -> int:
    """Return OURS if llama-server on the port accepts our token and rejects no token and a wrong token.

    A server that accepts any Authorization header fails this check. llama-server cannot prove that it knows the
    token, so a program that copies llama-server's answers for these three requests can still pass.
    """
    base = f"http://127.0.0.1:{port}/v1/models"
    try:
        without, _ = _get(base)
        wrong, _ = _get(base, secrets.token_hex(32))
        ours, _ = _get(base, token)
    except OSError:
        return DOWN
    if without == wrong == ours == HTTPStatus.SERVICE_UNAVAILABLE:
        return LOADING  # llama-server answers 503 to every request until the model is loaded
    rejected = without == wrong == HTTPStatus.UNAUTHORIZED
    return OURS if rejected and ours == HTTPStatus.OK else FOREIGN


def main() -> int:
    """Run the command given on the command line."""
    match sys.argv[1:]:
        case ["init", path]:
            init_token(Path(path))
            return OURS
        case ["check-server", port, path]:
            return check_server(int(port), read_token(Path(path)))
        case ["check-llama", port, path]:
            return check_llama(int(port), read_token(Path(path)))
        case _:
            raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main())
