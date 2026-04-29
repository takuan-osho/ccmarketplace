# Sequential Workflow

## Overview

Agents execute **one after another**, with each agent receiving the previous agent's findings. This builds comprehensive analysis iteratively.

## Diagram

```
┌─────────────┐
│    Task     │
│  (Input)    │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│      Agent A        │
│     (Codex)         │
│  Persona: Architect │
└──────────┬──────────┘
           │
           │ Result A
           ▼
┌─────────────────────────────────────┐
│            Agent B                  │
│           (Gemini)                  │
│    Persona: Security Researcher     │
│                                     │
│  Input: Task + Result A             │
│  "Building on the Architect's       │
│   analysis, evaluate security..."   │
└──────────────┬──────────────────────┘
               │
               │ Result B (includes A's context)
               ▼
┌─────────────────────────────────────┐
│            Agent C                  │
│           (Claude)                  │
│      Persona: QA Engineer           │
│                                     │
│  Input: Task + Result A + Result B  │
│  "Given the architecture and        │
│   security analysis, design tests..." │
└──────────────┬──────────────────────┘
               │
               │ Final Result
               ▼
┌─────────────────────────────────────┐
│         Final Report                │
│  (Cumulative analysis from all)     │
└─────────────────────────────────────┘
```

## When to Use

- **Dependency between analyses**: Security review needs architecture understanding
- **Building comprehensive picture**: Each perspective adds to the previous
- **Expert consultation chain**: Like getting referred specialist opinions
- **Refinement process**: Each agent refines the previous analysis

## Execution Steps

### Step 1: Define Agent Order

Consider dependencies:
```
Recommended Orders:

Review Chain:
  Architect → Security → Performance → QA

Implementation Review:
  Analyzer → Code Reviewer → Documentarian

Bug Investigation:
  Analyzer → Domain Expert → QA
```

### Step 2: Execute First Agent

```bash
# Agent A: Codex as Architect
RESULT_A=$(codex --model gpt-5.2-codex "
You are a Senior Software Architect.
Analyze the following code for design and structure:

[CODE_CONTENT]

Provide findings with severity levels.
")
```

### Step 3: Execute Subsequent Agents

```bash
# Agent B: Gemini as Security (with Agent A's results)
RESULT_B=$(gemini -p "
You are a Security Researcher.

Previous Analysis (Architect):
$RESULT_A

Building on the Architect's analysis, perform a security review:
- Consider the architectural decisions when evaluating security
- Identify vulnerabilities in the identified modules
- Pay special attention to the interfaces highlighted

[CODE_CONTENT]
" -m gemini-3-flash-preview)
```

```bash
# Agent C: Claude as QA (with both results)
# Use Task tool
"You are a QA Engineer.

Previous Analyses:
Architect: [RESULT_A]
Security: [RESULT_B]

Based on the architecture and security findings:
1. Design test cases that cover the identified issues
2. Create security tests for the vulnerabilities found
3. Suggest integration tests for the module boundaries

[CODE_CONTENT]"
```

### Step 4: Compile Final Report

The final agent's output naturally includes context from all previous agents.

## Prompt Template for Chained Agents

```
You are a [PERSONA].

## Previous Analysis Summary
[PREVIOUS_AGENT_PERSONA]: [KEY_FINDINGS_SUMMARY]

## Your Task
Building on the previous analysis:
1. [SPECIFIC_FOCUS_AREA_1]
2. [SPECIFIC_FOCUS_AREA_2]
3. Address any concerns raised by [PREVIOUS_AGENT]

## Code to Analyze
[CODE_CONTENT]

## Output Format
1. Summary of how your analysis relates to previous findings
2. New findings from your perspective
3. Recommendations (considering all analyses)
```

## Best Practices

1. **Summarize previous results** - Don't pass full output, extract key points
2. **Reference previous findings** - Ask agent to build on specific points
3. **Order by dependency** - Architecture before security before testing
4. **Limit chain length** - 3-4 agents max to avoid context dilution
5. **Final agent synthesizes** - Last agent should tie everything together

## Example: Security-Focused Review

```
Task: Review authentication module

Chain:
1. Architect (Codex) → Understand structure
2. Security (Gemini) → Find vulnerabilities (using architecture context)
3. QA (Claude) → Design security tests (using both contexts)

Agent 1 (Architect) finds:
- Auth module has 3 components: session, token, password
- Password component directly accesses database
- Token component has complex refresh logic

Agent 2 (Security) knows to:
- Focus on password component's DB access (injection risk)
- Examine token refresh for security issues
- Check session management based on architecture

Agent 2 finds:
- SQL injection in password component (predicted from architecture)
- Token refresh has race condition
- Session fixation possible

Agent 3 (QA) designs:
- SQL injection test cases for password component
- Concurrent token refresh tests
- Session fixation attack tests

Final output: Comprehensive test suite addressing architectural concerns
```

## Handling Disagreements

If later agents disagree with earlier findings:

```
Agent B: "I disagree with Agent A's assessment that the
         module boundaries are well-defined. From a security
         perspective, the auth module has too much access."

Resolution:
1. Note the disagreement in report
2. If critical, use AskUserTool to resolve
3. Both perspectives may be valid from different viewpoints
```
