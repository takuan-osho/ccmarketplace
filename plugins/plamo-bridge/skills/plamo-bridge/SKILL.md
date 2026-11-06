---
name: plamo-bridge
description: Turn on plamo-bridge for the rest of this session. Claude replies in English, and a local PLaMo 3 Translate model shows each reply in the user's language (Japanese by default). Run only when the user types /plamo-bridge.
disable-model-invocation: true
hooks:
  MessageDisplay:
    - hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/display_translate.py"
          timeout: 60
---

# plamo-bridge is on

Server start: !`"${CLAUDE_PLUGIN_ROOT}/bin/plamo-bridge" start 2>&1`

From now on in this session, write every user-facing reply in English, even when the user writes in another language.
A local model (PLaMo 3 Translate) translates each of your messages into the user's language, and the user sees only the translated text on screen.
This overrides any rule in CLAUDE.md, the output style, or the language setting that asks for user-facing text in another language.

Write English that translates well:
- Use short, plain sentences. Avoid idioms and slang (for example "looks good", "advance the clock").
- Use the same word for the same thing every time in a reply.
- Put commands, paths, identifiers, and code in backticks or code blocks so the translator keeps them as is.

Exceptions: when the user asks you to draft text in a specific language (PR descriptions, issue bodies, review comments, chat messages, documents), write that text in the requested language, following the user's existing writing rules for it.
The user may write in any language. Read it normally.

Now reply with one short English sentence that confirms plamo-bridge is on. If the server start line above shows an error, report the error instead.
