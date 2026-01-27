# Parallel Workflow (Cross-Review)

## Overview

All agents work **independently** on the same task, then results are **synthesized** at the end. This provides unbiased, multi-perspective analysis.

## Diagram

```
                    ┌─────────────┐
                    │    Task     │
                    │  (Input)    │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   Agent A   │ │   Agent B   │ │   Agent C   │
    │  (Codex)    │ │  (Gemini)   │ │  (Claude)   │
    │             │ │             │ │             │
    │  Persona:   │ │  Persona:   │ │  Persona:   │
    │  Architect  │ │  Security   │ │  QA         │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           ▼               ▼               ▼
      Result A        Result B        Result C
           │               │               │
           └───────────────┼───────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   SYNTHESIS     │
                  │  (Orchestrator) │
                  ├─────────────────┤
                  │ • Merge results │
                  │ • Find consensus│
                  │ • Identify gaps │
                  │ • Resolve       │
                  │   conflicts     │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Final Report   │
                  └─────────────────┘
```

## When to Use

- **Code Review**: Get multiple independent perspectives
- **Security Audit**: Different security experts check the same code
- **Architecture Review**: Multiple architects assess design
- **Pre-production Check**: Comprehensive validation before release

## Execution Steps

### Step 1: Prepare Context

```
Orchestrator:
1. Identify target files
2. Prepare code snippets
3. Define the review scope
```

### Step 2: Launch Parallel Agents

```bash
# Launch all agents simultaneously (or in quick succession)

# Agent A: Codex as Architect
codex --model gpt-5.2-codex "
[ARCHITECT PERSONA PROMPT]
[CODE_CONTENT]
"

# Agent B: Gemini as Security Researcher
gemini -p "
[SECURITY PERSONA PROMPT]
[CODE_CONTENT]
" -m gemini-3-flash-preview

# Agent C: Claude as QA Engineer
# Use Task tool with subagent_type: general-purpose
```

### Step 3: Collect Results

```
Orchestrator:
1. Wait for all agents to complete
2. Parse each agent's output
3. Normalize findings format
```

### Step 4: Synthesize

```
Synthesis Process:
1. Categorize all findings
2. Identify overlapping findings (consensus)
3. Identify unique findings from each agent
4. Flag contradictory findings for user decision
5. Prioritize by severity and consensus
```

## Synthesis Template

```markdown
## Synthesis Report

### Consensus Findings (All Agents Agree)
| Finding | Agents | Severity | Action |
|---------|--------|----------|--------|
| SQL Injection in users.ts | A, B, C | Critical | Fix immediately |

### Unique Findings (Single Agent)
| Finding | Agent | Severity | Confidence | Action |
|---------|-------|----------|------------|--------|
| Memory leak in cache | A (Architect) | Medium | High | Investigate |

### Contradictory Findings (Agents Disagree)
| Topic | Agent A | Agent B | Agent C | User Decision |
|-------|---------|---------|---------|---------------|
| Error handling approach | Use exceptions | Use Result type | No preference | Required |
```

## Best Practices

1. **Give same context to all agents** - Ensure fairness
2. **Don't share results between agents** - Keep perspectives independent
3. **Use different AI models** - Avoid model-specific blind spots
4. **Weight consensus higher** - Multiple agents agreeing increases confidence
5. **Flag unique findings for review** - Don't dismiss, but verify

## Example: Cross-Review Pull Request

```
Task: Review PR #123 - Add payment processing

Team:
- Codex → Architect: Check design
- Gemini → Security: Check vulnerabilities
- Claude → QA: Check test coverage

Execution:
1. All three analyze the same diff
2. Orchestrator collects results
3. Synthesis:
   - All agree: Input validation needed
   - Architect only: Suggests refactoring
   - Security only: Finds CSRF vulnerability
   - QA only: Missing edge case tests

Final Report:
- P0: Add CSRF protection (Security)
- P0: Add input validation (Consensus)
- P1: Add edge case tests (QA)
- P2: Consider refactoring (Architect)
```
