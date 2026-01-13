#!/usr/bin/env python3
"""
Create a new Requirement document (Functional or Non-Functional) with TDL template.

Uses random Base36 IDs for parallel development support.

Usage:
    python create_requirement.py "User Authentication" --type FR
    python create_requirement.py "Performance under load" --type NFR
    python create_requirement.py "API Response Time" --type NFR --category Performance
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

from tdl_new_id import generate_unique_id, find_docs_directory


REQUIREMENT_TEMPLATE = """# {title}

## Metadata

- **ID**: {id}
- **Type**: {req_type}
- **Category**: {category}
- **Priority**: P2 (Medium)
- **Owner**: [Person or role]
- **Reviewers**: [List of reviewers]
- **Status**: Proposed
- **Date**: {date}

## Links

- **Implemented by Tasks**: N/A – [T-xxxxx]
- **Related Requirements**: N/A – [FR-xxxxx, NFR-xxxxx]
- **Related ADRs**: N/A – [ADR-xxxxx]
- **Tests**: N/A – [link to test files]
- **Issue**: N/A – [link to issue]
- **PR**: N/A – [link to PR]

## Requirement Statement

[Clear, specific, and measurable statement of the requirement.
What MUST the system do? Use "shall" or "must" for mandatory requirements.]

## Rationale

[Why is this requirement needed? What problem does it solve?]

## User Story

As a [role],
I want [capability],
So that [benefit].

## Acceptance Criteria

- [ ] Criterion 1: [Specific, testable condition]
- [ ] Criterion 2: [Specific, testable condition]
- [ ] Criterion 3: [Specific, testable condition]

## Technical Details

{technical_section}

## Verification Method

### Test Strategy

[How will this requirement be verified?]

- [ ] Unit tests
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Manual testing

### Verification Commands

```bash
# Commands to verify this requirement
```

### Success Metrics

[Quantifiable metrics for success]

## Dependencies

### Depends On

- N/A – [List requirements this depends on]

### Blocks

- N/A – [List requirements that depend on this]

## Platform Considerations

- **Unix**: [Specific considerations]
- **Windows**: [Specific considerations]
- **Cross-Platform**: [Shared considerations]

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk 1] | Low/Medium/High | Low/Medium/High | [Mitigation strategy] |

## Implementation Notes

[Any notes for implementers]

## External References

- [Link to external reference]
"""

FR_TECHNICAL_SECTION = """### Functional Specification

[Detailed functional behavior]

### Input/Output

- **Input**: [What the system receives]
- **Output**: [What the system produces]
- **Side Effects**: [Any state changes]

### Error Handling

- [Error condition 1]: [How to handle]
- [Error condition 2]: [How to handle]"""

NFR_TECHNICAL_SECTION = """### Performance Targets

- **Response Time**: [Target, e.g., < 100ms]
- **Throughput**: [Target, e.g., 1000 req/s]
- **Resource Usage**: [Target, e.g., < 512MB RAM]

### Quality Attributes

- **Reliability**: [Target, e.g., 99.9% uptime]
- **Scalability**: [Target, e.g., 10x current load]
- **Security**: [Specific requirements]

### Measurement Method

[How will these metrics be measured and monitored?]"""


def create_filename(title: str, req_id: str, prefix: str) -> str:
    """Create requirement filename from title and ID."""
    title_slug = title.lower().replace(" ", "-")
    title_slug = "".join(c for c in title_slug if c.isalnum() or c == "-")
    while "--" in title_slug:
        title_slug = title_slug.replace("--", "-")
    title_slug = title_slug.strip("-")
    return f"{prefix}-{req_id}-{title_slug}.md"


def create_requirement(
    title: str,
    req_type: str = "FR",
    category: str = "General",
    path: Path | None = None
) -> None:
    """Create a new requirement file with random ID."""
    prefix = req_type.upper()
    if prefix not in ["FR", "NFR"]:
        print(f"Error: Invalid requirement type '{req_type}'. Use 'FR' or 'NFR'.")
        sys.exit(1)

    type_name = "Functional Requirement" if prefix == "FR" else "Non-Functional Requirement"
    technical_section = FR_TECHNICAL_SECTION if prefix == "FR" else NFR_TECHNICAL_SECTION

    # Determine requirements directory
    if path:
        req_dir = path / "docs" / "requirements"
        docs_dir = path / "docs"
    else:
        docs_dir = find_docs_directory()
        if docs_dir:
            req_dir = docs_dir / "requirements"
        else:
            req_dir = Path.cwd() / "docs" / "requirements"
            docs_dir = Path.cwd() / "docs"

    req_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique random ID
    try:
        req_id = generate_unique_id(docs_dir)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Create filename
    filename = create_filename(title, req_id, prefix)
    filepath = req_dir / filename

    if filepath.exists():
        print(f"Error: Requirement already exists: {filepath}")
        sys.exit(1)

    # Generate content
    content = REQUIREMENT_TEMPLATE.format(
        id=f"{prefix}-{req_id}",
        title=title,
        req_type=type_name,
        category=category,
        date=datetime.now().strftime("%Y-%m-%d"),
        technical_section=technical_section
    )

    filepath.write_text(content)

    print(f"Created {type_name}: {filepath}")
    print(f"ID: {prefix}-{req_id}")
    print(f"\nNext steps:")
    print(f"1. Edit {filepath}")
    print(f"2. Fill in the Requirement Statement")
    print(f"3. Define clear Acceptance Criteria")
    print(f"4. Update Links section with related documents")
    print(f"5. Update status when approved (Proposed -> Accepted)")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Create a new Requirement document"
    )
    parser.add_argument("title", help="Title of the requirement")
    parser.add_argument(
        "--type", "-t",
        choices=["FR", "NFR"],
        default="FR",
        help="Requirement type: FR (Functional) or NFR (Non-Functional)"
    )
    parser.add_argument(
        "--category", "-c",
        default="General",
        help="Category (e.g., Performance, Security, Usability)"
    )
    parser.add_argument(
        "--path", "-p",
        type=Path,
        help="Base path for the project (default: current directory)"
    )

    args = parser.parse_args()
    create_requirement(args.title, args.type, args.category, args.path)


if __name__ == "__main__":
    main()
