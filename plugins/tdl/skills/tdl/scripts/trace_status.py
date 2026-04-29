#!/usr/bin/env python3
"""
Analyze TDL traceability status across the project.

Scans all TDL documents and reports on coverage, gaps, and linkage status.
Implements distributed traceability by parsing Links sections from each document.

Usage:
    python trace_status.py                    # Show status summary
    python trace_status.py --verbose          # Show detailed report
    python trace_status.py --check            # CI mode - exit 1 if gaps found
    python trace_status.py --format markdown  # Output as markdown
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Document:
    """Represents a TDL document with its metadata and links."""

    id: str
    doc_type: str
    title: str
    path: Path
    status: str = "Unknown"
    links: dict[str, list[str]] = field(default_factory=dict)
    raw_content: str = ""


@dataclass
class TraceabilityReport:
    """Summary of traceability analysis."""

    total_documents: int = 0
    analyses: list[Document] = field(default_factory=list)
    requirements: list[Document] = field(default_factory=list)
    adrs: list[Document] = field(default_factory=list)
    tasks: list[Document] = field(default_factory=list)
    orphan_requirements: list[Document] = field(default_factory=list)
    orphan_tasks: list[Document] = field(default_factory=list)
    missing_links: list[str] = field(default_factory=list)
    coverage_percent: float = 0.0


# Patterns for extracting document information
ID_PATTERN = re.compile(r"(AN|FR|NFR|ADR|T)-([a-z0-9]{5})", re.IGNORECASE)
METADATA_SECTION_PATTERN = re.compile(r"## Metadata\s*\n(.*?)(?=\n## |\Z)", re.DOTALL)
METADATA_PATTERN = re.compile(r"\*\*([^*]+)\*\*:\s*(.+)", re.MULTILINE)
LINK_PATTERN = re.compile(r"\*\*([^*]+)\*\*:\s*(.+)", re.MULTILINE)
STATUS_PATTERN = re.compile(r"\*\*Status\*\*:\s*([^\n]+)", re.IGNORECASE)


def find_docs_directory(start_path: Path | None = None) -> Path | None:
    """Find the docs/ directory by searching up from the start path."""
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()
    while current != current.parent:
        docs_path = current / "docs"
        if docs_path.is_dir():
            return docs_path
        current = current.parent

    docs_path = current / "docs"
    if docs_path.is_dir():
        return docs_path

    return None


def extract_document_type(filename: str) -> str | None:
    """Extract document type from filename prefix."""
    prefixes = {
        "AN-": "Analysis",
        "FR-": "Functional Requirement",
        "NFR-": "Non-Functional Requirement",
        "ADR-": "ADR",
        "T-": "Task",
    }
    for prefix, doc_type in prefixes.items():
        if filename.upper().startswith(prefix):
            return doc_type
    return None


def extract_id(filename: str) -> str | None:
    """Extract TDL ID from filename."""
    match = ID_PATTERN.search(filename)
    if match:
        return f"{match.group(1).upper()}-{match.group(2).lower()}"
    return None


def normalize_doc_type(doc_type: str) -> str:
    """Normalize document type labels for reporting."""
    normalized = doc_type.strip()
    if normalized.upper().startswith("ADR"):
        return "ADR"
    return normalized


def parse_metadata_section(content: str) -> dict[str, str]:
    """Parse the Metadata section from document content."""
    metadata_match = METADATA_SECTION_PATTERN.search(content)
    if not metadata_match:
        return {}

    metadata = {}
    for match in METADATA_PATTERN.finditer(metadata_match.group(1)):
        key = match.group(1).strip()
        value = match.group(2).strip()
        metadata[key] = value
    return metadata


def parse_links_section(content: str) -> dict[str, list[str]]:
    """Parse the Links section from document content."""
    links: dict[str, list[str]] = {}

    # Find Links section
    links_match = re.search(r"## Links\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if not links_match:
        return links

    links_content = links_match.group(1)

    # Extract each link
    for match in LINK_PATTERN.finditer(links_content):
        link_type = match.group(1).strip()
        link_value = match.group(2).strip()

        # Skip N/A links
        if link_value.startswith("N/A"):
            continue

        # Extract IDs from the value
        found_ids = ID_PATTERN.findall(link_value)
        if found_ids:
            links[link_type] = [
                f"{prefix.upper()}-{id_part.lower()}" for prefix, id_part in found_ids
            ]

    return links


def parse_document(filepath: Path) -> Document | None:
    """Parse a TDL document and extract its metadata."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    filename = filepath.name
    metadata = parse_metadata_section(content)
    doc_type = extract_document_type(filename)
    doc_id = extract_id(filename)

    if not doc_id:
        doc_id = extract_id(metadata.get("ID", ""))

    if not doc_type:
        metadata_type = metadata.get("Type", "")
        if metadata_type:
            doc_type = normalize_doc_type(metadata_type)

    if not doc_type or not doc_id:
        return None

    # Extract title (first H1)
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else filename

    # Extract status
    status = metadata.get("Status")
    if not status:
        status_match = STATUS_PATTERN.search(content)
        status = status_match.group(1) if status_match else "Unknown"
    status = status.strip()

    # Parse links
    links = parse_links_section(content)

    return Document(
        id=doc_id,
        doc_type=doc_type,
        title=title,
        path=filepath,
        status=status,
        links=links,
        raw_content=content,
    )


def scan_documents(docs_dir: Path) -> list[Document]:
    """Scan all TDL documents in the docs directory."""
    documents: list[Document] = []

    def add_parsed_documents(paths: list[Path]) -> None:
        for path in paths:
            doc = parse_document(path)
            if doc:
                documents.append(doc)

    analysis_dir = docs_dir / "analysis"
    if analysis_dir.exists():
        add_parsed_documents(list(analysis_dir.glob("AN-*.md")))

    req_dir = docs_dir / "requirements"
    if req_dir.exists():
        for pattern in ["FR-*.md", "NFR-*.md"]:
            add_parsed_documents(list(req_dir.glob(pattern)))

    adr_dir = docs_dir / "adr"
    if adr_dir.exists():
        add_parsed_documents(list(adr_dir.glob("ADR-*.md")))

    documents.extend(scan_tasks(docs_dir / "tasks"))
    return documents


def scan_tasks(tasks_dir: Path) -> list[Document]:
    """Scan task directories and synthesize task documents."""
    if not tasks_dir.exists():
        return []

    task_documents: list[Document] = []
    for task_dir in tasks_dir.iterdir():
        task_doc = build_task_document(task_dir)
        if task_doc:
            task_documents.append(task_doc)
    return task_documents


def merge_links(
    target: dict[str, list[str]], source: dict[str, list[str]]
) -> None:
    """Merge link lists without dropping existing entries."""
    for key, ids in source.items():
        bucket = target.setdefault(key, [])
        for link_id in ids:
            if link_id not in bucket:
                bucket.append(link_id)


def build_task_document(task_dir: Path) -> Document | None:
    """Build a synthetic task document from task directory contents."""
    if not (task_dir.is_dir() and task_dir.name.upper().startswith("T-")):
        return None

    task_id = extract_id(task_dir.name)
    if not task_id:
        return None

    design_doc = parse_document(task_dir / "design.md")
    plan_doc = parse_document(task_dir / "plan.md")

    links: dict[str, list[str]] = {}
    status = "Unknown"

    if design_doc:
        merge_links(links, design_doc.links)
        status = design_doc.status

    if plan_doc:
        merge_links(links, plan_doc.links)
        if plan_doc.status != "Unknown":
            status = plan_doc.status

    return Document(
        id=task_id,
        doc_type="Task",
        title=task_dir.name,
        path=task_dir,
        status=status,
        links=links,
    )


def analyze_traceability(documents: list[Document]) -> TraceabilityReport:
    """Analyze traceability across all documents."""
    report = TraceabilityReport()
    report.total_documents = len(documents)

    requirement_ids: set[str] = set()

    # Categorize documents
    for doc in documents:
        if doc.doc_type == "Analysis":
            report.analyses.append(doc)
        elif doc.doc_type in ["Functional Requirement", "Non-Functional Requirement"]:
            report.requirements.append(doc)
            requirement_ids.add(doc.id)
        elif doc.doc_type == "ADR":
            report.adrs.append(doc)
        elif doc.doc_type == "Task":
            report.tasks.append(doc)

    # Find requirements implemented by tasks
    implemented_requirements: set[str] = set()
    for task in report.tasks:
        req_links = task.links.get("Requirements", [])
        implemented_requirements.update(req_links)

    # Find orphan requirements (no implementing task)
    for req in report.requirements:
        if req.id not in implemented_requirements:
            # Check if any task links to this requirement
            is_linked = False
            for task in report.tasks:
                if req.id in task.links.get("Requirements", []):
                    is_linked = True
                    break
            if not is_linked:
                report.orphan_requirements.append(req)

    # Find orphan tasks (no linked requirements)
    for task in report.tasks:
        if not task.links.get("Requirements"):
            report.orphan_tasks.append(task)

    # Calculate coverage
    if report.requirements:
        implemented_count = len(implemented_requirements & requirement_ids)
        report.coverage_percent = (implemented_count / len(report.requirements)) * 100

    return report


def format_report_text(report: TraceabilityReport) -> str:
    """Format the report as plain text."""
    lines = []
    lines.append("=" * 60)
    lines.append("TDL Traceability Status Report")
    lines.append("=" * 60)
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append(f"  Total Documents: {report.total_documents}")
    lines.append(f"  Analyses: {len(report.analyses)}")
    lines.append(f"  Requirements: {len(report.requirements)}")
    lines.append(f"  ADRs: {len(report.adrs)}")
    lines.append(f"  Tasks: {len(report.tasks)}")
    lines.append(f"  Coverage: {report.coverage_percent:.1f}%")
    lines.append("")

    # Gaps
    if report.orphan_requirements or report.orphan_tasks:
        lines.append("## Gaps Detected")
        lines.append("")

        if report.orphan_requirements:
            lines.append("### Requirements without Tasks:")
            for req in report.orphan_requirements:
                lines.append(f"  - {req.id}: {req.title}")
            lines.append("")

        if report.orphan_tasks:
            lines.append("### Tasks without Requirements:")
            for task in report.orphan_tasks:
                lines.append(f"  - {task.id}: {task.title}")
            lines.append("")
    else:
        lines.append("## No gaps detected!")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_report_markdown(report: TraceabilityReport) -> str:
    """Format the report as markdown."""
    lines = []
    lines.append("# TDL Traceability Status Report")
    lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Documents | {report.total_documents} |")
    lines.append(f"| Analyses | {len(report.analyses)} |")
    lines.append(f"| Requirements | {len(report.requirements)} |")
    lines.append(f"| ADRs | {len(report.adrs)} |")
    lines.append(f"| Tasks | {len(report.tasks)} |")
    lines.append(f"| **Coverage** | **{report.coverage_percent:.1f}%** |")
    lines.append("")

    # Gaps
    if report.orphan_requirements or report.orphan_tasks:
        lines.append("## Gaps Detected")
        lines.append("")

        if report.orphan_requirements:
            lines.append("### Requirements without Tasks")
            lines.append("")
            for req in report.orphan_requirements:
                lines.append(f"- `{req.id}`: {req.title}")
            lines.append("")

        if report.orphan_tasks:
            lines.append("### Tasks without Requirements")
            lines.append("")
            for task in report.orphan_tasks:
                lines.append(f"- `{task.id}`: {task.title}")
            lines.append("")
    else:
        lines.append("## Status: All Clear")
        lines.append("")
        lines.append("No traceability gaps detected.")
        lines.append("")

    return "\n".join(lines)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Analyze TDL traceability status")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed document list"
    )
    parser.add_argument(
        "--check", action="store_true", help="CI mode - exit with error if gaps found"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "markdown"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--path",
        "-p",
        type=Path,
        help="Project root path (default: search from current directory)",
    )

    args = parser.parse_args()

    # Find docs directory
    if args.path:
        docs_dir = args.path / "docs"
    else:
        docs_dir = find_docs_directory()

    if docs_dir is None or not docs_dir.exists():
        print("Error: Could not find docs/ directory", file=sys.stderr)
        sys.exit(1)
    assert docs_dir is not None

    # Scan and analyze
    documents = scan_documents(docs_dir)

    if not documents:
        print("No TDL documents found.")
        sys.exit(0)

    report = analyze_traceability(documents)

    # Output report
    if args.format == "markdown":
        print(format_report_markdown(report))
    else:
        print(format_report_text(report))

    # Verbose output
    if args.verbose:
        print("\n## All Documents")
        for doc in sorted(documents, key=lambda d: d.id):
            print(f"  {doc.id} ({doc.doc_type}): {doc.status}")
            if doc.links:
                for link_type, link_ids in doc.links.items():
                    print(f"    -> {link_type}: {', '.join(link_ids)}")

    # CI mode exit code
    if args.check:
        if report.orphan_requirements or report.orphan_tasks:
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
