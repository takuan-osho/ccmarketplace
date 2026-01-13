# Commit Message Guide for Traceability

## Overview

Well-written commit messages are critical for traceability. They enable:
- Finding all changes related to a requirement
- Understanding why code was changed
- Connecting production issues back to requirements
- Generating release notes automatically
- Code archaeology and debugging

## Format

### Basic Structure

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Conventional Commits Format

```
type(scope): Short description (#issue)

Longer explanation of what and why (not how).
Can be multiple paragraphs.

Related: REQ-001, ADR-005
Implements: requirement docs/requirements/REQ-001.md
Closes: #123
```

## Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(auth): Add JWT-based authentication` |
| `fix` | Bug fix | `fix(api): Handle missing user ID in request` |
| `docs` | Documentation only | `docs(readme): Update installation instructions` |
| `style` | Code style (formatting) | `style(api): Fix indentation in handler.py` |
| `refactor` | Code refactoring | `refactor(db): Extract query logic to repository` |
| `perf` | Performance improvement | `perf(cache): Implement Redis caching layer` |
| `test` | Adding/updating tests | `test(auth): Add integration tests for login` |
| `build` | Build system changes | `build(deps): Update httpx to 0.27.0` |
| `ci` | CI/CD changes | `ci(github): Add automated security scanning` |
| `chore` | Maintenance tasks | `chore(deps): Update development dependencies` |
| `revert` | Revert previous commit | `revert: Revert "feat(api): Add new endpoint"` |

## Examples

### ✅ Good Commit Messages

#### 1. Feature Implementation

```
feat(device): Implement device property validation (#42)

Add validation for ECHONET Lite property values before sending
to device. This prevents invalid commands from being sent and
improves error messages for users.

- Validate property ranges based on device type
- Add custom error messages for each property
- Update API documentation

Implements: REQ-005 Device Property Validation
Related ADR: ADR-010
Closes: #42
```

**Why it's good:**
- Clear type and scope
- Issue number in subject
- Explains what and why
- Links to requirements and ADR
- Closes the issue

#### 2. Bug Fix

```
fix(auth): Handle expired tokens correctly (#89)

Fix issue where expired JWT tokens were not being properly rejected,
allowing unauthorized access in some edge cases.

Root cause: Token expiry check was using wrong timezone, causing
tokens to appear valid for an extra hour.

- Update token validation to use UTC
- Add test cases for token expiry
- Add logging for token validation failures

Fixes: #89
Related: REQ-002 Authentication
Trace-ID: 1-68e3927d-3dd1ffab (production error)
```

**Why it's good:**
- Describes the bug clearly
- Explains root cause
- Links to production trace ID
- Connects to requirement

#### 3. Refactoring

```
refactor(api): Extract Kii client to separate service (#56)

Separate Kii Cloud API client logic from Lambda handler for better
testability and maintainability.

This refactoring:
- Moves all Kii API calls to services/kii_client.py
- Makes mocking easier in tests
- Reduces handler complexity from 200 to 80 lines
- Follows single responsibility principle

No functional changes - all tests pass.

Related ADR: ADR-008 Service Layer Architecture
```

**Why it's good:**
- Clear that it's refactoring
- Explains benefits
- Notes no functional changes
- Links to architecture decision

#### 4. Documentation

```
docs(adr): Add ADR-012 for async processing strategy

Document decision to use SQS for asynchronous device command processing
to handle Lambda timeout limitations.

Related: REQ-007 Long-running Commands
Issue: #67
```

**Why it's good:**
- Clear documentation change
- Explains what was documented
- Links to requirement and issue

### ❌ Bad Commit Messages

#### 1. Too Vague

```
fix bug
```

**Problems:**
- What bug?
- Where?
- Why did it happen?
- No traceability

#### 2. No Context

```
Update handler.py
```

**Problems:**
- What was updated?
- Why?
- What's the impact?

#### 3. Too Much Detail

```
feat(api): Add new endpoint for getting device properties

This commit adds a new endpoint at /devices/{id}/properties that
returns all properties for a device. First I created the route
in app.py on line 45, then I added the handler function on line
120. Then I updated the imports at the top of the file. I also
had to modify the response schema...
```

**Problems:**
- Implementation details in commit message (should be in code)
- No "why"
- Missing requirement/issue links

## Traceability Linking

### Reference Requirements

```
Implements: REQ-001
Related: REQ-002, REQ-005
See: docs/requirements/REQ-001-user-auth.md
```

### Reference ADRs

```
Implements: ADR-003 Redis Session Storage
Related ADR: ADR-001, ADR-002
See: docs/adr/ADR-003-use-redis.md
```

### Reference Issues

```
Closes: #123
Fixes: #456
Related: #789
```

### Reference Production Traces

```
Fixes production error: Trace-ID 1-68e3927d-3dd1ffab
CloudWatch Log Group: /aws/lambda/my-function
Error timestamp: 2024-01-15T10:30:00Z
```

## Multi-Commit Workflow

### Breaking Changes

```
feat(api)!: Change authentication to JWT-based

BREAKING CHANGE: API now requires JWT tokens instead of API keys.

Old clients using API keys will stop working. Migration guide
available at docs/migration/api-key-to-jwt.md

Implements: ADR-007 JWT Authentication
Related: REQ-002
```

**Note:** The `!` in `feat(api)!:` marks breaking changes.

### Co-authored Commits

```
feat(cache): Implement distributed caching

Implements Redis-based distributed caching for session data.

Co-authored-by: Jane Developer <jane@example.com>
Co-authored-by: Bob Reviewer <bob@example.com>

Implements: ADR-003
```

## Commit Message Templates

### Git Config Template

Create `.gitmessage` in your project:

```
# <type>(<scope>): <subject> (#issue)
#
# <body>
#
# Implements: REQ-XXX
# Related ADR: ADR-XXX
# Closes: #XXX
# Trace-ID: (if fixing production issue)
#
# Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore
# Scope: Component/module affected
# Subject: Imperative, present tense, lowercase, no period
# Body: What and why (not how)
```

Configure git to use it:

```bash
git config commit.template .gitmessage
```

### Project-Specific Template

For a specific project, add traceability fields:

```
# <type>(<scope>): <subject> (#issue)
#
# What changed:
#
#
# Why it changed:
#
#
# Traceability:
# - Requirement:
# - ADR:
# - Issue:
# - Trace-ID (if production bug):
#
# Testing:
# - [ ] Unit tests added/updated
# - [ ] Integration tests pass
# - [ ] Manual testing performed
```

## Searching Commits for Traceability

### Find All Commits for a Requirement

```bash
git log --all --grep="REQ-001"
```

### Find Commits for an ADR

```bash
git log --all --grep="ADR-003"
```

### Find Commits Fixing Production Issues

```bash
git log --all --grep="Trace-ID"
```

### Find Breaking Changes

```bash
git log --all --grep="BREAKING CHANGE"
```

### Advanced Search

```bash
# Find all feature commits in last month
git log --all --since="1 month ago" --grep="^feat"

# Find all commits related to authentication
git log --all --grep="auth" --oneline

# Find commits by specific author for a requirement
git log --all --author="John" --grep="REQ-005"
```

## Automation

### Commit Message Linting

Use [commitlint](https://commitlint.js.org/) to enforce format:

```bash
# .commitlintrc.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'footer-max-line-length': [0, 'always'],
    'body-max-line-length': [0, 'always'],
  },
};
```

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/commit-msg

# Check for requirement/issue reference
if ! grep -qE "(REQ-[0-9]+|#[0-9]+|ADR-[0-9]+)" "$1"; then
    echo "Error: Commit message must reference REQ-XXX, ADR-XXX, or #issue"
    exit 1
fi
```

### Generate Changelog

```bash
# Using conventional-changelog
npx conventional-changelog -p angular -i CHANGELOG.md -s

# Filter by requirement
git log --all --grep="REQ-001" --oneline > REQ-001-history.txt
```

## Best Practices Summary

1. **Use conventional commit format** - Enables automation
2. **Include issue/requirement references** - Enables traceability
3. **Explain why, not how** - How is in the code
4. **Write for future developers** - Including yourself in 6 months
5. **One logical change per commit** - Makes debugging easier
6. **Use imperative mood** - "Add feature" not "Added feature"
7. **Keep subject line under 50 chars** - Readable in git log
8. **Wrap body at 72 chars** - Readable in terminal
9. **Link to production traces** - For bug fixes
10. **Reference ADRs** - Connect code to decisions

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ Traceable Commit Message Template              │
├─────────────────────────────────────────────────┤
│ type(scope): Short description (#123)          │
│                                                 │
│ Detailed explanation of what and why.          │
│                                                 │
│ Implements: REQ-XXX                            │
│ Related ADR: ADR-XXX                           │
│ Closes: #123                                   │
│ Trace-ID: (if production bug)                  │
└─────────────────────────────────────────────────┘

Types: feat fix docs refactor perf test build ci
Scope: Component or module affected
Subject: Present tense, lowercase, no period
Body: What and why (not how)
Footer: Traceability links
```
