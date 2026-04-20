---
name: interview
description: Conduct structured interviews to clarify scope, surface constraints, and reach a "do / don't do / done" agreement before starting non-trivial work. Use when receiving an ambiguous request, a vague task description, or before entering plan mode for any non-trivial implementation. Skip for one-line concrete fixes ("rename foo to bar") or single-fact questions. Supports requirements definition, debugging investigation, architecture review, security review, documentation creation, and general exploration.
---

# Interview

Act as a clarification interviewer that drills into a request until "do", "don't do", and "done" are unambiguous. Ambiguous specs cost rework; ten minutes of interview saves hours of guesswork and prevents code from being written in the wrong direction.

## Decide whether to interview

**Use this skill when:**

- A request lacks a clear scope ("I want to add auth", "investigate the 504 errors")
- The task is large enough that approach matters (multi-file change, design decision, architectural choice)
- You suspect hidden constraints, dependencies, or stakeholder expectations
- Before entering plan mode for any non-trivial implementation

**Skip this skill (act directly) when:**

- A one-line concrete fix is requested ("rename foo to bar in baz.ts")
- A single-fact question is answerable from the codebase
- The user has already specified scope, constraints, and acceptance criteria

If unsure, prefer interviewing — the cost of one extra clarification turn is far smaller than the cost of building the wrong thing.

## Workflow

The interview is a **single iterative loop, not numbered phases**. Walk the decision tree branch by branch, **one question at a time**, until every branch converges on a decision (accepted, rejected, or explicitly deferred). The only "phase" header below is `Output`, which marks the moment you stop interviewing and produce the summary.

### Question style

| Rule | Why it matters |
|------|----------------|
| **One question per turn** | Multiple questions overwhelm and produce shallow, batched answers |
| **Attach a recommended answer to every question** | User can confirm with "yes" and the conversation advances quickly |
| **No upper bound on question count** | Stop when branches converge, not at a preset stage |
| **Skip questions already answered by prior context** | Re-asking signals you weren't listening |

### Question template

```
Q: <single specific question>
Recommended: <a concrete default with a one-line rationale>
```

The recommended answer should reflect the most common pattern, the safest choice, or the option suggested by codebase/web evidence you have already gathered. The user either accepts ("yes" / "go with that") or pushes back with their own answer.

**Notation note**: The `Recommended: …` line is the canonical authoring format used in this skill's prose and examples. When the question is rendered through `AskUserQuestion`, the same recommendation is *displayed* as the first option labeled `(Recommended)` — they are the same content, just formatted for the channel.

### Branch order

Resolve dependencies first (answers that constrain later questions), then breadth, then depth:

1. **Goal / outcome** — what does success look like?
2. **Stakeholders / users** — who is affected? *(Skip if the Goal answer already pins down a single user/role unambiguously, e.g. "reduce signup drop-off" implies end users.)*
3. **Interview type** (see table below) — drives the subsequent question framing
4. **Scope boundaries** — what is explicitly in / out
5. **Constraints** — technical, business, timeline
6. **Acceptance criteria** — observable "done" condition

If the user expands or pivots the type mid-interview ("actually, also include the architecture decision"), do not restart. Treat the new branch as additive: append it to the open-branches list and continue the current branch first, then address the new one before convergence.

### Interview types

The user can name a type explicitly, or you can infer it from the request. The type drives which questions to prioritize.

| Type | Use when | Drives questions about |
|------|----------|----------------------|
| Requirements | New feature, spec, API design | Behavior, edge cases, validation, error UX |
| Investigation | Bug analysis, incident, performance issue | Symptoms, repro steps, hypotheses, blast radius |
| Architecture | Design review, technology selection, refactor | Trade-offs, constraints, integration points |
| Security | Audit, threat model, vulnerability scan | Assets, threats, controls, compliance scope |
| Documentation | Report, runbook, onboarding doc | Audience, depth, format, distribution |
| General | Open exploration, brainstorm | Whatever surfaces |

### On-demand exploration

Do **not** batch-explore the codebase or web upfront. Reach for these tools only when an answer would shape the very next question:

- **Codebase** — `Glob` / `Grep` / `Read`, or `Agent` with the `Explore` subagent for surveys spanning many files
- **Existing docs** — `Read` files the user already referenced
- **Web** — `WebSearch` for library behavior, best practices, or security advisories

Weave findings back into the next question:

> "I read `src/auth/login.ts` — it uses NextAuth with the credentials provider. Should we extend that, or replace it for the new OAuth flow?"

If exploration fails or the target cannot be located, skip it and ask the user directly rather than guessing.

### Convergence

A branch is converged when the user has either:

- Accepted a concrete answer (the recommended option or their own)
- Explicitly deferred to a separate decision (recorded as an "open question")

Stop interviewing when **every** active branch is converged or deferred. Then move to the Output stage.

## Output

Generate a single Markdown summary. Default to English; match the user's language if they were typing in Japanese or another language.

```markdown
### Work Summary: <topic>

**Goal**: <1-2 sentences capturing why this matters>

**Type**: <one of the interview types>

**In scope**:
- <bullet>
- <bullet>

**Out of scope**:
- <bullet>

**Acceptance criteria / Done when**:
- <observable, testable condition>
- <another condition>

**Open questions / Deferred**:
- [ ] <unresolved item>

**Constraints**:
- <technical / business / timeline>

**References**:
- `<file path>` / <link> — <one-line note>
```

After the summary, surface next-step options:

- "If you want to start building, I can enter plan mode."
- "If we should drill into any item further, name which."

## Edge cases

| Situation | Handling |
|-----------|----------|
| User answers "I don't know" / "you decide" | Sequential, do not skip steps: **(1)** present **2 concrete options** with a one-line rationale each and re-ask; **(2)** if the user still defers or stays silent, propose a single recommended path and ask "OK to proceed with X?"; **(3)** if the user accepts, record the choice and tag it `[auto-decided]` in the Output summary so they can revisit it later. Never decide silently. |
| Scope is too large for one interview | Propose splitting: "This is large; let's start with sub-area A. We can re-interview for B and C later." Then continue interviewing on the chosen sub-scope |
| User contradicts a prior answer | Reflect both versions: "Earlier you said X; now Y. Which is current?" Update earlier decisions explicitly so the summary stays consistent |
| No reasonable recommendation exists | Say so: "I don't have a strong recommendation — what matters most here: speed, cost, or correctness?" Frame the trade-off rather than guessing |
| User wants to skip the interview mid-way | Honor it. Emit whatever Output summary you have so far, marking remaining branches as open questions |
| User pushes back on the recommended answer | Treat the rejection as new information. Confirm their preferred answer and move on; do not argue |

## Example

```text
User: "I want to add an export feature for teams"

Q1: What is the export for — audit, data migration, or reporting?
Recommended: Audit is the most common driver for "team export". OK?
A1: Audit.

[Reads src/teams/ — finds Team model with members, permissions, activity log]

Q2: I see Team has members, permissions, and activity logs. Which fields
should the export include?
Recommended: For audit, members + permissions is the standard pair.
Activity logs are usually exported separately.
A2: Members and permissions.

Q3: Format? CSV is the audit default; JSON is friendlier for tooling.
Recommended: CSV.
A3: CSV.

Q4: Who can run the export? Admin-only is safer because it includes
permission data.
Recommended: Admin-only.
A4: Yes.

Q5: Anything explicitly out of scope — PDF, scheduling, encryption-at-rest?
Recommended: Out of scope for v1; we can flag follow-ups separately.
A5: All out of scope.

Q6: "Done" when an admin can download a CSV containing members and
permissions for a team. Correct?
A6: Yes.

[Output: Work Summary]
```

## Environment notes

### Claude Code

Use `AskUserQuestion` when the question has 2–4 concrete options. Label the recommended option `"(Recommended)"` and place it first. For open-ended answers, ask in plain text — `AskUserQuestion` is not the right shape for free-form input.

### Codex / Gemini CLI / plain terminal

Present the question and the recommended answer in plain text. Number multiple-choice options manually:

```
Q: Which export format?
1. CSV (Recommended) — standard for audit exports
2. JSON
3. Other (please describe)
```

### Auto Mode

If the orchestrator is in auto mode (continuous, autonomous execution), **do not block** waiting for user input. Apply the recommended answer to each question, mark each auto-applied choice as `[auto]` in the Output summary, and surface the chosen path so the user can correct it after the run completes. Continue interviewing only if the user joins the session interactively.

**Simulation / dry-run override**: If the caller (user or another skill) explicitly asks you to *simulate* the interview, *render the dialogue*, or *show what you would ask*, the simulation request takes priority over Auto Mode — produce the Q&A turns rather than auto-deciding. Auto Mode only governs *real* user-facing runs where no human is present to answer.

## Guidelines

- **Match the user's language** in the summary; otherwise default to English
- **Capture rationale**, not only decisions, so re-reading the summary still explains the *why*
- **Surface gaps as open questions** rather than guessing
- **Refer to actual code or links** when possible — concrete beats abstract
- **One question per turn even when you have many** — list the others as a hidden TODO and address them after the current branch converges
