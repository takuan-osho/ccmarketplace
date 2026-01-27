# Multi-AI Collaboration Skill

Orchestrate multiple AI agents (Codex CLI, Gemini CLI, Claude) with specialized personas for cross-review and collaborative software development tasks.

## Features

- **Cross-Review**: Multiple AI agents independently review code, then synthesize findings
- **Persona-Based Roles**: Assign specialized roles (Architect, Security, QA, etc.) to each agent
- **Flexible Workflows**: Sequential, Parallel, Pipeline, or Adversarial execution modes
- **Conflict Resolution**: AskUserTool integration for handling divergent opinions

## Supported AI Agents

| Agent | CLI Command | Model | Best For |
|-------|-------------|-------|----------|
| Codex CLI | `codex` | latest default | Deep reasoning, architecture |
| Gemini CLI | `gemini` | latest default | Web search, latest info |
| Claude | Task subagent | latest default | Fast implementation, orchestration |

## Available Personas

- 🏗️ **Architect** - System design and structure evaluation
- 🔒 **Security Researcher** - Vulnerability analysis
- 🧪 **QA Engineer** - Test design and quality assurance
- 👁️ **Code Reviewer** - Code quality review
- ⚡ **Performance Engineer** - Performance analysis
- 🔍 **Analyzer** - Static analysis and bug detection
- 📝 **Documentarian** - Documentation quality
- 🧠 **Domain Expert** - Business logic verification

## Quick Start

1. Invoke the skill from any AI agent CLI
2. Select personas for your team
3. Assign AI agents to each persona
4. Choose workflow mode
5. Review synthesized results

## Usage

```
/multi-ai-collab [task description]
```

See [SKILL.md](./SKILL.md) for detailed usage instructions.
