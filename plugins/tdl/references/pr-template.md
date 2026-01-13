# Pull Request Templates for Traceability

## Overview

Well-structured pull requests are critical for:
- Code review efficiency
- Tracing features back to requirements
- Understanding historical decisions
- Onboarding new team members
- Generating release notes

## Basic PR Template

```markdown
## What does this PR do?

<!-- Brief, clear description of what this PR accomplishes -->

## Changes Made

<!-- Detailed list of changes -->
-
-
-

## Related Documentation

<!-- Links to requirements, ADRs, analysis docs -->
- **Requirements**: [REQ-XXX](../docs/requirements/REQ-XXX.md)
- **ADR**: [ADR-XXX](../docs/adr/ADR-XXX.md)
- **Analysis**: [AN-XXX](../docs/analysis/AN-XXX.md)
- **Issue**: #XXX

## Testing

<!-- How was this tested? -->
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] Performance tested (if applicable)

## Screenshots/Recordings

<!-- If applicable, add screenshots or recordings -->

## Deployment Notes

<!-- Any special deployment considerations? -->

## Checklist

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Linked to related issue/requirement
- [ ] Breaking changes documented
- [ ] Security implications considered
```

## Feature PR Template

```markdown
## Feature: [Feature Name]

### What does this PR do?

Implements [feature name] to allow users to [capability].

### Business Value

<!-- Why is this feature important? -->
This feature addresses [business need] and provides [benefit to users].

### Changes Made

#### New Files
- `src/features/feature-name.py` - Main feature implementation
- `tests/test_feature_name.py` - Test suite

#### Modified Files
- `src/app.py` - Added feature route
- `docs/api.md` - Updated API documentation

#### Database Changes
- [ ] No database changes
- [x] Added tables: `feature_data`
- [ ] Modified existing tables
- [ ] Migration required: `migrations/003_add_feature.sql`

### Traceability

- **Requirement**: [REQ-015 Feature Name](../docs/requirements/REQ-015-feature-name.md)
- **Design Decision**: [ADR-012 Feature Architecture](../docs/adr/ADR-012-feature-architecture.md)
- **User Story**: #456
- **Epic**: #123

### API Changes

#### New Endpoints

```
GET /api/v1/feature
POST /api/v1/feature/{id}
```

#### Request/Response Examples

<details>
<summary>POST /api/v1/feature/{id}</summary>

**Request:**
```json
{
  "action": "enable",
  "options": {
    "level": "standard"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "feature_id": "feat_123",
  "enabled": true
}
```
</details>

### Testing

#### Unit Tests
```bash
pytest tests/test_feature_name.py -v
```

- [x] All new functions have tests
- [x] Edge cases covered
- [x] Error handling tested

#### Integration Tests
```bash
pytest tests/integration/test_feature_integration.py -v
```

- [x] End-to-end scenarios tested
- [x] External API integration tested
- [x] Database operations tested

#### Manual Testing Checklist
- [x] Feature works in local environment
- [x] Feature works with existing data
- [x] Error messages are user-friendly
- [x] Performance is acceptable (< 200ms response time)

### Performance Impact

- **Response Time**: Adds ~50ms to request processing
- **Memory**: +10MB baseline, +5MB per active feature
- **Database**: 2 additional queries per request

Load testing results:
- 100 concurrent users: Avg 150ms, 95th percentile 250ms
- No degradation observed

### Security Considerations

- [x] Input validation implemented
- [x] Authorization checks added
- [x] No sensitive data in logs
- [x] SQL injection prevented (parameterized queries)
- [x] XSS prevention implemented
- [x] Rate limiting considered

### Breaking Changes

- [ ] No breaking changes
- [x] Breaking changes (described below)

**Breaking Changes:**
- API endpoint `/api/v1/old-feature` is deprecated
- Response format changed for `/api/v1/feature` (added `version` field)

**Migration Guide:** See [MIGRATION.md](../docs/MIGRATION.md#v2-feature-changes)

### Documentation Updates

- [x] API documentation updated
- [x] README updated
- [x] User guide updated
- [x] Architecture diagrams updated
- [ ] Video tutorial needed (tracked in #789)

### Deployment Notes

**Environment Variables:**
```bash
FEATURE_ENABLED=true
FEATURE_LEVEL=standard
```

**Configuration:**
- Update `config/production.yaml` with new feature flags
- Restart service after deployment

**Rollback Plan:**
- Set `FEATURE_ENABLED=false`
- No database rollback needed (backward compatible)

### Follow-up Tasks

- [ ] Add admin UI for feature configuration (#790)
- [ ] Implement analytics tracking (#791)
- [ ] Create video tutorial (#789)
- [ ] Update monitoring dashboards (#792)

### Review Notes

**Areas needing special attention:**
1. Error handling in `feature_processor.py` lines 45-60
2. Database query optimization in `repository.py` line 123
3. Race condition prevention in `cache.py` lines 78-95

### Screenshots

<details>
<summary>Feature UI</summary>

![Feature UI](./screenshots/feature-ui.png)
</details>

<details>
<summary>Admin Configuration</summary>

![Admin Config](./screenshots/admin-config.png)
</details>

---

**Related PRs:** #456, #457
**Depends on:** #455
**Blocks:** #459

```

## Bug Fix PR Template

```markdown
## Bug Fix: [Bug Description]

### What was the bug?

<!-- Clear description of the bug behavior -->

Users were unable to [action] when [condition] because [root cause].

### Root Cause Analysis

<!-- Technical explanation of why the bug occurred -->

The bug was caused by [technical explanation]. Specifically:

1. [Step 1 that led to bug]
2. [Step 2 that led to bug]
3. [Result/symptom]

**Code path:**
```
user_action() → function_a() → function_b() → BUG HERE
```

### How to Reproduce (Before Fix)

1. Navigate to [page/endpoint]
2. Perform [action]
3. Observe [incorrect behavior]

**Expected:** [correct behavior]
**Actual:** [incorrect behavior]

### The Fix

<!-- Explanation of the solution -->

The fix addresses the root cause by [explanation]:

- [Change 1]
- [Change 2]
- [Change 3]

### Changes Made

**Modified Files:**
- `src/module/file.py` - Fixed validation logic (line 123)
- `tests/test_file.py` - Added regression test

**Diff highlights:**
```diff
- if user_input is None:
+ if user_input is None or user_input == "":
      raise ValidationError("Input required")
```

### Traceability

- **Issue**: #789 Users cannot submit empty forms
- **Production Trace ID**: `1-68e3927d-3dd1ffab`
- **CloudWatch Logs**: `/aws/lambda/api-handler` @ 2024-01-15T10:30:00Z
- **Related Requirement**: [REQ-008 Input Validation](../docs/requirements/REQ-008.md)
- **Error Count**: 1,234 occurrences in past 24 hours
- **Affected Users**: ~500 users

### Testing

#### Regression Test
```python
def test_empty_input_validation():
    """Regression test for #789"""
    with pytest.raises(ValidationError):
        validate_input("")
    with pytest.raises(ValidationError):
        validate_input(None)
```

#### Manual Testing Checklist
- [x] Bug no longer reproduces
- [x] Original functionality still works
- [x] Edge cases handled:
  - [x] Empty string
  - [x] Null value
  - [x] Whitespace only
  - [x] Very long input

### Impact Assessment

**Before Fix:**
- Error rate: 2.5% of all requests
- Affected endpoints: `/api/v1/submit`, `/api/v1/update`
- User complaints: 15 in past week

**After Fix:**
- Error rate: 0.1% (unrelated errors only)
- No new user complaints
- Backward compatible: Yes

### Deployment Priority

**Severity:** HIGH
**Priority:** Deploy ASAP

**Reasoning:**
- Affects 500+ users daily
- High error volume (1,000+ errors/day)
- Simple fix with low risk
- No breaking changes

### Rollback Plan

If issues arise:
1. Revert this PR
2. Original code path still valid
3. No data migration needed

### Follow-up

- [ ] Add monitoring alert for this error pattern (#800)
- [ ] Improve error message user-friendliness (#801)
- [ ] Document validation requirements in API docs (#802)

---

**Fixes:** #789
**Production Trace:** 1-68e3927d-3dd1ffab
```

## Refactoring PR Template

```markdown
## Refactoring: [Component Name]

### What does this PR do?

Refactors [component] to improve [quality attribute: maintainability, testability, performance].

### Motivation

<!-- Why is this refactoring needed? -->

Current implementation has the following issues:
- [Issue 1: e.g., tight coupling]
- [Issue 2: e.g., hard to test]
- [Issue 3: e.g., code duplication]

### Changes Made

#### Architectural Changes
- Extracted [X] into separate module
- Introduced [pattern] pattern
- Separated [concerns]

#### Before & After

**Before:**
```python
# 200 lines of mixed logic
def handle_request(request):
    # validation
    # business logic
    # database access
    # response formatting
    pass
```

**After:**
```python
# handler.py (20 lines)
def handle_request(request):
    validated = validator.validate(request)
    result = service.process(validated)
    return formatter.format(result)

# validator.py (30 lines)
# service.py (50 lines)
# formatter.py (20 lines)
```

#### Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Lines of code | 200 | 120 | -40% |
| Cyclomatic complexity | 15 | 5 | -67% |
| Test coverage | 60% | 95% | +35% |
| Files | 1 | 4 | +3 |

### Traceability

- **Technical Debt**: #678
- **ADR**: [ADR-014 Service Layer Pattern](../docs/adr/ADR-014-service-layer.md)
- **Related Requirement**: [REQ-001](../docs/requirements/REQ-001.md) (unchanged)

### Testing

- [x] All existing tests pass
- [x] No functional changes
- [x] Test coverage increased from 60% to 95%
- [x] Added tests for previously untested edge cases

```bash
# Verify no behavioral changes
pytest tests/ -v --cov=src --cov-report=html
```

### Functional Changes

**None.** This is a pure refactoring with no behavioral changes.

All tests pass without modification, proving equivalence.

### Review Guide

For reviewers:

1. **Verify no functional changes:**
   - Run tests before and after
   - Check that all tests pass without modification

2. **Focus areas:**
   - Improved separation of concerns in `service.py`
   - Better error handling in `validator.py`
   - Simplified handler logic in `handler.py`

3. **Don't worry about:**
   - More files (intentional separation)
   - Import changes (refactoring consequence)

### Benefits

1. **Maintainability**: Each module has single responsibility
2. **Testability**: Easy to mock dependencies
3. **Readability**: Clear separation of concerns
4. **Extensibility**: Easy to add new validators/formatters

### Follow-up

- [ ] Apply same pattern to related modules (#803)
- [ ] Update architecture diagrams (#804)
- [ ] Share pattern in team documentation (#805)

---

**Closes:** #678 (Technical Debt: Refactor request handler)
```

## Documentation PR Template

```markdown
## Documentation: [Topic]

### What does this PR do?

Updates documentation for [topic/feature/system].

### Changes Made

#### New Documentation
- `docs/requirements/REQ-020-new-feature.md` - New requirement spec
- `docs/adr/ADR-015-tech-decision.md` - Architecture decision

#### Updated Documentation
- `README.md` - Added setup instructions for new feature
- `docs/api.md` - Updated API endpoints
- `CHANGELOG.md` - Added entry for v2.5.0

### Motivation

<!-- Why was this documentation needed? -->

- [Reason 1: e.g., New feature added in #456]
- [Reason 2: e.g., User feedback about unclear docs]
- [Reason 3: e.g., Onboarding difficulties]

### Traceability

- **Related PR**: #456 (Feature implementation)
- **Requirement**: REQ-020
- **User Feedback**: #789 (Users unclear about authentication)

### Review Checklist

- [x] No typos or grammatical errors
- [x] All links work
- [x] Code examples are correct and tested
- [x] Consistent with existing documentation style
- [x] Screenshots up-to-date (if applicable)
- [x] Table of contents updated

### Impact

**Before:**
- Documentation coverage: 60% of features
- Average onboarding time: 3 days
- User questions/week: 25

**Expected After:**
- Documentation coverage: 85% of features
- Average onboarding time: 2 days
- User questions/week: <15 (estimate)

---

**Related:** #456, #789
```

## Release PR Template

```markdown
## Release v[X.Y.Z]

### Release Summary

This release includes [number] features, [number] bug fixes, and [number] improvements.

### Highlights

- **Feature**: [Major feature 1] (#123)
- **Feature**: [Major feature 2] (#124)
- **Fix**: [Important bug fix] (#125)
- **Performance**: [Performance improvement] (#126)

### Changelog

#### Features
- [Feature 1] (#123) - Implements REQ-015
- [Feature 2] (#124) - Implements REQ-016

#### Bug Fixes
- Fix [bug 1] (#125) - Fixes issue with [X]
- Fix [bug 2] (#126) - Resolves [Y] error

#### Improvements
- Improve [aspect 1] (#127)
- Optimize [aspect 2] (#128)

#### Breaking Changes
- **BREAKING**: [Change description] (#129)
  - Migration guide: [link]
  - Impacts: [who/what]

### Traceability Matrix

| Feature | Requirement | ADR | Tests | Docs |
|---------|-------------|-----|-------|------|
| Feature 1 | REQ-015 | ADR-020 | ✅ | ✅ |
| Feature 2 | REQ-016 | ADR-021 | ✅ | ✅ |

### Testing

- [x] All tests pass
- [x] Integration tests pass
- [x] Performance tests pass
- [x] Security scan passed
- [x] Manual QA completed

### Deployment Checklist

#### Pre-deployment
- [ ] Backup database
- [ ] Review rollback plan
- [ ] Notify stakeholders
- [ ] Schedule maintenance window

#### Deployment
- [ ] Deploy to staging
- [ ] Run smoke tests
- [ ] Deploy to production
- [ ] Verify deployment

#### Post-deployment
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify critical paths
- [ ] Update status page

### Migration Guide

For users upgrading from v[X.Y.Z-1]:

1. **Update configuration:**
   ```yaml
   # Add new config
   new_feature:
     enabled: true
   ```

2. **Run migrations:**
   ```bash
   ./scripts/migrate.sh v[X.Y.Z]
   ```

3. **Update API calls:**
   - Change `old_endpoint` to `new_endpoint`
   - Update request format (see docs)

### Rollback Plan

If critical issues arise:

```bash
# Rollback commands
git revert <commit>
./scripts/deploy.sh v[X.Y.Z-1]
```

### Documentation

- [x] CHANGELOG.md updated
- [x] Version bumped in package.json
- [x] Release notes published
- [x] Migration guide created

---

**Includes:** #123, #124, #125, #126, #127, #128, #129
```

## Best Practices

### 1. **Link Everything**

Always link to:
- Issues (#123)
- Requirements (REQ-XXX)
- ADRs (ADR-XXX)
- Related PRs (#456)
- Production traces (if bug fix)

### 2. **Use Checklists**

Checklists ensure:
- Nothing is forgotten
- Process is followed
- Reviewers know what to check

### 3. **Add Context**

Help reviewers by:
- Explaining "why" not just "what"
- Highlighting areas needing attention
- Providing testing instructions
- Including screenshots/recordings

### 4. **Track Metrics**

Include before/after metrics:
- Performance (response time, memory)
- Code quality (coverage, complexity)
- User impact (error rate, usage)

### 5. **Plan Follow-ups**

Create follow-up tasks for:
- Future improvements
- Related work
- Documentation updates
- Monitoring setup

## Automation

### Auto-link Issues

Use keywords in PR description:
- `Closes #123` - Closes issue when PR merges
- `Fixes #456` - Same as Closes
- `Resolves #789` - Same as Closes
- `Related #111` - Links without closing

### PR Labels

Auto-apply labels based on:
- Changed files (e.g., `backend`, `frontend`)
- PR title prefix (e.g., `feat:` → `feature`)
- Content (e.g., "BREAKING" → `breaking-change`)

### GitHub Actions

```yaml
# .github/workflows/pr-checks.yml
name: PR Checks
on: [pull_request]

jobs:
  check-traceability:
    runs-on: ubuntu-latest
    steps:
      - name: Check for requirement links
        run: |
          if ! grep -qE "(REQ-[0-9]+|#[0-9]+)" ${{ github.event.pull_request.body }}; then
            echo "Error: PR must reference a requirement or issue"
            exit 1
          fi
```

## Summary

Good PR templates:
- ✅ Provide structure and consistency
- ✅ Ensure traceability links are included
- ✅ Guide reviewers to important areas
- ✅ Document decisions and context
- ✅ Enable efficient code review
- ✅ Support compliance and auditing
- ✅ Facilitate knowledge transfer
- ✅ Improve team communication
