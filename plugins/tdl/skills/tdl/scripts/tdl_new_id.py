#!/usr/bin/env python3
"""
Generate unique random IDs for TDL documents.

Uses cryptographically secure random generation with collision checking
to ensure IDs are unique across the project.

Usage:
    python tdl_new_id.py              # Generate a random ID
    python tdl_new_id.py --prefix FR  # Generate with prefix (FR-xxxxx)
    python tdl_new_id.py --check      # Check if ID already exists
"""

import secrets
import string
import sys
from pathlib import Path

# Base36 character set: 0-9 and a-z
BASE36_CHARS = string.digits + string.ascii_lowercase

# Default ID length (5 characters = ~60 million combinations)
DEFAULT_ID_LENGTH = 5

# Maximum retry attempts for collision resolution
MAX_RETRIES = 10


def generate_base36_id(length: int = DEFAULT_ID_LENGTH) -> str:
    """Generate a cryptographically secure random Base36 ID.

    Args:
        length: Number of characters in the ID (default: 5)

    Returns:
        A random Base36 string of the specified length
    """
    return "".join(secrets.choice(BASE36_CHARS) for _ in range(length))


def find_docs_directory(start_path: Path | None = None) -> Path | None:
    """Find the docs/ directory by searching up from the start path.

    Args:
        start_path: Starting directory for search (default: current directory)

    Returns:
        Path to docs/ directory if found, None otherwise
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # Search up the directory tree
    while current != current.parent:
        docs_path = current / "docs"
        if docs_path.is_dir():
            return docs_path
        current = current.parent

    # Check root level
    docs_path = current / "docs"
    if docs_path.is_dir():
        return docs_path

    return None


def id_exists(id_str: str, docs_dir: Path) -> bool:
    """Check if an ID already exists in the docs/ directory.

    Searches for the ID pattern in file names and directory names.

    Args:
        id_str: The ID to check (without prefix)
        docs_dir: Path to the docs/ directory

    Returns:
        True if the ID exists, False otherwise
    """
    if not docs_dir.exists():
        return False

    # Patterns to search for (e.g., AN-a3bf2, FR-a3bf2, T-a3bf2)
    patterns = [
        f"*-{id_str}-*",
        f"*-{id_str}.*",
        f"*-{id_str}",
    ]

    for pattern in patterns:
        # Check files
        if list(docs_dir.rglob(pattern)):
            return True

    return False


def generate_unique_id(
    docs_dir: Path | None = None, length: int = DEFAULT_ID_LENGTH
) -> str:
    """Generate a unique ID that doesn't exist in the docs/ directory.

    Args:
        docs_dir: Path to docs/ directory for collision checking
        length: Number of characters in the ID

    Returns:
        A unique random Base36 ID

    Raises:
        RuntimeError: If unable to generate unique ID after MAX_RETRIES attempts
    """
    for attempt in range(MAX_RETRIES):
        new_id = generate_base36_id(length)

        # If no docs directory or ID doesn't exist, we're done
        if docs_dir is None or not id_exists(new_id, docs_dir):
            return new_id

        # Collision detected, retry
        print(
            f"Collision detected for {new_id}, retrying... ({attempt + 1}/{MAX_RETRIES})",
            file=sys.stderr,
        )

    raise RuntimeError(
        f"Failed to generate unique ID after {MAX_RETRIES} attempts. "
        "This is extremely unlikely - please check your docs/ directory."
    )


def format_id_with_prefix(id_str: str, prefix: str) -> str:
    """Format an ID with its document type prefix.

    Args:
        id_str: The base ID
        prefix: Document type prefix (e.g., FR, NFR, ADR, AN, T)

    Returns:
        Formatted ID (e.g., FR-a3bf2)
    """
    return f"{prefix}-{id_str}"


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate unique random IDs for TDL documents"
    )
    parser.add_argument(
        "--prefix",
        "-p",
        type=str,
        help="Document type prefix (e.g., FR, NFR, ADR, AN, T)",
    )
    parser.add_argument(
        "--length",
        "-l",
        type=int,
        default=DEFAULT_ID_LENGTH,
        help=f"ID length (default: {DEFAULT_ID_LENGTH})",
    )
    parser.add_argument(
        "--no-check",
        action="store_true",
        help="Skip collision checking against docs/ directory",
    )
    parser.add_argument(
        "--path",
        type=Path,
        help="Project root path (default: search from current directory)",
    )

    args = parser.parse_args()

    # Find docs directory for collision checking
    docs_dir = None
    if not args.no_check:
        if args.path:
            docs_dir = args.path / "docs"
            if not docs_dir.exists():
                docs_dir = None
        else:
            docs_dir = find_docs_directory()

    # Generate unique ID
    try:
        new_id = generate_unique_id(docs_dir, args.length)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Output with or without prefix
    if args.prefix:
        print(format_id_with_prefix(new_id, args.prefix.upper()))
    else:
        print(new_id)


if __name__ == "__main__":
    main()
