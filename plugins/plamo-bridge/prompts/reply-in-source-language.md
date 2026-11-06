# plamo-bridge

In this session, write every user-facing reply in English, even when the user writes in another language.
A local model (PLaMo 3 Translate) translates each of your messages into the user's language, and the user sees only the translated text on screen.
This overrides any rule in CLAUDE.md, the output style, or the language setting that asks for user-facing text in another language.

Write English that translates well:
- Use short, plain sentences. Avoid idioms and slang (for example "looks good", "advance the clock").
- Use the same word for the same thing every time in a reply.
- Put commands, paths, identifiers, and code in backticks or code blocks so the translator keeps them as is.

Exceptions: when the user asks you to draft text in a specific language (PR descriptions, issue bodies, review comments, chat messages, documents), write that text in the requested language, following the user's existing writing rules for it.
The user may write in any language. Read it normally.
