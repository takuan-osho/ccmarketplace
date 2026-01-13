#!/usr/bin/env python3
"""
Trace a requirement or TDL document through the codebase.

Finds all code, tests, commits, and documentation related to a specific
requirement, ADR, analysis, or task.

Supports TDL ID formats:
- FR-xxxxx  (Functional Requirements)
- NFR-xxxxx (Non-Functional Requirements)
- ADR-xxxxx (Architecture Decision Records)
- AN-xxxxx  (Analysis documents)
- T-xxxxx   (Tasks)

Usage:
    python trace_requirement.py FR-a3bf2
    python trace_requirement.py ADR-b4cd8 --verbose
    python trace_requirement.py "user authentication" --search-term
"""

import argparse
import re
import shutil
import subprocess
from pathlib import Path


def compile_pattern(pattern: str, search_term: bool) -> re.Pattern[str]:
    """Compile a case-insensitive regex pattern, optionally escaping literals."""
    if search_term:
        pattern = re.escape(pattern)

    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error:
        return re.compile(re.escape(pattern), re.IGNORECASE)


def expand_file_pattern(base_path: Path, file_pattern: str) -> list[Path]:
    """Expand a file pattern relative to the base path."""
    if "/" in file_pattern or file_pattern.startswith("**"):
        return list(base_path.glob(file_pattern))
    return list(base_path.rglob(file_pattern))


def collect_matches(path: Path, pattern: re.Pattern[str], base_path: Path) -> list[str]:
    """Collect matching lines from a single file."""
    try:
        rel_path = path.relative_to(base_path)
    except ValueError:
        rel_path = path

    matches: list[str] = []
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for line_number, line in enumerate(handle, start=1):
                if pattern.search(line):
                    matches.append(f"{rel_path}:{line_number}:{line.rstrip()}")
    except OSError:
        return []

    return matches


def search_in_files(
    pattern: re.Pattern[str], file_patterns: list[str], base_path: Path
) -> dict[str, list[str]]:
    """Search for pattern in files matching the given patterns."""
    results: dict[str, list[str]] = {}

    for file_pattern in file_patterns:
        matches: list[str] = []
        for path in expand_file_pattern(base_path, file_pattern):
            if not path.is_file():
                continue

            matches.extend(collect_matches(path, pattern, base_path))

        if matches:
            results[file_pattern] = matches

    return results


def search_git_history(pattern: str) -> list[str]:
    """Search git commit history for pattern."""
    if shutil.which("git") is None:
        return []

    try:
        cmd = [
            "git",
            "log",
            "--all",
            "--grep",
            pattern,
            "--oneline",
            "--regexp-ignore-case",
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, cwd=Path.cwd()
        )

        if result.returncode == 0 and result.stdout:
            return result.stdout.strip().split("\n")
    except subprocess.SubprocessError:
        pass

    return []


def search_documentation(
    pattern: re.Pattern[str], base_path: Path
) -> dict[str, list[str]]:
    """Search documentation files for pattern."""
    doc_patterns = [
        "docs/requirements/*.md",
        "docs/adr/*.md",
        "docs/adr/archive/*.md",
        "docs/analysis/*.md",
        "docs/analysis/archive/*.md",
        "docs/tasks/*/*.md",
        "README.md",
        "*.md",
    ]

    return search_in_files(pattern, doc_patterns, base_path)


def print_search_results(
    title: str,
    results: dict[str, list[str]],
    verbose: bool,
    empty_message: str,
    limit: int | None = None,
) -> None:
    """Print search results with optional match limiting."""
    print(title)
    if not results:
        print(empty_message)
        return

    for file_pattern, matches in results.items():
        if verbose:
            print(f"\n  {file_pattern}:")
            for match in matches[:limit] if limit is not None else matches:
                print(f"    {match}")
            if limit is not None and len(matches) > limit:
                print(f"    ... and {len(matches) - limit} more")
        else:
            print(f"  {file_pattern}: {len(matches)} matches")


def count_matches(results: dict[str, list[str]]) -> int:
    """Count total matches in a result set."""
    return sum(len(matches) for matches in results.values())


def trace_requirement(
    requirement_id: str, search_term: bool = False, verbose: bool = False
) -> None:
    """Trace a TDL document through the codebase."""
    base_path = Path.cwd()
    pattern = compile_pattern(requirement_id, search_term)

    print(f"🔍 Tracing: {requirement_id}\n")
    print("Supported ID formats: FR-xxxxx, NFR-xxxxx, ADR-xxxxx, AN-xxxxx, T-xxxxx\n")

    # Search in documentation
    doc_results = search_documentation(pattern, base_path)
    print_search_results(
        "📚 Documentation References:",
        doc_results,
        verbose,
        "  No documentation references found",
    )

    # Search in source code
    code_patterns = ["*.py", "*.js", "*.ts", "*.java", "*.go", "*.rs"]
    code_results = search_in_files(pattern, code_patterns, base_path)
    print_search_results(
        "\n💻 Source Code References:",
        code_results,
        verbose,
        "  No source code references found",
        limit=10,
    )

    # Search in tests
    test_patterns = ["*test*.py", "*test*.js", "*test*.ts", "*_test.go", "*_test.rs"]
    test_results = search_in_files(pattern, test_patterns, base_path)
    print_search_results(
        "\n🧪 Test References:",
        test_results,
        verbose,
        "  No test references found",
        limit=10,
    )

    # Search git history
    print("\n📝 Git Commit History:")
    git_pattern = re.escape(requirement_id) if search_term else requirement_id
    commits = search_git_history(git_pattern)
    if commits:
        for commit in commits[:10]:  # Show first 10 commits
            print(f"  {commit}")
        if len(commits) > 10:
            print(f"  ... and {len(commits) - 10} more commits")
    else:
        print("  No commits found")

    # Summary
    print("\n" + "=" * 60)
    doc_count = count_matches(doc_results)
    code_count = count_matches(code_results)
    test_count = count_matches(test_results)
    total_matches = doc_count + code_count + test_count + len(commits)

    print(f"📊 Total References Found: {total_matches}")
    print(f"   Documentation: {doc_count}")
    print(f"   Source Code: {code_count}")
    print(f"   Tests: {test_count}")
    print(f"   Git Commits: {len(commits)}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Trace a TDL document through the codebase"
    )
    parser.add_argument(
        "requirement",
        help="TDL ID (e.g., FR-a3bf2, ADR-b4cd8) or search term with --search-term flag",
    )
    parser.add_argument(
        "--search-term",
        "-s",
        action="store_true",
        help="Treat argument as search term instead of TDL ID",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed results"
    )

    args = parser.parse_args()

    trace_requirement(args.requirement, args.search_term, args.verbose)


if __name__ == "__main__":
    main()
