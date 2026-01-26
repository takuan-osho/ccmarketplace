# Usage Examples

This document provides complete, end-to-end examples of using the Multi-AI Collaboration skill.

---

## Example 1: Cross-Review a Pull Request

### Scenario

A developer has submitted a PR adding authentication functionality. We want multiple AI agents to independently review it from different perspectives.

### Setup

```
Target: PR #42 - Add JWT authentication
Files: src/auth/jwt.ts, src/auth/middleware.ts, src/routes/auth.ts
Team:
  - Codex (Architect): Review structure and design
  - Gemini (Security): Check for vulnerabilities
  - Claude (QA): Assess test coverage
Workflow: Parallel
```

### Execution

#### Phase 1: Preparation (Orchestrator)

```
1. Read target files:
   - Glob: src/auth/**/*.ts
   - Read each file

2. Detect available agents:
   - which codex ✓
   - which gemini ✓
   - which claude ✓

3. Prepare context for each agent
```

#### Phase 2: Configuration (AskUserTool)

```
Q1: Select personas for this review
    [✓] Architect
    [✓] Security Researcher
    [✓] QA Engineer
    [ ] Code Reviewer
    [ ] Performance Engineer

Q2: Assign agents
    Architect → Codex CLI (gpt-5.2-codex)
    Security → Gemini CLI (gemini-2.5-pro)
    QA → Claude (sub-agent)

Q3: Workflow mode
    [✓] Parallel (Cross-Review)
```

#### Phase 3: Execution (Parallel)

**Agent A: Codex as Architect**

```bash
codex --model gpt-5.2-codex "$(cat <<'EOF'
You are a Senior Software Architect.

## Task
Review the following authentication implementation for design quality.

## Focus Areas
1. Module structure and separation of concerns
2. Dependency management
3. Interface design
4. Error handling patterns
5. Extensibility

## Code

### src/auth/jwt.ts
```typescript
import jwt from 'jsonwebtoken';

const SECRET = process.env.JWT_SECRET || 'default-secret';

export function generateToken(userId: string): string {
  return jwt.sign({ userId }, SECRET, { expiresIn: '15m' });
}

export function verifyToken(token: string): { userId: string } | null {
  try {
    return jwt.verify(token, SECRET) as { userId: string };
  } catch {
    return null;
  }
}
```

### src/auth/middleware.ts
```typescript
import { verifyToken } from './jwt';

export function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(401).json({ error: 'No token' });
  }
  const payload = verifyToken(token);
  if (!payload) {
    return res.status(401).json({ error: 'Invalid token' });
  }
  req.userId = payload.userId;
  next();
}
```

## Output Format
Provide findings with severity (Critical/High/Medium/Low) and recommendations.
EOF
)"
```

**Agent B: Gemini as Security Researcher**

```bash
gemini -p "$(cat <<'EOF'
You are a Security Researcher.

## Task
Perform a security analysis of this authentication implementation.

## Focus Areas
1. OWASP Top 10 vulnerabilities
2. JWT security best practices
3. Secret management
4. Token handling
5. Error message information leakage

## Code
[Same code as above]

## Output Format
List vulnerabilities with:
- ID (SEC-XXX)
- Type (OWASP category)
- Severity (Critical/High/Medium/Low)
- Location
- Attack scenario
- Remediation
EOF
)" -m gemini-2.5-pro
```

**Agent C: Claude as QA Engineer**

```
Task tool:
  subagent_type: general-purpose
  model: sonnet
  prompt: |
    You are a QA Engineer.

    ## Task
    Design a comprehensive test strategy for this authentication module.

    ## Focus Areas
    1. Unit test cases
    2. Integration test scenarios
    3. Edge cases and boundary conditions
    4. Security test cases
    5. Error handling tests

    ## Code
    [Same code as above]

    ## Output Format
    Provide:
    - Required test cases (table format)
    - Edge cases to cover
    - Test coverage recommendations
```

#### Phase 4: Synthesis

**Collected Results:**

Architect (Codex):
- Finding 1: Hardcoded fallback secret (High)
- Finding 2: No token refresh mechanism (Medium)
- Finding 3: Tight coupling with Express (Low)

Security (Gemini):
- SEC-001: Default secret in production risk (Critical)
- SEC-002: No token blacklist for logout (High)
- SEC-003: Error messages could leak info (Medium)

QA (Claude):
- Missing tests for expired tokens
- No integration tests with database
- Edge case: malformed token handling

**Synthesis:**

```markdown
## Consensus (All Agents Agree)
| Finding | Agents | Severity | Action |
|---------|--------|----------|--------|
| Hardcoded/default secret | Arch, Sec | Critical | Remove fallback, require env var |

## Unique Findings
| Finding | Agent | Severity | Action |
|---------|-------|----------|--------|
| No token blacklist | Security | High | Implement Redis blacklist |
| No refresh tokens | Architect | Medium | Add refresh token flow |
| Missing edge case tests | QA | Medium | Add test cases |

## Priority Actions
1. [P0] Remove default secret - throw error if not set
2. [P0] Implement token blacklist for logout
3. [P1] Add refresh token mechanism
4. [P1] Add comprehensive test suite
5. [P2] Decouple from Express for testability
```

---

## Example 2: Security Audit with Adversarial Review

### Scenario

Before launching a payment feature, we want a thorough security review with agents challenging each other's findings.

### Setup

```
Target: Payment processing module
Files: src/payment/**/*.ts
Team:
  - Codex (Proponent): Argues implementation is secure
  - Gemini (Opponent): Finds vulnerabilities
  - Claude (Adjudicator): Makes final assessment
Workflow: Adversarial
```

### Execution

**Round 1: Proponent (Codex)**

```bash
codex --model gpt-5.2-codex "
You are the PROPONENT defending this payment implementation's security.

## Your Position
Argue that this implementation is secure and follows best practices.

## Code
[Payment code]

## Task
1. List security measures already in place
2. Explain why they are sufficient
3. Reference industry standards followed
4. Anticipate and preempt criticisms
"
```

Result:
- Uses Stripe SDK (PCI compliant)
- No card data stored locally
- HTTPS enforced
- Input validation on amounts
- Idempotency keys prevent double charges

**Round 1: Opponent (Gemini)**

```bash
gemini -p "
You are the OPPONENT challenging this payment implementation.

## Proponent's Claims
[Codex's arguments]

## Code
[Payment code]

## Task
1. Challenge each security claim
2. Find vulnerabilities the proponent missed
3. Propose attack scenarios
4. Suggest alternative, more secure approaches
" -m gemini-2.5-pro
```

Result:
- Idempotency key predictable (timestamp-based)
- No rate limiting on payment attempts
- Webhook signature verification missing
- Error messages reveal internal errors
- No audit logging

**Round 2: Rebuttals**

[Exchange continues with proponent defending and opponent pressing]

**Adjudication (Claude)**

```
Task tool:
  subagent_type: general-purpose
  model: opus
  prompt: |
    You are the neutral ADJUDICATOR.

    ## Debate Summary
    Proponent (Codex): [Summary]
    Opponent (Gemini): [Summary]

    ## Task
    1. Evaluate which arguments are valid
    2. Determine winner
    3. Synthesize actionable recommendations
    4. Provide final security assessment
```

**Final Decision:**

```markdown
## Adjudication Result

**Winner: Opponent (Gemini)**

Rationale: While the implementation has good foundational security
(Stripe SDK, HTTPS), the opponent identified critical operational
security gaps that must be addressed.

## Required Fixes (from debate)
1. [Critical] Add webhook signature verification
2. [Critical] Implement rate limiting
3. [High] Use cryptographic idempotency keys
4. [High] Add audit logging
5. [Medium] Sanitize error messages

## Security Assessment
Current: **Not Ready for Production**
After fixes: **Ready with monitoring**
```

---

## Example 3: Implementation + Test Pipeline

### Scenario

User requests a new feature. We use pipeline workflow to implement, test, and review with different agents.

### Setup

```
Feature: Add user profile update endpoint
Team:
  - Claude (Implementer): Writes the code
  - Codex (Tester): Creates tests (blind)
  - Gemini (Reviewer): Final review
Workflow: Pipeline
```

### Execution

**Stage 1: Implementation (Claude - Orchestrator)**

Orchestrator implements the feature:

```typescript
// src/routes/profile.ts
export async function updateProfile(req: Request, res: Response) {
  const { userId } = req.params;
  const { name, email, bio } = req.body;

  // Validate input
  if (!name && !email && !bio) {
    return res.status(400).json({ error: 'No fields to update' });
  }

  if (email && !isValidEmail(email)) {
    return res.status(400).json({ error: 'Invalid email format' });
  }

  try {
    const updated = await userService.updateProfile(userId, { name, email, bio });
    return res.json(updated);
  } catch (error) {
    if (error instanceof UserNotFoundError) {
      return res.status(404).json({ error: 'User not found' });
    }
    throw error;
  }
}
```

**Stage 2: Testing (Codex - Blind)**

```bash
codex --model gpt-5.2-codex "
You are a QA Engineer. You did NOT write this code.

## Requirements (NOT the implementation)
- Users can update their profile (name, email, bio)
- Email must be valid format if provided
- At least one field must be provided
- Returns 404 if user not found
- Returns updated profile on success

## Public API
PUT /users/:userId/profile
Body: { name?: string, email?: string, bio?: string }
Response: User object or error

## Task
Write comprehensive tests based ONLY on the requirements.
Do NOT look at implementation details.
Include:
- Happy path tests
- Validation error tests
- Edge cases
- Security considerations
"
```

Result: Test suite with 15 test cases including:
- Update single field
- Update all fields
- Empty body rejection
- Invalid email rejection
- Non-existent user handling
- SQL injection attempt in bio field (!)
- XSS attempt in name field (!)

**Stage 3: Review (Gemini)**

```bash
gemini -p "
You are performing final review before merge.

## Implementation
[Profile update code]

## Test Suite
[Codex's tests]

## Test Results
[Test run output - all passing]

## Review Checklist
1. Does implementation meet requirements?
2. Are tests adequate?
3. Security issues?
4. Performance issues?

## Decision
APPROVE or REQUEST_CHANGES with specific items
" -m gemini-2.5-pro
```

Result:
```
Decision: REQUEST_CHANGES

Required Changes:
1. Add input sanitization for XSS (Tester found this!)
2. Add rate limiting to prevent abuse
3. Add audit logging for compliance

Suggestions:
- Consider partial update validation
- Add email verification flow
```

**Feedback Loop**

Orchestrator implements fixes → Codex updates tests → Gemini re-reviews → APPROVE

---

## Example 4: Quick Second Opinion

### Scenario

Developer wants a quick sanity check on a code change from a different AI perspective.

### Setup

```
Task: Get second opinion on error handling approach
Primary: Claude (current session)
Secondary: Codex
Workflow: Simple second opinion
```

### Execution

```
User: "I'm handling errors like this. Is this a good approach?"

Orchestrator (Claude) analysis:
- Pattern looks reasonable
- Uses custom error types
- Consistent error responses

Get second opinion:
```

```bash
codex --model gpt-5.2-codex "
Quick review: Is this error handling approach good?

[Code snippet]

Respond with:
- Thumbs up/down
- One thing that's good
- One thing to improve (if any)
"
```

Result:
```
👍 Thumbs up

Good: Custom error types enable precise handling

Improve: Consider using a Result type instead of try/catch
for expected errors (like validation failures)
```

**Report to User:**

```markdown
## Second Opinion Results

Your approach: ✅ Validated

**Claude's take:**
Pattern is reasonable with good consistency.

**Codex's take:**
Agrees it's good. Suggests considering Result type for
expected errors as an alternative pattern.

**Consensus:** Approach is sound. Optional enhancement available.
```

---

## Quick Start Templates

### Template 1: Fast Cross-Review

```
1. Select 2-3 personas
2. Use Parallel workflow
3. Synthesize in < 5 minutes

Good for: PR reviews, quick audits
```

### Template 2: Deep Security Audit

```
1. Security Researcher + Analyzer
2. Use Adversarial workflow
3. Multiple rounds of debate

Good for: Pre-launch security, compliance
```

### Template 3: Feature Development

```
1. Implement with orchestrator
2. Test with different agent (blind)
3. Review with third agent

Good for: New features, TDD
```

### Template 4: Architecture Decision

```
1. Architect presents option A
2. Different Architect argues option B
3. User adjudicates with synthesized pros/cons

Good for: Major design decisions
```
