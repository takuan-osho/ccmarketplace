# create-pr

[Agent Skill](https://agentskills.io) for automated Pull Request creation.

## Overview

Analyzes differences between the current branch and main branch, generating appropriate PR titles and descriptions.

## Usage

```
/create-pr
```

## Features

- Automatic analysis of changed files
- Title generation in Conventional Commits format
  - `feat:` - New feature
  - `fix:` - Bug fix
  - `refactor:` - Refactoring
  - `docs:` - Documentation update
- Auto-generated description for reviewers
- PR creation using GitHub CLI

## Generated Description Structure

- **Overview**: Background and purpose of changes
- **Related Issue**: Related issues
- **Changes**: Main changes
- **Impact Scope**: Affected areas
- **Checklist**: Pre-review checklist
- **How to Test**: Testing instructions

## Details

See [SKILL.md](SKILL.md) for detailed workflow.
