# gemini-search

[Agent Skill](https://agentskills.io) for web search using Google Gemini CLI.

## Overview

Performs web searches using the Gemini CLI tool instead of the built-in WebSearch tool.

## Prerequisites

The `gemini` CLI tool must be installed and configured.

## Usage

```bash
gemini --prompt "WebSearch: <query>"
```

## Examples

```bash
# Basic search
gemini --prompt "WebSearch: latest Python 3.12 features"

# Technical documentation search
gemini --prompt "WebSearch: Kubernetes pod networking best practices 2025"

# API documentation search
gemini --prompt "WebSearch: OpenAI API rate limits documentation"
```

## When to Use

- User explicitly requests search using Gemini
- More comprehensive search results are needed
- Google's search capabilities are preferred

## Details

See [SKILL.md](SKILL.md) for more information.
