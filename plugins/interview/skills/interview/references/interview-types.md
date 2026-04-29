# Interview Types Reference

This document provides detailed question sets and strategies for each interview type.

## Requirements Interview

### Goal
Gather comprehensive requirements for new features, APIs, or specifications.

### Question Framework

**Phase 1: Understanding the Problem**
1. What problem are we trying to solve?
2. Who experiences this problem? (End users, developers, operators)
3. How is this problem currently handled?
4. What is the impact of not solving this problem?

**Phase 2: Solution Scope**
1. What does the ideal solution look like?
2. What are the minimum requirements (MVP)?
3. What is explicitly out of scope?
4. Are there any related systems or features affected?

**Phase 3: Technical Details**
1. What data inputs are needed?
2. What outputs are expected?
3. What are the performance requirements? (Latency, throughput)
4. What error scenarios should be handled?
5. What security considerations exist?

**Phase 4: Acceptance Criteria**
1. How will we know when this is complete?
2. What tests should pass?
3. What documentation is needed?

### Output Structure
```markdown
## Feature: [Name]

### Problem Statement
[Clear description of the problem]

### Requirements
#### Must Have (P0)
- [ ] Requirement 1
- [ ] Requirement 2

#### Should Have (P1)
- [ ] Requirement 3

#### Could Have (P2)
- [ ] Requirement 4

### Technical Specifications
- Input: [Description]
- Output: [Description]
- Constraints: [Performance, security, etc.]

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

---

## Investigation Interview

### Goal
Systematically diagnose bugs, performance issues, or incidents.

### Question Framework

**Phase 1: Symptom Collection**
1. What is the exact error message or behavior?
2. When did this first occur?
3. What is the frequency? (Always, intermittent, specific conditions)
4. What is the impact? (Users affected, severity)

**Phase 2: Context Gathering**
1. What changed recently? (Deployments, config changes, traffic patterns)
2. Which environment is affected? (Dev, staging, production)
3. Are there related issues or errors?
4. What has already been tried?

**Phase 3: Reproduction**
1. What are the exact steps to reproduce?
2. What is the expected behavior?
3. What is the actual behavior?
4. Can this be reproduced locally?

**Phase 4: Data Collection**
1. What logs are available?
2. What metrics show anomalies?
3. What traces or request IDs are relevant?

### Output Structure
```markdown
## Investigation: [Issue Title]

### Symptom
- Error/Behavior: [Description]
- First occurrence: [Timestamp]
- Frequency: [Pattern]
- Impact: [Users/systems affected]

### Timeline
| Time | Event |
|------|-------|
| [T1] | [Event 1] |
| [T2] | [Event 2] |

### Hypotheses
1. **[Hypothesis 1]** - [Evidence for/against]
2. **[Hypothesis 2]** - [Evidence for/against]

### Next Steps
1. [ ] Action 1
2. [ ] Action 2

### References
- Logs: [Link]
- Metrics: [Link]
```

---

## Architecture Interview

### Goal
Evaluate design decisions, technology choices, or system evolution.

### Question Framework

**Phase 1: Current State**
1. What is the current architecture?
2. What are the pain points or limitations?
3. What is working well that should be preserved?
4. What are the current scale/performance characteristics?

**Phase 2: Future State**
1. What is the target state or goal?
2. What scale/load is expected in the future?
3. What new capabilities are needed?
4. What is the timeline for changes?

**Phase 3: Constraints**
1. What are the non-negotiable requirements?
2. What budget/resource constraints exist?
3. What team capabilities are available?
4. What dependencies or integrations must be considered?

**Phase 4: Trade-offs**
1. What are you willing to sacrifice for X?
2. How important is [consistency vs availability / latency vs cost / etc.]?
3. What risks are acceptable?

### Output Structure
```markdown
## Architecture Review: [System/Component]

### Current State
- Architecture overview
- Pain points
- What works well

### Proposed Changes
| Option | Pros | Cons |
|--------|------|------|
| Option A | [Pros] | [Cons] |
| Option B | [Pros] | [Cons] |

### Recommendation
[Selected option with rationale]

### Implementation Plan
1. Phase 1: [Scope]
2. Phase 2: [Scope]

### Risks
- Risk 1: [Mitigation]
- Risk 2: [Mitigation]
```

---

## Security Interview

### Goal
Identify security requirements, threats, and controls.

### Question Framework

**Phase 1: Asset Identification**
1. What data/systems need protection?
2. What is the sensitivity/classification of the data?
3. Who are the authorized users?
4. What are the compliance requirements?

**Phase 2: Threat Modeling**
1. Who are potential attackers? (Internal, external, nation-state)
2. What attack vectors are most likely?
3. What would be the impact of a breach?
4. What is the threat landscape for this domain?

**Phase 3: Current Controls**
1. What security controls are already in place?
2. What authentication/authorization exists?
3. What logging/monitoring is available?
4. What incident response processes exist?

**Phase 4: Requirements**
1. What new controls are needed?
2. What security standards must be met?
3. What is the acceptable risk level?

### Output Structure
```markdown
## Security Assessment: [System/Feature]

### Assets
| Asset | Sensitivity | Owner |
|-------|-------------|-------|
| [Asset 1] | [Level] | [Team] |

### Threat Model
| Threat | Likelihood | Impact | Risk |
|--------|------------|--------|------|
| [Threat 1] | High/Med/Low | High/Med/Low | [Score] |

### Controls
#### Existing
- Control 1

#### Required
- [ ] Control 2

### Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
```

---

## Documentation Interview

### Goal
Gather requirements for creating effective documentation.

### Question Framework

**Phase 1: Audience**
1. Who is the primary audience?
2. What is their technical level?
3. What do they need to accomplish?
4. What do they already know?

**Phase 2: Content**
1. What topics must be covered?
2. What is the appropriate level of detail?
3. What examples or samples are helpful?
4. What formats are preferred? (Text, diagrams, video)

**Phase 3: Context**
1. What existing documentation should be referenced or updated?
2. Where will this documentation live?
3. Who will maintain it?
4. What is the review/approval process?

### Output Structure
```markdown
## Documentation Plan: [Topic]

### Audience
- Primary: [Description]
- Secondary: [Description]

### Content Outline
1. Section 1
   - Subsection A
   - Subsection B
2. Section 2

### Format
- Type: [Guide/Reference/Tutorial]
- Length: [Estimated]
- Includes: [Diagrams/Examples/Code samples]

### Location
- Repository: [Path]
- Review process: [Description]
```

---

## General Interview

### Goal
Open-ended exploration when the interview type is unclear or mixed.

### Approach
1. Start with broad questions to understand context
2. Identify which specialized interview type(s) apply
3. Transition to appropriate question frameworks
4. Synthesize findings across multiple dimensions

### Starting Questions
1. What brings you here today?
2. What are you trying to accomplish?
3. What have you already tried or considered?
4. What would success look like?
5. What constraints or concerns do you have?
