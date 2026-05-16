---
name: interview
description: Conduct iterative interviews to clarify scope, surface constraints, and reach a "do / don't do / done" agreement before starting non-trivial work. Use when receiving an ambiguous request, a vague task description, or before entering plan mode for any non-trivial implementation. Skip for one-line concrete fixes ("rename foo to bar"), single-fact questions, or when scope, constraints, and acceptance criteria are already specified. Supports requirements definition, debugging investigation, architecture review, security review, documentation creation, and general exploration.
---

Interview the user relentlessly until "do", "don't do", and "done" are unambiguous. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.
If a question can be answered by exploring the codebase, explore the codebase instead.
When the user signals convergence, output a Markdown summary with **Do / Don't do / Done** sections.

## Output

When the interview converges, emit a single Markdown block (match the user's language; default to English):

```markdown
### Do
- <bullet>

### Don't do
- <bullet>

### Done when
- <observable, testable condition>
```

Mark any auto-applied recommendations with `[auto]` inline (e.g., `- Use bcrypt [auto]`).

## Edge cases

| Situation | Handling |
|-----------|----------|
| User answers "I don't know" / "you decide" | Sequential: (1) present 2 concrete options with one-line rationale each; (2) if still deferred, propose a single recommended path and ask "OK to proceed with X?"; (3) if accepted, record with `[auto]`. Never decide silently. |
| User contradicts a prior answer | Reflect both versions: "Earlier you said X; now Y. Which is current?" Update the earlier decision so the summary stays consistent. |
| User wants to skip mid-way | Honor it. Emit the partial summary; list unresolved branches as bullets in an extra `### Open questions` section appended after `### Done when`. |

## Environment notes

### Claude Code
Use `AskUserQuestion` when the question has 2-4 concrete options. Label the recommended option `(Recommended)` and place it first. For open-ended answers, ask in plain text.

### Codex / Gemini CLI / plain terminal
Number multiple-choice options manually:

```
Q: Which export format?
1. CSV (Recommended) — standard for audit exports
2. JSON
3. Other (please describe)
```

### Auto Mode
If the orchestrator is in auto mode (continuous, autonomous execution), do not block waiting for user input. Apply the recommended answer to each question, mark each auto-applied choice with `[auto]` inline in the output, and surface the chosen path so the user can correct it after the run completes.

**Simulation override**: If the caller explicitly asks you to simulate the interview or render the dialogue, produce the Q&A turns rather than auto-deciding.

## Example

```text
User: "I want to add an export feature for teams"

Q1: What is the export for — audit, data migration, or reporting?
Recommended: Audit. OK?
A1: Audit.

[Reads src/teams/ — finds members, permissions, activity log]

Q2: Format and access? Recommend CSV, admin-only (audit default).
A2: Yes.

→ Output:
### Do
- Admin can download CSV (members + permissions) for a team
### Don't do
- PDF, scheduling, encryption-at-rest (v1 out of scope)
### Done when
- An admin can download a CSV with members and permissions
```
