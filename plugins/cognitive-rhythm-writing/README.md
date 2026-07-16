# Cognitive Rhythm Writing Skill

A skill for designing pacing in Japanese expository writing, treating rhythm not as decoration but as deliberate switching of the reader's cognitive modes.

## Overview

This skill defines norms for making dense explanatory prose readable as a narrative. It covers:

- **Core principles** - Rhythm as cognitive-mode switching (observe, waver, assert, re-observe) and keeping at least one unresolved tension open
- **Sentence beat** - Alternating assertion and hesitation; the "plant, flow, stop" paragraph beat
- **Paragraph density waves** - Interleaving dense and sparse paragraphs, switching viewpoint distance
- **Openings and section entries** - Creating tension in the first few sentences instead of agenda-style previews
- **Landing enumerations** - Grounding each listed item back into a concrete scene
- **Telling slack from filler** - The one-axis test: does the sentence update the situation, or the document itself?
- **Post-draft inspection** - A mechanical checklist for topic, leakage, tension ledger, beat, and boundaries

Use it when writing chapters, articles, or explanatory documents meant to be read as prose, or when diagnosing writing that is dense but flat.

## Dependency

This skill reads the `japanese-tech-writing` skill before working. Install the [japanese-tech-writing](../japanese-tech-writing/) plugin from this marketplace alongside this one.

## Usage

The skill triggers automatically when generating or revising Japanese expository prose that should read with rhythm. You can also invoke it explicitly:

```
/cognitive-rhythm-writing
```

## Source and License

The skill content is imported from [k16shikano's gist](https://gist.github.com/k16shikano/eb2929f13ed19c97188393d297be8432) by Keiichiro Shikano ([@k16shikano](https://github.com/k16shikano)), with one change: the companion-skill reference was converted from a relative path to a skill-name reference so it resolves after plugin installation.

The original work is released into the public domain under [the Unlicense](https://gist.github.com/k16shikano/67625f2a7d96e3bbdfae8d571a936063). See [LICENSE](LICENSE).
