# Interview Skill Usage Examples

This document provides detailed examples of how to use the interview skill for different scenarios.

## Example 1: Feature Requirements

**Command:**
```
/interview Add user authentication to the API
```

**Phase 1: Preparation**
- Explore codebase for existing auth patterns
- Check for auth-related dependencies (JWT, OAuth libraries)
- Review security documentation or policies

**Phase 2: Interview**
- Goal: Understand authentication requirements
- Questions:
  - What authentication method? (OAuth, JWT, session-based)
  - What user roles and permissions are needed?
  - What session management requirements exist?
  - What are the security requirements? (MFA, password policies)
  - Integration with existing user database?

**Phase 3: Output**
```markdown
# Requirements: User Authentication API

## Summary
Implement JWT-based authentication with role-based access control.

## Goal
- **Objective**: Secure API endpoints with user authentication
- **Stakeholders**: API consumers, security team
- **Success Criteria**: All protected endpoints require valid JWT

## Requirements
### Must Have
- JWT token generation and validation
- User login/logout endpoints
- Password hashing with bcrypt

### Should Have
- Refresh token mechanism
- Role-based access control (admin, user)

### Could Have
- OAuth2 social login integration
- MFA support

## Affected Files / Components
- `src/auth/` - New auth module
- `src/middleware/` - Auth middleware
- `src/routes/` - Protected route definitions
```

---

## Example 2: Bug Investigation

**Command:**
```
/interview Investigate 504 timeout errors in production
```

**Phase 1: Preparation**
- Check recent deployments and changes
- Review error logs and metrics
- Identify affected endpoints

**Phase 2: Interview**
- Goal: Understand the scope and impact of the issue
- Questions:
  - When did errors first appear?
  - What is the frequency? (constant, intermittent, peak hours)
  - Which endpoints are affected?
  - Any recent changes? (deployments, config, traffic patterns)
  - What has been tried so far?

**Phase 3: Output**
```markdown
# Investigation: 504 Timeout Errors in Production

## Summary
Intermittent 504 errors occurring on /api/reports endpoint since last deployment.

## Timeline
| Time | Event |
|------|-------|
| Jan 15 10:00 | Deployment v2.3.1 |
| Jan 15 14:30 | First 504 errors reported |
| Jan 15 16:00 | Error rate increased to 5% |

## Hypotheses
1. **Database query timeout** - Reports query may be slow for large datasets
   - Evidence: Slow query logs show 30s+ queries
2. **Connection pool exhaustion** - Connections not being released
   - Evidence: DB connection count elevated

## Next Steps
1. [ ] Add query timeout and pagination to reports endpoint
2. [ ] Review connection pool settings
3. [ ] Add circuit breaker for database calls

## References
- Error logs: `/var/log/app/error.log`
- Deployment: PR #456
```

---

## Example 3: Architecture Review

**Command:**
```
/interview Review database schema for scalability
```

**Phase 1: Preparation**
- Analyze current schema and relationships
- Review query patterns and indexes
- Check current data volume and growth rate

**Phase 2: Interview**
- Goal: Understand scalability requirements and constraints
- Questions:
  - What is the expected data growth rate?
  - What are the current pain points?
  - What queries are slowest?
  - What are the non-negotiable constraints?
  - What trade-offs are acceptable? (consistency vs availability)

**Phase 3: Output**
```markdown
# Architecture Review: Database Schema Scalability

## Current State
- PostgreSQL with 50+ tables
- 10M rows in largest table (events)
- Pain points: Slow aggregation queries, growing storage costs

## Proposed Changes
| Option | Pros | Cons |
|--------|------|------|
| Partitioning | Native PG support, transparent | Complex maintenance |
| Sharding | Horizontal scale | Application changes required |
| TimescaleDB | Optimized for time-series | Migration effort |

## Recommendation
Implement table partitioning for events table by month.

## Implementation Plan
1. Create partitioned table structure
2. Migrate existing data
3. Update application queries
4. Monitor performance

## Risks
- Migration downtime: Mitigate with blue-green deployment
- Query compatibility: Test all existing queries
```

---

## Example 4: Security Assessment

**Command:**
```
/interview Security review for payment processing module
```

**Phase 1: Preparation**
- Review current payment flow
- Check for sensitive data handling
- Identify external integrations

**Phase 2: Interview**
- Goal: Identify security risks and requirements
- Questions:
  - What payment data is stored? (PCI DSS scope)
  - What encryption is used for data at rest/transit?
  - What authentication protects payment endpoints?
  - What audit logging exists?
  - What compliance requirements apply?

**Phase 3: Output**
```markdown
# Security Assessment: Payment Processing Module

## Assets
| Asset | Sensitivity | Current Protection |
|-------|-------------|-------------------|
| Card numbers | High (PCI) | Tokenized via Stripe |
| Transaction logs | Medium | Encrypted at rest |
| User payment history | Medium | Access controlled |

## Findings
| Finding | Severity | Recommendation |
|---------|----------|----------------|
| Logs contain partial card numbers | High | Mask all card data in logs |
| No rate limiting on payment API | Medium | Add rate limiting |
| Missing audit trail for refunds | Medium | Add audit logging |

## Recommendations
1. Implement log sanitization for payment data
2. Add rate limiting (10 requests/minute per user)
3. Enable audit logging for all payment operations
```

---

## Example 5: Documentation

**Command:**
```
/interview Create API documentation for external developers
```

**Phase 1: Preparation**
- Review existing API endpoints
- Check for existing documentation
- Identify common use cases

**Phase 2: Interview**
- Goal: Understand documentation requirements
- Questions:
  - Who is the target audience? (external devs, partners)
  - What technical level should we assume?
  - What format is preferred? (OpenAPI, Markdown, hosted docs)
  - What examples are most important?
  - What authentication flow needs documentation?

**Phase 3: Output**
```markdown
# Documentation Plan: External API Documentation

## Audience
- Primary: External developers integrating our API
- Technical level: Intermediate (familiar with REST APIs)

## Content Outline
1. Getting Started
   - Authentication (API keys)
   - Base URL and versioning
   - Rate limits
2. Core Endpoints
   - Users API
   - Orders API
   - Products API
3. Webhooks
   - Event types
   - Payload formats
   - Retry policy
4. Error Handling
   - Error codes
   - Troubleshooting

## Format
- OpenAPI 3.0 specification
- Hosted on readme.io
- Interactive API explorer

## Next Steps
1. Generate OpenAPI spec from code
2. Write getting started guide
3. Create example applications
```

---

## Example 6: General Exploration

**Command:**
```
/interview Help me understand this codebase
```

**Phase 1: Preparation**
- Explore project structure
- Read README and documentation
- Identify key entry points

**Phase 2: Interview**
- Goal: Understand what the user wants to accomplish
- Questions:
  - What is your role? (new team member, contributor, auditor)
  - What specific areas are you interested in?
  - What is your familiarity with the tech stack?
  - What will you be working on?
  - Any specific concerns or questions?

**Phase 3: Output**
Tailored based on user's needs - could be:
- Architecture overview document
- Onboarding guide
- Specific area deep-dive
- Development workflow guide
