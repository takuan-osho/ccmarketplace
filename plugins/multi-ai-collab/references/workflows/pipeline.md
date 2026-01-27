# Pipeline Workflow

## Overview

A structured flow where different agents handle different **stages** of development: Implementation → Testing → Review. This separates concerns and reduces bias.

## Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PIPELINE STAGES                              │
└─────────────────────────────────────────────────────────────────────┘

     Stage 1              Stage 2              Stage 3
   IMPLEMENT              TEST                REVIEW
       │                    │                    │
       ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Implementer │      │   Tester    │      │  Reviewer   │
│  (Claude)   │─────▶│  (Codex)    │─────▶│  (Gemini)   │
└─────────────┘      └─────────────┘      └─────────────┘
       │                    │                    │
       │                    │                    │
       ▼                    ▼                    ▼
   Code Output         Test Suite          Review Report
       │                    │                    │
       │                    │                    │
       └────────────────────┴────────────────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   Quality-Assured   │
                 │       Output        │
                 └─────────────────────┘


     ┌──────────────────────────────────────────────────┐
     │              FEEDBACK LOOP                       │
     │                                                  │
     │  Review Findings ──────────────────────┐        │
     │         │                              │        │
     │         ▼                              ▼        │
     │  ┌─────────────┐              ┌─────────────┐   │
     │  │ Implementer │◀─────────────│   Tester    │   │
     │  │  (Fixes)    │   Test       │  (Updates)  │   │
     │  └─────────────┘   Failures   └─────────────┘   │
     │                                                  │
     └──────────────────────────────────────────────────┘
```

## When to Use

- **TDD-style development**: Write tests before or alongside implementation
- **Quality gates**: Enforce testing and review at each stage
- **Separation of concerns**: Different "people" implement and test
- **Bias reduction**: Testers don't know implementation details

## Stage Definitions

### Stage 1: Implementation

**Agent**: Primary (Orchestrator) or designated Implementer
**Output**: Working code

```
Responsibilities:
- Implement the requested feature/fix
- Follow coding standards
- Basic error handling
- Initial inline comments
```

### Stage 2: Testing

**Agent**: Separate from Implementer (e.g., Codex)
**Input**: Implementation code
**Output**: Test suite

```
Responsibilities:
- Design comprehensive test cases
- Write unit tests
- Write integration tests
- Identify edge cases
- Run tests and report results
```

### Stage 3: Review

**Agent**: Third agent (e.g., Gemini)
**Input**: Implementation + Tests
**Output**: Review report + Approval/Changes

```
Responsibilities:
- Review code quality
- Review test coverage
- Security assessment
- Performance check
- Final recommendations
```

## Execution Steps

### Step 1: Implementation Phase

```
Orchestrator (or designated agent) implements:

Task: "Implement user registration with email verification"

Output:
- src/services/registration.ts
- src/services/emailVerification.ts
- src/types/user.ts
```

### Step 2: Testing Phase

```bash
# Codex as Tester (QA persona)
codex --model gpt-5.2-codex "
You are a QA Engineer. You did NOT write this code.

Your task: Create a comprehensive test suite for this implementation.

## Implementation to Test
[IMPLEMENTATION_CODE]

## Requirements
[ORIGINAL_REQUIREMENTS]

## Testing Guidelines
1. Do NOT assume you know implementation details
2. Test based on requirements and public API
3. Include:
   - Happy path tests
   - Error cases
   - Edge cases
   - Security tests (input validation)
   - Integration tests

## Output
1. Test file(s) with complete test cases
2. Test coverage analysis
3. Any issues found during test design
"
```

### Step 3: Review Phase

```bash
# Gemini as Reviewer (multiple personas)
gemini -p "
You are a Senior Code Reviewer performing a final quality gate review.

## Implementation
[IMPLEMENTATION_CODE]

## Test Suite
[TEST_CODE]

## Test Results
[TEST_RUN_OUTPUT]

## Review Checklist
1. Code Quality
   - Readability
   - Maintainability
   - Error handling

2. Test Quality
   - Coverage adequacy
   - Test case design
   - Missing scenarios

3. Security
   - Input validation
   - Authentication/authorization
   - Data protection

4. Performance
   - Obvious inefficiencies
   - Scalability concerns

## Output
1. Approval status: Approve / Request Changes
2. Required changes (if any)
3. Suggestions (optional improvements)
4. Security/Performance flags
" -m gemini-2.5-pro
```

### Step 4: Feedback Loop (if needed)

```
If Review requests changes:
1. Implementer addresses required changes
2. Tester updates/adds tests
3. Re-run review phase

Continue until approved or user intervention needed.
```

## Prompt Templates

### Tester Prompt (Blind Testing)

```
You are a QA Engineer testing code you did not write.

IMPORTANT: Test based on REQUIREMENTS, not implementation details.
You should discover edge cases through systematic testing,
not by reading the implementation.

Requirements:
[REQUIREMENTS]

Public API to test:
[FUNCTION_SIGNATURES]

Write tests that:
1. Verify all requirements are met
2. Test boundary conditions
3. Test error handling
4. Test security aspects
```

### Reviewer Prompt (Final Gate)

```
You are performing a final quality gate review.

You must evaluate:
1. Does the implementation meet requirements?
2. Are the tests adequate?
3. Are there security concerns?
4. Are there performance issues?

Approval Criteria:
- All requirements addressed
- Test coverage > 80%
- No critical security issues
- No obvious performance problems

Your decision: APPROVE or REQUEST_CHANGES
```

## Best Practices

1. **Keep implementer and tester separate** - Reduces confirmation bias
2. **Tester should not see implementation first** - Test from requirements
3. **Reviewer sees everything** - Full context for final decision
4. **Limit feedback loops** - Max 2-3 iterations before human intervention
5. **Document rejections** - Track why reviews fail for improvement

## Example: Feature Development Pipeline

```
Feature: Add password reset functionality

Stage 1 - Implementation (Claude):
- Implements reset token generation
- Email sending
- Token validation
- Password update

Stage 2 - Testing (Codex):
- Tests valid reset flow
- Tests expired token
- Tests invalid token
- Tests rate limiting
- Discovers: No check for weak passwords!

Stage 3 - Review (Gemini):
- Reviews implementation: Good structure
- Reviews tests: Comprehensive
- Security check: Flags no HTTPS requirement
- Performance: OK
- Decision: REQUEST_CHANGES
  - Add weak password check
  - Enforce HTTPS for reset endpoint

Feedback Loop:
- Claude adds password strength validation
- Codex adds password strength tests
- Gemini re-reviews: APPROVE
```

## Pipeline Variants

### Test-First Pipeline (TDD)

```
Tester → Implementer → Reviewer
  │           │            │
  │           │            │
  Tests     Code that    Verify
  first     passes       both
            tests
```

### Review-Driven Pipeline

```
Reviewer (spec) → Implementer → Tester → Reviewer (final)
      │                │            │           │
      │                │            │           │
   Design          Implement     Test      Approve
   review          to spec       impl
```
