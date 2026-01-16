# Codebase Exploration Patterns

This document provides environment-specific patterns for exploring codebases during the preparation phase.

## Claude Code

Use built-in tools for efficient exploration:

### Project Structure
```
# Find key files by pattern
Glob: **/*.md
Glob: **/config.*
Glob: **/package.json, **/pyproject.toml, **/go.mod

# Read important files
Read: README.md, CONTRIBUTING.md, ARCHITECTURE.md
```

### Code Search
```
# Search for patterns
Grep: "class.*Controller" --type=py
Grep: "func.*Handler" --type=go
Grep: "TODO|FIXME"

# Find definitions
Grep: "def function_name"
Grep: "interface.*Name"
```

### Git History
```bash
git log --oneline -10
git diff main...HEAD --stat
git blame <file>
```

## Codex / OpenAI

Use shell commands and MCP tools:

### Project Structure
```bash
# Directory overview
ls -la
tree -L 2 -d

# Find config files
find . -name "*.json" -o -name "*.yaml" -o -name "*.toml" | head -20

# List recent files
find . -type f -mtime -7 | head -20
```

### Code Search
```bash
# Search patterns
grep -r "pattern" --include="*.py"
rg "pattern" -t py

# Find definitions
grep -rn "def function_name" .
grep -rn "class ClassName" .
```

### With Serena MCP
```
# Activate project
serena_activate_project

# Get symbols
serena_get_symbols <file>

# Find references
serena_find_references <symbol>
```

## API / Generic Environment

Use standard shell commands:

### Quick Overview
```bash
# Project structure
find . -type f -name "*.md" | head -10
ls -la src/ lib/ app/ 2>/dev/null

# Package info
cat package.json 2>/dev/null | head -20
cat pyproject.toml 2>/dev/null | head -20
cat go.mod 2>/dev/null
```

### Search Patterns
```bash
# Basic search
grep -r "keyword" --include="*.js" .
grep -rn "function_name" .

# With context
grep -B 2 -A 2 "pattern" <file>
```

## What to Look For

### Project Understanding
- Entry points (main.*, index.*, app.*)
- Configuration files
- Test structure
- Build/deployment scripts

### Architecture Clues
- Directory naming conventions
- Module/package organization
- Dependency injection patterns
- API route definitions

### Recent Activity
- Last modified files
- Recent commits
- Open branches
- Pending changes

### Documentation
- README files
- ADR (Architecture Decision Records)
- API documentation
- Inline comments in complex areas

## Common Patterns by Project Type

### Web Application
```
src/
├── components/    # UI components
├── pages/         # Route pages
├── api/           # API routes
├── hooks/         # Custom hooks
└── utils/         # Utilities
```

### Backend Service
```
.
├── cmd/           # Entry points
├── internal/      # Private packages
├── pkg/           # Public packages
├── api/           # API definitions
└── config/        # Configuration
```

### Python Package
```
.
├── src/<package>/ # Source code
├── tests/         # Tests
├── docs/          # Documentation
└── pyproject.toml # Project config
```

## Tips

1. **Start broad, then narrow** - Get overview first, then dive into specifics
2. **Follow imports** - Trace dependencies to understand relationships
3. **Check tests** - Tests often reveal expected behavior and edge cases
4. **Read error handling** - Error paths reveal assumptions and constraints
5. **Look for patterns** - Identify conventions used in the codebase
