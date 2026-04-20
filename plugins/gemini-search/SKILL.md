---
name: gemini-search
description: Web search using Google Gemini CLI. This skill should be used when performing web searches through the Gemini CLI tool instead of the built-in WebSearch tool. Requires the Gemini CLI to be installed and configured.
---

# Gemini Search

## Overview

This skill enables web search functionality using the Google Gemini CLI tool. When this skill is triggered, use the Gemini CLI for web searches instead of the built-in WebSearch tool.

## Prerequisites

The `gemini` CLI tool must be installed and configured on the system. The Gemini CLI provides access to Google's Gemini AI model with web search capabilities.

## Usage

When web search is needed, execute the Gemini CLI via the Bash tool:

```bash
gemini --prompt "WebSearch: <query>"
```

### About the `WebSearch:` prefix

The `WebSearch:` prefix inside the prompt is a convention that signals to Gemini that this request requires web grounding rather than answering from training data. Keep it for any search-style query. Without the prefix, Gemini may respond from its training corpus and miss recent information.

## Fallback

If the `gemini` CLI is unavailable (not installed, unauthenticated, or returns a non-zero exit code), fall back to the built-in `WebSearch` tool and report the fallback to the user in one line (e.g., "gemini CLI unavailable, falling back to built-in WebSearch"). Do not silently swallow the failure.

## Examples

### Basic Search

```bash
gemini --prompt "WebSearch: latest Python 3.12 features"
```

### Technical Documentation Search

```bash
gemini --prompt "WebSearch: Kubernetes pod networking best practices 2025"
```

### API Documentation Search

```bash
gemini --prompt "WebSearch: OpenAI API rate limits documentation"
```

## When to Use

This skill is appropriate when:
- The user explicitly requests using Gemini for search
- More comprehensive web search results are needed
- The built-in WebSearch tool has limitations for specific queries
- Access to Google's search capabilities is preferred

## Notes

- The Gemini CLI must be properly authenticated and configured
- Search queries should be clear and specific for best results
- Results are returned through the Gemini model's response
