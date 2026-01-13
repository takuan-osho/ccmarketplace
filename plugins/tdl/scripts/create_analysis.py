#!/usr/bin/env python3
"""
Create a new Analysis document with TDL template.

Analysis documents are used for problem exploration and requirements discovery.
They are archived after requirements are formalized.

Usage:
    python create_analysis.py "User Authentication Flow"
    python create_analysis.py "Performance Bottleneck Investigation"
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

from tdl_new_id import generate_unique_id, find_docs_directory


ANALYSIS_TEMPLATE = """# {title}

## Metadata

- **ID**: {id}
- **Type**: Analysis
- **Owner**: [Person or role]
- **Status**: Draft
- **Date**: {date}

## Links

- **Related Analyses**: N/A – [AN-xxxxx]
- **Existing Requirements**: N/A – [FR-xxxxx, NFR-xxxxx]
- **Existing ADRs**: N/A – [ADR-xxxxx]
- **Issue/Discussion**: N/A – [link to issue]

## Executive Summary

[1-2 paragraph summary of the analysis and key findings]

## Problem Space

### Current State

[Description of how things work today]

### Desired State

[Description of the target state]

### Gap Analysis

[What gaps exist between current and desired state?]

| Area | Current | Desired | Gap |
|------|---------|---------|-----|
| [Area 1] | [Current state] | [Desired state] | [Gap description] |

## Stakeholder Analysis

| Stakeholder | Interest | Impact | Priority |
|-------------|----------|--------|----------|
| [Stakeholder 1] | [Their interest] | High/Medium/Low | P0-P3 |

## Research & Discovery

### User Feedback

[Summary of user feedback, interviews, surveys]

### Competitive Analysis

[How do competitors solve this problem?]

### Technical Investigation

[Technical research findings]

### Data Analysis

[Relevant data and metrics]

## Discovered Requirements

### Functional Requirements (Draft)

#### FR-DRAFT-1: [Title]

- **Rationale**: [Why this is needed]
- **Priority**: P0-P3
- **Acceptance Criteria**:
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]

#### FR-DRAFT-2: [Title]

- **Rationale**: [Why this is needed]
- **Priority**: P0-P3
- **Acceptance Criteria**:
  - [ ] [Criterion 1]

### Non-Functional Requirements (Draft)

#### NFR-DRAFT-1: [Title]

- **Rationale**: [Why this is needed]
- **Priority**: P0-P3
- **Target**: [Measurable target]

## Design Considerations

### Technical Constraints

- [Constraint 1]
- [Constraint 2]

### Potential Approaches

1. **Approach A**: [Description]
   - Pros: [List]
   - Cons: [List]

2. **Approach B**: [Description]
   - Pros: [List]
   - Cons: [List]

### Architecture Impact

[How might this affect the system architecture?]

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk 1] | Low/Medium/High | Low/Medium/High | [Strategy] |

## Open Questions

- [ ] Question 1
- [ ] Question 2
- [ ] Question 3

## Recommendations

### Immediate Actions

1. [Action 1]
2. [Action 2]

### Next Steps

1. [Step 1]
2. [Step 2]

### Out of Scope

- [Item deliberately excluded]

## Appendix

### Meeting Notes

[Summary of relevant meetings]

### References

- [External reference 1]
- [External reference 2]

### Raw Data

[Links to or summaries of raw data sources]
"""


def create_filename(title: str, analysis_id: str) -> str:
    """Create analysis filename from title and ID."""
    title_slug = title.lower().replace(" ", "-")
    title_slug = "".join(c for c in title_slug if c.isalnum() or c == "-")
    while "--" in title_slug:
        title_slug = title_slug.replace("--", "-")
    title_slug = title_slug.strip("-")
    return f"AN-{analysis_id}-{title_slug}.md"


def create_analysis(
    title: str,
    path: Path | None = None
) -> None:
    """Create a new analysis file with random ID."""
    # Determine analysis directory
    if path:
        analysis_dir = path / "docs" / "analysis"
        docs_dir = path / "docs"
    else:
        docs_dir = find_docs_directory()
        if docs_dir:
            analysis_dir = docs_dir / "analysis"
        else:
            analysis_dir = Path.cwd() / "docs" / "analysis"
            docs_dir = Path.cwd() / "docs"

    analysis_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique random ID
    try:
        analysis_id = generate_unique_id(docs_dir)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Create filename
    filename = create_filename(title, analysis_id)
    filepath = analysis_dir / filename

    if filepath.exists():
        print(f"Error: Analysis already exists: {filepath}")
        sys.exit(1)

    # Generate content
    content = ANALYSIS_TEMPLATE.format(
        id=f"AN-{analysis_id}",
        title=title,
        date=datetime.now().strftime("%Y-%m-%d")
    )

    filepath.write_text(content)

    print(f"Created Analysis: {filepath}")
    print(f"ID: AN-{analysis_id}")
    print(f"\nNext steps:")
    print(f"1. Edit {filepath}")
    print(f"2. Fill in the Problem Space section")
    print(f"3. Document your research and findings")
    print(f"4. Draft discovered requirements (FR-DRAFT, NFR-DRAFT)")
    print(f"5. When requirements are formalized, update status to Complete")
    print(f"6. Archive the analysis after requirements are created")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Create a new Analysis document"
    )
    parser.add_argument("title", help="Title of the analysis")
    parser.add_argument(
        "--path", "-p",
        type=Path,
        help="Base path for the project (default: current directory)"
    )

    args = parser.parse_args()
    create_analysis(args.title, args.path)


if __name__ == "__main__":
    main()
