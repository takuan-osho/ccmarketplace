#!/usr/bin/env python3
"""
Create a new Task directory with design.md and plan.md templates.

Tasks are the implementation units in TDL that contain both design and plan documents.

Usage:
    python create_task.py "implement-user-auth"
    python create_task.py "cache-refresh" --requirements FR-a1b2c,FR-d3e4f
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

from tdl_new_id import generate_unique_id, find_docs_directory


DESIGN_TEMPLATE = """# {title} - Design

## Metadata

- **ID**: {id}
- **Type**: Design
- **Owner**: [Person or role]
- **Reviewers**: [List of reviewers]
- **Status**: Draft
- **Date**: {date}

## Links

- **Requirements**: {requirements}
- **Relevant ADRs**: N/A – [ADR-xxxxx]
- **Issue**: N/A – [link to issue]
- **PR**: N/A – [link to PR]

## Requirements Summary

[Brief summary of the requirements being implemented]

### Requirements Mapping

| Requirement | Design Element | Notes |
|-------------|---------------|-------|
| [FR-xxxxx] | [Component/Module] | [How it's addressed] |

## Component Design

### Overview

[High-level design overview]

### Architecture

```
[ASCII diagram or description of component architecture]
```

### Key Components

#### Component 1: [Name]

- **Purpose**: [What it does]
- **Interface**: [Public API]
- **Dependencies**: [What it depends on]

## Data Flows

### Primary Flow

```
[Data flow diagram or description]
```

### Edge Cases

- [Edge case 1]: [How handled]
- [Edge case 2]: [How handled]

## APIs

### Public API

```python
# Example API signatures
def function_name(param: Type) -> ReturnType:
    \"\"\"Description.\"\"\"
    pass
```

### Internal API

[Internal interfaces between components]

## Error Handling Strategy

| Error Condition | Detection | Response | Recovery |
|-----------------|-----------|----------|----------|
| [Error 1] | [How detected] | [Action taken] | [Recovery steps] |

## Platform Differences

### Unix

- [Specific considerations]

### Windows

- [Specific considerations]

### Cross-Platform

- [Shared considerations]

## Testing Strategy

### Unit Tests

- [What to test at unit level]

### Integration Tests

- [What to test at integration level]

### External API Parsing Tests

- [Tests for external data parsing]

## Acceptance/Success Metrics

- [ ] Metric 1: [Specific, measurable criterion]
- [ ] Metric 2: [Specific, measurable criterion]

## Open Questions

- [ ] Question 1
- [ ] Question 2

## External References

- [Link to external reference]
"""


PLAN_TEMPLATE = """# {title} - Implementation Plan

## Metadata

- **ID**: {id}
- **Type**: Implementation Plan
- **Owner**: [Person or role]
- **Reviewers**: [List of reviewers]
- **Status**: Not Started
- **Date**: {date}

## Links

- **Requirements**: {requirements}
- **Design**: [design.md](./design.md)
- **Related ADRs**: N/A – [ADR-xxxxx]
- **Issue**: N/A – [link to issue]
- **PR**: N/A – [link to PR]

## Overview

[Brief overview of what this implementation accomplishes]

## Success Metrics

- [ ] [Metric 1]
- [ ] [Metric 2]

## Scope

### Goal

[Primary objective of this implementation]

### Non-Goals

- [What is explicitly NOT in scope]

### Assumptions

- [Assumption 1]
- [Assumption 2]

### Constraints

- [Constraint 1]
- [Constraint 2]

## Plan Summary

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | [Phase 1 name] | Not Started |
| 2 | [Phase 2 name] | Not Started |
| 3 | [Phase 3 name] | Not Started |

---

## Phase 1: [Name]

### Goal

[What this phase accomplishes]

### Inputs

- [What's needed to start]

### Tasks

- [ ] Task 1.1: [Description]
- [ ] Task 1.2: [Description]
- [ ] Task 1.3: [Description]

### Deliverables

- [Concrete output 1]
- [Concrete output 2]

### Verification

```bash
# Commands to verify this phase
```

### Acceptance Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]

### Rollback

[How to roll back if needed]

---

## Phase 2: [Name]

### Goal

[What this phase accomplishes]

### Inputs

- Output from Phase 1

### Tasks

- [ ] Task 2.1: [Description]
- [ ] Task 2.2: [Description]

### Deliverables

- [Concrete output]

### Verification

```bash
# Commands to verify this phase
```

### Acceptance Criteria

- [ ] [Criterion 1]

### Rollback

[How to roll back if needed]

---

## Phase 3: [Name]

### Goal

[What this phase accomplishes]

### Inputs

- Output from Phase 2

### Tasks

- [ ] Task 3.1: [Description]
- [ ] Task 3.2: [Description]

### Deliverables

- [Concrete output]

### Verification

```bash
# Commands to verify this phase
```

### Acceptance Criteria

- [ ] [Criterion 1]

### Rollback

[How to roll back if needed]

---

## Testing Strategy

### Unit Tests

- [ ] [Test area 1]
- [ ] [Test area 2]

### Integration Tests

- [ ] [Test area 1]

### API Tests

- [ ] [Test area 1]

### Performance Tests

- [ ] [Test area 1]

## Platform Matrix

| Platform | Tested | Notes |
|----------|--------|-------|
| Linux | [ ] | |
| macOS | [ ] | |
| Windows | [ ] | |

## Dependencies

### External

- [External dependency 1]

### Internal

- [Internal dependency 1]

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk 1] | Low/Medium/High | Low/Medium/High | [Strategy] |

## Documentation & Change Management

### CLI Changes

- [ ] [Change 1]

### Behavior Changes

- [ ] [Change 1]

### ADR Impact

- [ ] [Any ADR updates needed]

## Implementation Guidelines

### Error Handling

- [Guidelines for error handling]

### Naming Conventions

- [Naming guidelines]

### Safety Considerations

- [Safety guidelines]

## Definition of Done (DoD)

All items must pass before completion:

- [ ] All tasks completed
- [ ] All tests pass
- [ ] Code review approved
- [ ] Documentation updated
- [ ] Links section updated with PR

## Status Tracking

| Date | Status | Notes |
|------|--------|-------|
| {date} | Created | Initial plan |

## Open Questions

- [ ] Question 1
- [ ] Question 2

## Visual/UI Reference (Optional)

[Screenshots or mockups if applicable]
"""


def create_task(
    topic: str,
    requirements: str | None = None,
    path: Path | None = None
) -> None:
    """Create a new task directory with design.md and plan.md."""
    # Determine tasks directory
    if path:
        tasks_dir = path / "docs" / "tasks"
        docs_dir = path / "docs"
    else:
        docs_dir = find_docs_directory()
        if docs_dir:
            tasks_dir = docs_dir / "tasks"
        else:
            tasks_dir = Path.cwd() / "docs" / "tasks"
            docs_dir = Path.cwd() / "docs"

    tasks_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique random ID
    try:
        task_id = generate_unique_id(docs_dir)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Create task directory name
    topic_slug = topic.lower().replace(" ", "-")
    topic_slug = "".join(c for c in topic_slug if c.isalnum() or c == "-")
    while "--" in topic_slug:
        topic_slug = topic_slug.replace("--", "-")
    topic_slug = topic_slug.strip("-")

    task_dir_name = f"T-{task_id}-{topic_slug}"
    task_dir = tasks_dir / task_dir_name

    if task_dir.exists():
        print(f"Error: Task directory already exists: {task_dir}")
        sys.exit(1)

    task_dir.mkdir(parents=True)

    # Format requirements link
    req_links = requirements if requirements else "N/A – [FR-xxxxx, NFR-xxxxx]"

    date = datetime.now().strftime("%Y-%m-%d")
    title = topic.replace("-", " ").title()

    # Create design.md
    design_content = DESIGN_TEMPLATE.format(
        id=f"T-{task_id}",
        title=title,
        date=date,
        requirements=req_links
    )
    (task_dir / "design.md").write_text(design_content)

    # Create plan.md
    plan_content = PLAN_TEMPLATE.format(
        id=f"T-{task_id}",
        title=title,
        date=date,
        requirements=req_links
    )
    (task_dir / "plan.md").write_text(plan_content)

    print(f"Created Task: {task_dir}")
    print(f"ID: T-{task_id}")
    print(f"\nFiles created:")
    print(f"  - {task_dir}/design.md")
    print(f"  - {task_dir}/plan.md")
    print(f"\nNext steps:")
    print(f"1. Edit design.md to document how you'll implement the requirements")
    print(f"2. Edit plan.md to break down the implementation into phases")
    print(f"3. Update the Links sections with requirement IDs")
    print(f"4. Update status as you progress through phases")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Create a new Task directory with design and plan documents"
    )
    parser.add_argument("topic", help="Topic/name of the task (e.g., 'implement-user-auth')")
    parser.add_argument(
        "--requirements", "-r",
        help="Comma-separated requirement IDs (e.g., 'FR-a1b2c,NFR-d3e4f')"
    )
    parser.add_argument(
        "--path", "-p",
        type=Path,
        help="Base path for the project (default: current directory)"
    )

    args = parser.parse_args()
    create_task(args.topic, args.requirements, args.path)


if __name__ == "__main__":
    main()
