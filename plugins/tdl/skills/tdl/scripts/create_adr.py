#!/usr/bin/env python3
"""
Create a new Architecture Decision Record (ADR) with proper TDL template.

Uses random Base36 IDs for parallel development support.
Supports both Full and Lite ADR formats.

Usage:
    python create_adr.py "Use PostgreSQL for data storage"
    python create_adr.py "Use PostgreSQL for data storage" --lite
    python create_adr.py "Minor API change" --lite
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from tdl_new_id import find_docs_directory, generate_unique_id

ADR_TEMPLATE_FULL = """# {title}

## Metadata

- **ID**: {id}
- **Type**: ADR
- **Owner**: [Person or role]
- **Reviewers**: [List of reviewers]
- **Status**: Proposed
- **Date**: {date}

## Links

- **Analysis**: N/A – [reason if none]
- **Requirements**: N/A – [FR-xxxxx, NFR-xxxxx]
- **Design**: N/A – [link to design doc]
- **Plan**: N/A – [link to plan doc]
- **Related ADRs**: N/A – [ADR-xxxxx]
- **Issue**: N/A – [link to issue]
- **PR**: N/A – [link to PR]
- **Supersedes**: N/A – [ADR-xxxxx if replacing another]
- **Superseded by**: N/A – [ADR-xxxxx if replaced]

## Context

[Describe the context and problem statement. What forces are at play?
What are the constraints? What assumptions are being made?]

## Success Metrics (Optional)

[How will we measure the success of this decision?]

- [ ] Metric 1
- [ ] Metric 2

## Decision

### Decision Drivers

- [Driver 1: e.g., Performance requirements]
- [Driver 2: e.g., Team expertise]
- [Driver 3: e.g., Cost constraints]

### Options Considered

#### Option 1: [Name]

[Description]

**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

#### Option 2: [Name]

[Description]

**Pros:**
- [Pro 1]

**Cons:**
- [Con 1]

#### Option 3: [Name]

[Description]

**Pros:**
- [Pro 1]

**Cons:**
- [Con 1]

### Analysis

[Comparative analysis of options against decision drivers]

### Decision Outcome

**Chosen option: [Selected Option]**

[Justification for the choice]

## Rationale

[Detailed explanation of why this option was chosen, including trade-offs considered]

## Consequences

### Positive

- [e.g., improvement of quality attribute satisfaction]
- [e.g., enables future features]

### Negative

- [e.g., compromising quality attribute]
- [e.g., technical debt introduced]

### Neutral

- [e.g., requires team training]
- [e.g., changes development workflow]

## Implementation Notes (Optional)

[How will this decision be implemented? Any specific steps or considerations?]

## Examples (Optional)

[Code examples or diagrams illustrating the decision]

## Platform Considerations

[If applicable: differences for Unix, Windows, Cross-Platform]

## Security & Privacy

[If applicable: security implications and mitigations]

## Monitoring & Logging

[If applicable: observability considerations]

## Open Questions

- [ ] Question 1
- [ ] Question 2

## External References

- [Link to external reference 1]
- [Link to external reference 2]
"""


ADR_TEMPLATE_LITE = """# {title}

## Metadata

- **ID**: {id}
- **Type**: ADR (Lite)
- **Owner**: [Person or role]
- **Reviewers**: [List of reviewers]
- **Status**: Proposed
- **Date**: {date}

## Links

- **Analysis**: N/A – [reason if none]
- **Requirements**: N/A – [FR-xxxxx, NFR-xxxxx]
- **Design**: N/A – [link to design doc]
- **Plan**: N/A – [link to plan doc]
- **Related ADRs**: N/A – [ADR-xxxxx]
- **Issue**: N/A – [link to issue]
- **PR**: N/A – [link to PR]
- **Supersedes**: N/A – [ADR-xxxxx if replacing another]
- **Superseded by**: N/A – [ADR-xxxxx if replaced]

## Context

[Brief description of the context and problem]

## Success Metrics (Optional)

[How will we measure success?]

## Decision

**Chosen approach: [Selected approach]**

[What was decided and why]

## Consequences

### Positive

- [Positive outcome 1]

### Negative

- [Negative outcome 1]

## Open Questions (Optional)

- [ ] Question 1

## External References (Optional)

- [Link to external reference]
"""


def create_filename(title: str, adr_id: str) -> str:
    """Create ADR filename from title and ID."""
    title_slug = title.lower().replace(" ", "-")
    title_slug = "".join(c for c in title_slug if c.isalnum() or c == "-")
    while "--" in title_slug:
        title_slug = title_slug.replace("--", "-")
    title_slug = title_slug.strip("-")
    return f"ADR-{adr_id}-{title_slug}.md"


def escape_braces(value: str) -> str:
    """Escape braces so str.format does not treat them as placeholders."""
    return value.replace("{", "{{").replace("}", "}}")


def resolve_docs_dir(base_path: Path | None) -> Path:
    """Resolve docs/ directory from an optional base path."""
    if base_path:
        return base_path / "docs"

    docs_dir = find_docs_directory()
    if docs_dir:
        return docs_dir

    return Path.cwd() / "docs"


def create_adr(title: str, lite: bool = False, path: Path | None = None) -> None:
    """Create a new ADR file with random ID."""
    docs_dir = resolve_docs_dir(path)
    adr_dir = docs_dir / "adr"

    adr_dir.mkdir(parents=True, exist_ok=True)

    try:
        adr_id = generate_unique_id(docs_dir)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    filename = create_filename(title, adr_id)
    filepath = adr_dir / filename

    if filepath.exists():
        print(f"Error: ADR already exists: {filepath}")
        sys.exit(1)

    template = ADR_TEMPLATE_LITE if lite else ADR_TEMPLATE_FULL
    safe_title = escape_braces(title)
    content = template.format(
        id=f"ADR-{adr_id}", title=safe_title, date=datetime.now().strftime("%Y-%m-%d")
    )

    filepath.write_text(content, encoding="utf-8")

    template_type = "Lite" if lite else "Full"
    print(f"Created ADR ({template_type}): {filepath}")
    print(f"ID: ADR-{adr_id}")
    print("\nNext steps:")
    print(f"1. Edit {filepath}")
    print("2. Fill in the Context section")
    print("3. Document the decision and rationale")
    print("4. Update Links section with related documents")
    print("5. Update status when decided (Proposed -> Accepted/Rejected)")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Create a new Architecture Decision Record (ADR)"
    )
    parser.add_argument("title", help="Title of the ADR")
    parser.add_argument(
        "--lite",
        "-l",
        action="store_true",
        help="Use the Lite ADR template for tactical decisions",
    )
    parser.add_argument(
        "--path",
        "-p",
        type=Path,
        help="Base path for the project (default: current directory)",
    )

    args = parser.parse_args()
    create_adr(args.title, args.lite, args.path)


if __name__ == "__main__":
    main()
