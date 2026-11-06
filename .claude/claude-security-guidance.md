# Security review rules for this repository

## plamo-bridge: accepted risks (do not report)

plamo-bridge (`plugins/plamo-bridge/`) is designed for a single-user machine. The owner has reviewed and accepted
these risks. Do not report findings in these classes for plamo-bridge:

- Port squatting or impersonation of the local servers on `127.0.0.1` (the translation server and llama-server),
  by another user or process on the same machine.
- The hook, `check-llama`, or `server.py` sending the shared token or the reply text to a local server without
  first verifying that server's identity.
- Missing Unix domain sockets, TLS, or per-request challenge-response between these local processes.
- Denial of service against these local servers: request size, concurrency, read timeouts.
- Programs that run as the same user reading the token file.

Still report other issues in plamo-bridge, such as command injection, unsafe file handling outside the cache
folder, or anything that exposes the servers beyond `127.0.0.1`.
