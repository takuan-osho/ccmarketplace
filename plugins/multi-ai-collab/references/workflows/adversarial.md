# Adversarial Workflow

## Overview

Agents are assigned **opposing roles** and tasked with **challenging each other's findings**. This stress-tests analyses and surfaces hidden issues through debate.

## Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ADVERSARIAL DEBATE                             │
└─────────────────────────────────────────────────────────────────────┘

                         ┌─────────────┐
                         │    Task     │
                         └──────┬──────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
       ┌─────────────────┐             ┌─────────────────┐
       │    PROPONENT    │             │    OPPONENT     │
       │    (Codex)      │             │    (Gemini)     │
       │                 │             │                 │
       │  Makes claims   │             │  Challenges     │
       │  Defends design │◀───────────▶│  Finds flaws    │
       │  Proposes       │   DEBATE    │  Questions      │
       │  solutions      │             │  assumptions    │
       └────────┬────────┘             └────────┬────────┘
                │                               │
                │    Round 1: Initial Claims    │
                │◀─────────────────────────────▶│
                │                               │
                │    Round 2: Rebuttals         │
                │◀─────────────────────────────▶│
                │                               │
                │    Round 3: Final Arguments   │
                │◀─────────────────────────────▶│
                │                               │
                └───────────────┬───────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │     ADJUDICATOR       │
                    │   (Claude/User)       │
                    │                       │
                    │  • Evaluates debate   │
                    │  • Identifies winner  │
                    │  • Synthesizes truth  │
                    │  • Makes decision     │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    FINAL DECISION     │
                    │  (with rationale)     │
                    └───────────────────────┘
```

## When to Use

- **Critical design decisions**: Major architectural choices
- **Risk assessment**: Security-critical features
- **Trade-off analysis**: Performance vs. maintainability
- **Assumption validation**: Challenging accepted beliefs
- **Pre-mortem analysis**: What could go wrong?

## Role Definitions

### Proponent (Advocate)

```
Responsibilities:
- Present and defend the proposed approach
- Highlight benefits and strengths
- Provide evidence and examples
- Address criticisms with rebuttals
- Propose mitigations for valid concerns
```

### Opponent (Critic)

```
Responsibilities:
- Challenge all assumptions
- Find weaknesses and risks
- Play devil's advocate
- Propose alternative approaches
- Identify edge cases that break the proposal
```

### Adjudicator (Judge)

```
Responsibilities:
- Remain neutral
- Evaluate arguments objectively
- Identify valid points from both sides
- Synthesize a balanced conclusion
- Make final decision with rationale
```

## Execution Steps

### Step 1: Define the Debate Topic

```
Topic Examples:
- "Should we use microservices or monolith?"
- "Is this authentication implementation secure?"
- "Should we prioritize performance or readability?"
- "Is this refactoring necessary?"
```

### Step 2: Round 1 - Initial Claims

```bash
# Proponent (Codex) - Present the proposal
codex --model gpt-5.2-codex "
You are the PROPONENT in a technical debate.

Topic: [DEBATE_TOPIC]
Context: [CODE_OR_DESIGN]

Your task:
1. Present a clear position
2. List 3-5 key arguments supporting your position
3. Provide evidence (code examples, benchmarks, references)
4. Anticipate potential criticisms

Be confident but fair. Acknowledge limitations where they exist.
"
```

```bash
# Opponent (Gemini) - Challenge the proposal
gemini -p "
You are the OPPONENT in a technical debate.

Topic: [DEBATE_TOPIC]
Context: [CODE_OR_DESIGN]
Proponent's Position: [PROPONENT_ROUND_1]

Your task:
1. Challenge the proponent's key arguments
2. Identify weaknesses, risks, and assumptions
3. Propose alternative approaches
4. Find edge cases that break the proposal

Be rigorous but constructive. Aim to improve, not just criticize.
" -m gemini-2.5-pro
```

### Step 3: Round 2 - Rebuttals

```bash
# Proponent rebuts Opponent's challenges
codex --model gpt-5.2-codex "
You are the PROPONENT continuing the debate.

Your original position: [PROPONENT_ROUND_1]
Opponent's challenges: [OPPONENT_ROUND_1]

Respond to each challenge:
1. Acknowledge valid criticisms
2. Defend against unfair criticisms
3. Propose mitigations for valid concerns
4. Strengthen your position with additional evidence
"
```

```bash
# Opponent responds to rebuttals
gemini -p "
You are the OPPONENT continuing the debate.

Original challenge: [OPPONENT_ROUND_1]
Proponent's rebuttal: [PROPONENT_ROUND_2]

Respond:
1. Accept valid defenses
2. Press on unaddressed concerns
3. Identify any new weaknesses in rebuttals
4. Summarize remaining critical issues
" -m gemini-2.5-pro
```

### Step 4: Final Arguments

Both sides present closing arguments summarizing their strongest points.

### Step 5: Adjudication

```
# Adjudicator (Claude sub-agent or User via AskUserTool)

"You are the neutral ADJUDICATOR.

Debate Topic: [TOPIC]

Proponent's Arguments:
[PROPONENT_SUMMARY]

Opponent's Arguments:
[OPPONENT_SUMMARY]

Evaluate objectively:
1. Which arguments were well-supported?
2. Which criticisms were valid?
3. What is the most reasonable conclusion?
4. What risks should be mitigated regardless?

Provide:
- Winner (Proponent/Opponent/Tie)
- Rationale
- Synthesized recommendation
- Action items"
```

## Debate Templates

### Security Debate

```
Proponent: "This implementation is secure"
- Lists security measures taken
- References best practices followed

Opponent: "This implementation has vulnerabilities"
- Attempts to find attack vectors
- Challenges assumptions about threats
- Proposes attack scenarios
```

### Architecture Debate

```
Proponent: "We should use [Architecture A]"
- Scalability benefits
- Team familiarity
- Cost efficiency

Opponent: "We should use [Architecture B]"
- Better maintainability
- Future flexibility
- Industry trend alignment
```

### Refactoring Debate

```
Proponent: "This refactoring is worth the effort"
- Technical debt reduction
- Improved testability
- Faster future development

Opponent: "This refactoring is not justified"
- Risk of introducing bugs
- Time better spent on features
- Current code is "good enough"
```

## Best Practices

1. **Assign different AI models** - Avoids model-specific biases
2. **Provide equal context** - Fair debate requires equal information
3. **Limit rounds** - 2-3 rounds prevents endless debate
4. **Neutral adjudicator** - User or third AI should decide
5. **Document the debate** - Valuable for future reference
6. **Accept valid criticisms** - Proponent should concede good points

## Example: Authentication Security Debate

```
Topic: "Is the JWT implementation secure?"

Round 1:
Proponent (Codex):
- Token signing with RS256 ✓
- Short expiration (15 min) ✓
- Refresh token rotation ✓
- Stored in httpOnly cookie ✓

Opponent (Gemini):
- No token blacklist for logout ✗
- Refresh token stored in localStorage (XSS risk) ✗
- No rate limiting on token endpoint ✗
- Missing CSRF protection ✗

Round 2:
Proponent:
- Logout: Accepts criticism, proposes Redis blacklist
- localStorage: Defends as necessary for SPA, proposes mitigation
- Rate limiting: Accepts, will add
- CSRF: Cookie has SameSite=Strict

Opponent:
- Redis blacklist: Acceptable solution
- localStorage: Still risky, recommends BFF pattern
- CSRF: SameSite not sufficient for all browsers

Adjudication:
Winner: Opponent (valid security concerns raised)

Recommendation:
1. [Must] Add Redis token blacklist
2. [Must] Add rate limiting
3. [Should] Consider BFF pattern for token storage
4. [Could] Add explicit CSRF token for legacy browser support

Action Items:
- Implement blacklist before release
- Add rate limiting before release
- Evaluate BFF pattern for v2
```

## Handling Stalemates

If debate reaches impasse:

```
Options:
1. Bring in third agent as tie-breaker
2. Use AskUserTool for human decision
3. Propose compromise solution
4. Defer decision with documented trade-offs
```
