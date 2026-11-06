# plamo-bridge

A plugin that bridges the language between you and Claude Code. Claude writes its replies in English, and a local [PLaMo 3 Translate](https://huggingface.co/pfnet/plamo-3-translate-0.8b-GGUF) model shows each reply on your screen in your language (Japanese by default).

This is a personal project. It is not made or endorsed by Preferred Networks, the developer of PLaMo.

## Overview

Claude Code has a `MessageDisplay` hook that can replace the text shown for an assistant message. plamo-bridge uses it like this:

1. Claude writes the reply in plain English.
2. The hook collects the streamed reply and sends the whole message to a local translation server, with your latest prompt as context.
3. The server hides code, paths, and URLs behind placeholders, asks PLaMo 3 Translate (through llama.cpp's `llama-server`) for the translation, and puts the hidden parts back.
4. Claude Code shows the translated text in place of the English text, and renders it as Markdown as usual.

Only the display changes. The transcript, and what Claude reads in later turns, stay in English. If translation fails, you see the original English text.

## Requirements

- macOS or Linux, with Python 3.14 or later as `python3` (standard library only)
- llama.cpp's `llama-server` on your `PATH` (macOS: `brew install llama.cpp`)
- About 550 MB of disk space for the model. `llama-server` downloads it on first start into the Hugging Face cache.
- About 0.8 GB of memory while the servers run

## Installation

```
/plugin install plamo-bridge --marketplace takuan-osho/ccmarketplace
```

## Usage

### Turn it on in a session

```
/plamo-bridge
```

The skill starts the servers if they are not running, registers the display hook, and tells Claude to reply in English. Translation stays on until the session ends. There is no command to turn it off. To stop translation, start a new session.

The first start downloads the model, so the first replies can appear in English until the servers are ready.

### Start a session with it on: `claude-plamo`

`bin/claude-plamo` starts Claude Code with the hook and the English-reply instruction from the first message. The instruction is passed with `--append-system-prompt-file`, so it stays in effect after `/compact`. Use this for long sessions.

Link it into a folder on your `PATH`. Point the link at a clone of this repository, because the installed plugin's path changes with each version:

```sh
ln -s /path/to/ccmarketplace/plugins/plamo-bridge/bin/claude-plamo ~/.local/bin/claude-plamo
claude-plamo            # takes the same arguments as claude
```

Use either `claude-plamo` or `/plamo-bridge` in a session, not both. Both register the same hook.

### Manage the servers

The servers keep running after Claude Code exits. `stop` stops only the processes that `start` recorded.

```sh
bin/plamo-bridge status
bin/plamo-bridge stop
```

## Configuration

Set these environment variables before you start Claude Code:

| Variable | Default | Meaning |
|----------|---------|---------|
| `PLAMO_BRIDGE_TARGET_LANG` | `Japanese` | Language shown to you. A name such as `French`, or a code from the model card such as `fr` or `zh-hans` |
| `PLAMO_BRIDGE_SOURCE_LANG` | `English` | Language Claude writes in |
| `PLAMO_MODEL` | `0.8b` | Model size: `0.8b` or `2b` |
| `PLAMO_BRIDGE_PORT` | `8765` | Port of the translation server |
| `PLAMO_BRIDGE_LLAMA_PORT` | `8766` | Port of `llama-server` |
| `PLAMO_BRIDGE_CACHE` | `${XDG_CACHE_HOME:-~/.cache}/plamo-bridge` | Token, message buffers, process IDs, and logs |

PLaMo 3 Translate supports 53 languages. The skill and `claude-plamo` always ask Claude to write in English. If you change `PLAMO_BRIDGE_SOURCE_LANG`, change that instruction too.

## Security

The servers listen on `127.0.0.1` only. Both local connections use one shared token:

- The hook sends the token to the translation server, which rejects requests without it.
- The translation server sends the same token to `llama-server`, which runs with `--api-key-file`.
- `start` checks that a server already on a port proves that it knows the token, without the token being sent. If another program uses the port, `start` stops with an error and does not touch that program.

The token is created once, in `token` in the cache folder, and reused, because the servers keep running between sessions. Everything in the cache folder is readable by your user only (folders `0700`, files `0600`).

What this protects against: other users on the same machine. What it does not protect against:

- Programs that run as your own user. They can read the token file, like the hook does.
- A program that takes the port before the servers start, while a session is running. The hook does not check the server before it sends a reply, so such a program receives the reply text and the token. `start` reports the port conflict the next time it runs.

The plugin is designed for a single-user machine. It does not limit request size or the number of requests.

## Measurements

Measured on the author's Mac with 10 sample replies, 3 rounds each:

| Model | Median time per message | Memory (RSS) |
|-------|-------------------------|--------------|
| 0.8B (default) | 1.14 s | about 0.8 GB |
| 2B | 2.97 s | 2.4 to 2.7 GB |

The 2B model made fewer meaning errors in technical text (1 against 3 in the same samples).

## Limitations

- The translated text appears only after the whole message is complete.
- Replies in the `/btw` side chat are not translated, because Claude Code does not run `MessageDisplay` hooks there.
- After `/compact`, the English-reply instruction from `/plamo-bridge` can be lost from the summary. The hook stays on, but Claude may go back to replying in your language. `claude-plamo` does not have this problem.
- Translation quality was checked only for English to Japanese. Other languages work, but the 0.8B model made clear mistakes in a short Korean test.

## Files

| Path | Purpose |
|------|---------|
| `skills/plamo-bridge/SKILL.md` | The `/plamo-bridge` skill. Registers the hook and starts the servers |
| `bin/plamo-bridge` | Starts, stops, and checks the servers |
| `scripts/auth.py` | Creates the shared token and checks whether a server on a port is ours |
| `bin/claude-plamo` | Launcher that starts Claude Code with the bridge on |
| `prompts/reply-in-source-language.md` | English-reply instruction used by `claude-plamo` |
| `scripts/display_translate.py` | The `MessageDisplay` hook |
| `scripts/server.py` | Translation server (`POST /translate`), with code and path protection from `scripts/protect.py` |
| `scripts/start-llama.sh` | Starts `llama-server` with the model |
| `scripts/yarn_args.py` | Computes the YaRN values used by `start-llama.sh` |
| `scripts/glossary.example.json` | Example glossary for `server.py --glossary` |
| `tests/` | Unit tests. Run `python3 -m unittest discover -s tests` from this folder |
| `pyproject.toml` | Settings for the development checks: `uvx ruff check .`, `uvx ruff format --check .`, and `uvx ty check` |

## YaRN workaround

The PLaMo 3 GGUF files set `yarn_truncate=false`, which llama.cpp currently ignores. `start-llama.sh` passes `--yarn-beta-fast` and `--yarn-beta-slow` with the values that [pfnet/plamo-translate-cli](https://github.com/pfnet/plamo-translate-cli) computes. The values are the same for 0.8B and 2B. To compute them for another GGUF file, run `python3 scripts/yarn_args.py <file.gguf>`. Remove the flags once llama.cpp supports `yarn_truncate`.

## License

The model is distributed under the [PLaMo Community License](https://plamo.preferredai.jp/info/plamo-community-license-en). Read it before you use the model. This plugin does not include the model. `llama-server` downloads it from Hugging Face.
