#!/usr/bin/env python3
"""
Initialize TDL documentation structure in a project.

Creates the following directory structure:
- docs/analysis/     (Analysis documents - AN-xxxxx)
- docs/requirements/ (Requirements - FR-xxxxx, NFR-xxxxx)
- docs/adr/          (Architecture Decision Records - ADR-xxxxx)
- docs/tasks/        (Task directories - T-xxxxx)
- docs/templates/    (Document templates)
- .github/           (GitHub templates)
"""

import sys
from pathlib import Path


def create_directory_structure(base_path: Path) -> None:
    """Create TDL documentation directory structure."""
    directories = [
        "docs/analysis",
        "docs/analysis/archive",
        "docs/requirements",
        "docs/adr",
        "docs/adr/archive",
        "docs/tasks",
        "docs/templates",
        ".github/ISSUE_TEMPLATE",
    ]

    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created: {directory}/")

    # Create README files
    readme_files = {
        "docs/analysis/README.md": """# Analysis Documents

This directory contains analysis documents for problem exploration and requirements discovery.

## Naming Convention

- `AN-<5-char-id>-topic.md` (e.g., `AN-a3bf2-user-auth-flow.md`)

## ID Generation

Use the `tdl_new_id.py` script or `create_analysis.py` to generate unique IDs:

```bash
python scripts/create_analysis.py "User Authentication Flow"
```

## Lifecycle

1. **Draft**: Initial exploration
2. **Active**: Under investigation
3. **Complete**: Analysis finished, requirements drafted
4. **Archived**: Move to `archive/` after requirements are formalized

## Links Section

Every document must have a Links section with:
- Related Analyses
- Existing Requirements (FR/NFR)
- Existing ADRs
- Issue/Discussion

Use `N/A – <reason>` if a link category doesn't apply.
""",
        "docs/requirements/README.md": """# Requirements Documentation

This directory contains functional (FR) and non-functional (NFR) requirement specifications.

## Naming Convention

- Functional: `FR-<5-char-id>-topic.md` (e.g., `FR-b4cd8-user-authentication.md`)
- Non-Functional: `NFR-<5-char-id>-topic.md` (e.g., `NFR-c5de9-api-response-time.md`)

## ID Generation

Use the `create_requirement.py` script to generate unique IDs:

```bash
python scripts/create_requirement.py "User Authentication" --type FR
python scripts/create_requirement.py "API Response Time" --type NFR --category Performance
```

## Priority Levels

- P0: Critical - Must have for launch
- P1: High - Important feature
- P2: Medium - Nice to have
- P3: Low - Future consideration

## Status Lifecycle

Proposed -> Accepted -> Implemented -> Verified -> (Deprecated)

## Links Section

Every requirement must link to:
- Implementing Tasks (T-xxxxx)
- Related Requirements
- Related ADRs
- Tests
- Issue/PR
""",
        "docs/adr/README.md": """# Architecture Decision Records (ADR)

This directory contains Architecture Decision Records - documents that capture
important architectural decisions made during the project.

## Naming Convention

- `ADR-<5-char-id>-topic.md` (e.g., `ADR-d6ef0-use-postgresql.md`)

## ID Generation

Use the `create_adr.py` script to generate unique IDs:

```bash
python scripts/create_adr.py "Use PostgreSQL for data storage"
python scripts/create_adr.py "Minor API change" --lite
```

## ADR Types

- **Full ADR**: For significant architectural decisions requiring detailed analysis
- **ADR Lite**: For tactical decisions with smaller scope

## Status Lifecycle

Proposed -> Accepted | Rejected -> (Deprecated | Superseded by ADR-xxxxx)

## Links Section

Every ADR must link to:
- Analysis (AN-xxxxx)
- Requirements (FR-xxxxx, NFR-xxxxx)
- Design/Plan documents
- Related ADRs
- Supersedes/Superseded by
""",
        "docs/tasks/README.md": """# Task Directories

This directory contains task-scoped implementation directories.
Each task has its own directory with design and plan documents.

## Naming Convention

- Directory: `T-<5-char-id>-topic/` (e.g., `T-e7fa1-implement-auth/`)
- Files inside:
  - `design.md`: Technical design for implementation
  - `plan.md`: Implementation plan with phases

## Creating Tasks

Use the `create_task.py` script:

```bash
python scripts/create_task.py "implement-user-auth" --requirements FR-a1b2c,FR-d3e4f
```

## Task Structure

```
T-xxxxx-topic/
├── design.md    # How to implement (technical design)
└── plan.md      # What to do (phased implementation plan)
```

## Plan Status

Not Started -> Phase X In Progress -> Blocked -> Under Review -> Completed

## Links Section

Both design.md and plan.md must link to:
- Requirements (FR-xxxxx, NFR-xxxxx)
- Relevant ADRs
- Issue/PR
""",
    }

    for file_path, content in readme_files.items():
        full_path = base_path / file_path
        if not full_path.exists():
            full_path.write_text(content)
            print(f"Created: {file_path}")
        else:
            print(f"Skipped (exists): {file_path}")


def create_github_templates(base_path: Path) -> None:
    """Create GitHub issue and PR templates."""

    pr_template = """## What does this PR do?

[Brief description of the changes]

## Changes Made

- [Change 1]
- [Change 2]

## Traceability

- **Requirements**: [FR-xxxxx, NFR-xxxxx or N/A]
- **Design**: [Link to task design.md or N/A]
- **ADR**: [ADR-xxxxx or N/A]
- **Issue**: #[issue number]

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Verification

```bash
# Commands to verify this PR
```

## Checklist

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Links section updated in relevant TDL documents
"""

    bug_template = """---
name: Bug Report
about: Report a bug to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## Description

[Clear and concise description of the bug]

## Steps to Reproduce

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior

[What should happen]

## Actual Behavior

[What actually happens]

## Environment

- Version/Commit:
- OS:
- Platform:

## Traceability

- Related requirement: [FR-xxxxx or N/A]
- Related ADR: [ADR-xxxxx or N/A]
- Trace ID (if applicable):

## Additional Context

[Screenshots, logs, etc.]
"""

    feature_template = """---
name: Feature Request
about: Suggest a new feature
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Feature Description

[What feature would you like to see?]

## Use Case

[Why is this feature needed?]

## Proposed Solution

[How do you think this should work?]

## TDL Documentation Required

- [ ] Analysis document (AN-xxxxx) needed
- [ ] Requirements (FR/NFR) needed
- [ ] ADR needed for design decisions
- [ ] Task with design/plan needed

## Success Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Related Items

- Existing requirements: [FR-xxxxx or N/A]
- Existing ADRs: [ADR-xxxxx or N/A]
"""

    templates = {
        ".github/PULL_REQUEST_TEMPLATE.md": pr_template,
        ".github/ISSUE_TEMPLATE/bug_report.md": bug_template,
        ".github/ISSUE_TEMPLATE/feature_request.md": feature_template,
    }

    for file_path, content in templates.items():
        full_path = base_path / file_path
        if not full_path.exists():
            full_path.write_text(content)
            print(f"Created: {file_path}")
        else:
            print(f"Skipped (exists): {file_path}")


def main():
    """Main execution function."""
    if len(sys.argv) > 1:
        base_path = Path(sys.argv[1])
    else:
        base_path = Path.cwd()

    if not base_path.exists():
        print(f"Error: Path does not exist: {base_path}")
        sys.exit(1)

    print(f"Initializing TDL documentation structure in: {base_path}\n")

    create_directory_structure(base_path)
    create_github_templates(base_path)

    print(f"\nTDL documentation structure initialized successfully!")
    print(f"\nNext steps:")
    print(f"1. Create your first analysis: python scripts/create_analysis.py 'Topic'")
    print(f"2. Create requirements: python scripts/create_requirement.py 'Title' --type FR")
    print(f"3. Create ADRs: python scripts/create_adr.py 'Decision Title'")
    print(f"4. Create tasks: python scripts/create_task.py 'task-name'")
    print(f"5. Check traceability: python scripts/trace_status.py")


if __name__ == "__main__":
    main()
