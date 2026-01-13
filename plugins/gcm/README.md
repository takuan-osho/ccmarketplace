# gcm

[Agent Skill](https://agentskills.io) for automated Git Commit Message generation.

## Overview

Analyzes staged changes and generates English commit messages in Conventional Commits format.

## Usage

```
/gcm
```

## Features

- Automatic analysis of staged changes (`git diff --cached`)
- Message generation in Conventional Commits format
  - `feat:` - New feature
  - `fix:` - Bug fix
  - `refactor:` - Refactoring
  - `test:` - Test additions/modifications
  - `docs:` - Documentation changes
  - `chore:` - Build/configuration changes
  - `style:` - Code style changes
  - `perf:` - Performance improvements
  - `ci:` - CI configuration changes
- References recent commit history for style consistency

## Output Format

```
<type>: <summary of changes>

<detailed description>

<impact scope or additional context>
```

## Details

See [SKILL.md](SKILL.md) for detailed guidelines.
