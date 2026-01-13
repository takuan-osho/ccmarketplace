# tdl

[Agent Skill](https://agentskills.io) for implementing Traceable Development Lifecycle (TDL).

## Overview

Provides a template-based development process ensuring complete traceability from requirements to implementation.

## Features

- **Random Base36 IDs**: Prevents conflicts in parallel development
- **Distributed Traceability**: Each document manages relationships via Links section
- **5-Phase Workflow**: Analysis → Requirements → ADR → Design → Plan

## Document Types

| Type | Format | Purpose |
|------|--------|---------|
| Analysis | AN-xxxxx | Problem exploration & requirements discovery |
| Functional Requirement | FR-xxxxx | Functional requirements |
| Non-Functional Requirement | NFR-xxxxx | Non-functional requirements |
| ADR | ADR-xxxxx | Architecture Decision Records |
| Task | T-xxxxx | Design & implementation plans |

## Usage

### Initialize Structure

```bash
python scripts/init_tdl_docs.py
```

### Create Documents

```bash
# Analysis
python scripts/create_analysis.py "Topic Name"

# Requirements
python scripts/create_requirement.py "Title" --type FR

# ADR
python scripts/create_adr.py "Decision Title"

# Task
python scripts/create_task.py "task-name"
```

### Traceability Analysis

```bash
python scripts/trace_status.py
python scripts/trace_status.py --check  # For CI
```

## Details

See [SKILL.md](SKILL.md) for detailed workflows and templates.
