# AGENTS.md

## Code Review Rules

### plamo-bridge (`plugins/plamo-bridge/`)

plamo-bridge shows Claude Code replies in another language on screen only. A translation mistake changes what the
user sees, not the transcript or what Claude does. It is designed for a single-user machine.

Severity:

- P1 or higher: the plugin fails to start or stop, a reply is lost or hidden with no fallback to the original text,
  a token or a reply leaves `127.0.0.1`, files are created outside the cache folder or with permissions wider than
  `0700`/`0600`, or command injection.
- P2 (does not block merging): an unusual Markdown construct that `scripts/protect.py` does not recognize, or that the
  line-by-line fallback in `scripts/server.py` renders imperfectly. Examples: rare fence forms, nesting of lists,
  quotes, and code. Report these, but mark them P2.

Do not report, because the owner accepted these risks (see the Security section of `plugins/plamo-bridge/README.md`):

- Port squatting or impersonation of the local servers by another user or process on the same machine.
- Sending the shared token or reply text to a local server before verifying its identity.
- Missing Unix domain sockets, TLS, or challenge-response between the local processes.
- Denial of service against the local servers (request size, concurrency, read timeouts).
