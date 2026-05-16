# Interview Skill

A skill for conducting iterative interviews that clarify scope, constraints, and acceptance criteria before non-trivial work starts.

## Overview

This skill helps reduce ambiguity before implementation by walking the user through the decision tree one branch at a time. It follows the `grill-me` pattern: ask one specific question, provide a recommended answer, and keep going until **Do / Don't do / Done** are unambiguous.

Use it for vague requests, ambiguous project goals, architecture choices, debugging investigations, documentation planning, or any task where building immediately would risk solving the wrong problem.

Skip it for one-line concrete fixes, single-fact questions, or requests that already include scope, constraints, and acceptance criteria.

## Usage

```
/interview [topic]
```

Examples:
```
/interview Add user authentication feature
/interview Investigate 504 errors in production
/interview Review database schema for scalability
```

## Workflow

1. Ask one focused question at a time.
2. Attach a recommended answer to each question.
3. If a question can be answered by exploring the codebase, inspect the code instead of asking the user.
4. Continue until every active branch is accepted, rejected, or explicitly deferred.
5. Output a concise Markdown summary with **Do**, **Don't do**, and **Done when** sections.

## Features

- **One-question loop** - Avoids batched questions and shallow answers
- **Recommended defaults** - Lets the user confirm quickly while still surfacing trade-offs
- **Codebase-aware clarification** - Uses local evidence when the repository can answer the next question
- **Environment-aware input** - Uses AskUserQuestion in Claude Code when options fit, and numbered options elsewhere
- **Auto Mode support** - Applies recommended answers without blocking during autonomous runs, marking them with `[auto]`
- **Focused output** - Produces a small **Do / Don't do / Done when** summary instead of a long requirements document

## Output Format

```markdown
### Do
- <what should be done>

### Don't do
- <what is out of scope>

### Done when
- <observable completion condition>
```

## Inspiration

This skill is based on [taichi/interview custom command](https://gist.github.com/taichi/8419da7e2b20685db8d5f91f73fc3b1d), adapted toward the local `grill-me` skill's iterative questioning style.
