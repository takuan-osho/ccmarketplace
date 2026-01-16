# Interview Skill

A skill for conducting structured interviews to gather requirements, clarify specifications, and understand context.

## Overview

This skill provides a structured interview framework to systematically gather information before starting work. It helps reduce ambiguity, ensure comprehensive understanding, and produce actionable outputs.

## Supported Interview Types

| Type | Use Case |
|------|----------|
| Requirements | New feature, specification, API design |
| Investigation | Bug analysis, performance issue, incident |
| Architecture | Design review, technology selection, refactoring |
| Security | Security audit, vulnerability assessment |
| Documentation | Report creation, knowledge transfer |
| General | Open-ended exploration, brainstorming |

## Usage

```
/interview [topic]
```

Examples:
```
/interview Add user authentication feature
/interview Investigate 504 errors in production
/interview Review database schema for scalability
```

## Workflow

1. **Phase 1: Preparation** - Codebase exploration, relevant documentation review (silent execution)
2. **Phase 2: Interview** - Goal confirmation, deep dive questions, priority setting
3. **Phase 3: Output** - Generate structured summary document

## Features

- **Environment-Aware Input** - AskUserQuestion tool in Claude Code, numbered options in other environments
- **Multiple Interview Types** - Question frameworks tailored to the task
- **Priority Classification** - Must/Should/Could requirement categorization
- **Output Templates** - Consistent structured documentation

## References

- `references/interview-types.md` - Detailed question frameworks per interview type
- `references/exploration-patterns.md` - Environment-specific codebase exploration commands
- `references/usage-examples.md` - Detailed usage examples with sample outputs

## Inspiration

This skill is based on [taichi/interview custom command](https://gist.github.com/taichi/8419da7e2b20685db8d5f91f73fc3b1d), extended as a more versatile interview framework.
