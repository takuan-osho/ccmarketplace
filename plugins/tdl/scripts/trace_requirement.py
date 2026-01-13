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
import subprocess
import sys
from pathlib import Path


def search_in_files(pattern: str, file_patterns: list[str]) -> dict[str, list[str]]:
    """Search for pattern in files matching the given patterns."""
    results = {}

    for file_pattern in file_patterns:
        try:
            # Use git grep for faster searching in git repositories
            cmd = ["git", "grep", "-n", "-i", pattern, "--", file_pattern]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False, cwd=Path.cwd()
            )

            if result.returncode == 0 and result.stdout:
                matches = result.stdout.strip().split("\n")
                if matches:
                    results[file_pattern] = matches

        except subprocess.SubprocessError:
            # Fallback to regular grep if git grep fails
            try:
                cmd = ["grep", "-r", "-n", "-i", pattern, file_pattern]
                result = subprocess.run(
                    cmd, capture_output=True, text=True, check=False, cwd=Path.cwd()
                )

                if result.returncode == 0 and result.stdout:
                    matches = result.stdout.strip().split("\n")
                    if matches:
                        results[file_pattern] = matches
            except subprocess.SubprocessError:
                continue

    return results


def search_git_history(pattern: str) -> list[str]:
    """Search git commit history for pattern."""
    try:
        cmd = ["git", "log", "--all", "--grep", pattern, "--oneline"]
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, cwd=Path.cwd()
        )

        if result.returncode == 0 and result.stdout:
            return result.stdout.strip().split("\n")
    except subprocess.SubprocessError:
        pass

    return []


def search_documentation(pattern: str) -> dict[str, list[str]]:
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

    return search_in_files(pattern, doc_patterns)


def trace_requirement(
    requirement_id: str, search_term: bool = False, verbose: bool = False
) -> None:
    """Trace a TDL document through the codebase."""
    pattern = requirement_id

    print(f"🔍 Tracing: {pattern}\n")
    print("Supported ID formats: FR-xxxxx, NFR-xxxxx, ADR-xxxxx, AN-xxxxx, T-xxxxx\n")

    # Search in documentation
    print("📚 Documentation References:")
    doc_results = search_documentation(pattern)
    if doc_results:
        for file_pattern, matches in doc_results.items():
            if verbose:
                print(f"\n  {file_pattern}:")
                for match in matches:
                    print(f"    {match}")
            else:
                print(f"  {file_pattern}: {len(matches)} matches")
    else:
        print("  No documentation references found")

    # Search in source code
    print("\n💻 Source Code References:")
    code_patterns = ["*.py", "*.js", "*.ts", "*.java", "*.go", "*.rs"]
    code_results = search_in_files(pattern, code_patterns)
    if code_results:
        for file_pattern, matches in code_results.items():
            if verbose:
                print(f"\n  {file_pattern}:")
                for match in matches[:10]:  # Limit to first 10 matches
                    print(f"    {match}")
                if len(matches) > 10:
                    print(f"    ... and {len(matches) - 10} more")
            else:
                print(f"  {file_pattern}: {len(matches)} matches")
    else:
        print("  No source code references found")

    # Search in tests
    print("\n🧪 Test References:")
    test_patterns = ["*test*.py", "*test*.js", "*test*.ts", "*_test.go", "*_test.rs"]
    test_results = search_in_files(pattern, test_patterns)
    if test_results:
        for file_pattern, matches in test_results.items():
            if verbose:
                print(f"\n  {file_pattern}:")
                for match in matches[:10]:
                    print(f"    {match}")
                if len(matches) > 10:
                    print(f"    ... and {len(matches) - 10} more")
            else:
                print(f"  {file_pattern}: {len(matches)} matches")
    else:
        print("  No test references found")

    # Search git history
    print("\n📝 Git Commit History:")
    commits = search_git_history(pattern)
    if commits:
        for commit in commits[:10]:  # Show first 10 commits
            print(f"  {commit}")
        if len(commits) > 10:
            print(f"  ... and {len(commits) - 10} more commits")
    else:
        print("  No commits found")

    # Summary
    print("\n" + "=" * 60)
    total_matches = (
        sum(len(matches) for matches in doc_results.values())
        + sum(len(matches) for matches in code_results.values())
        + sum(len(matches) for matches in test_results.values())
        + len(commits)
    )

    print(f"📊 Total References Found: {total_matches}")
    print(f"   Documentation: {sum(len(matches) for matches in doc_results.values())}")
    print(f"   Source Code: {sum(len(matches) for matches in code_results.values())}")
    print(f"   Tests: {sum(len(matches) for matches in test_results.values())}")
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
