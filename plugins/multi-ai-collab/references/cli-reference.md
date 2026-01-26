# CLI Reference

This document provides the exact CLI commands for invoking each supported AI agent.

## Codex CLI

### Installation

```bash
# Check OpenAI documentation for latest installation method
# https://developers.openai.com/codex/cli/
```

### Configuration

Configuration file: `~/.codex/config.toml`

```toml
# Set default model
model = "gpt-5.2-codex"

# Approval settings
approval_mode = "suggest"

# Provider settings
provider = "openai"
```

### Commands

```bash
# Basic usage with model override
codex --model gpt-5.2-codex "Your prompt here"

# Using config override
codex --config model='"gpt-5.2-codex"' "Your prompt here"

# Multi-line prompt using heredoc
codex --model gpt-5.2-codex "$(cat <<'EOF'
You are a Senior Software Architect.

Analyze the following code:
$(cat src/file.ts)

Provide findings with severity levels.
EOF
)"

# With specific working directory
cd /path/to/project && codex --model gpt-5.2-codex "Analyze this project"

# Reading file content into prompt
codex --model gpt-5.2-codex "Review this code: $(cat src/auth.ts)"
```

### Model Options

| Model | Description | Use Case |
|-------|-------------|----------|
| `gpt-5.2-codex` | Latest Codex model | Complex reasoning, architecture |
| `gpt-5-codex` | Previous generation | General coding tasks |

### Tips

- Codex CLI runs in agentic mode by default
- Results are returned after completion
- For long-running tasks, monitor progress in terminal

---

## Gemini CLI

### Installation

```bash
# npm (global install)
npm install -g @google/gemini-cli

# npx (no install)
npx @google/gemini-cli

# Homebrew (macOS/Linux)
brew install gemini-cli
```

### Authentication

Three options:

1. **Google Login (OAuth)**: Personal use, 60 req/min free tier
2. **Gemini API Key**: Set `GEMINI_API_KEY` environment variable
3. **Vertex AI**: Enterprise setup

```bash
# Set API key
export GEMINI_API_KEY="your-api-key"
```

### Commands

```bash
# Basic non-interactive mode (REQUIRED for scripting)
gemini -p "Your prompt here"

# With model specification
gemini -p "Your prompt here" -m gemini-2.5-pro

# JSON output format
gemini -p "Your prompt here" -m gemini-2.5-pro --output-format json

# Including multiple directories
gemini --include-directories ../lib,../docs -p "Analyze these directories"

# Multi-line prompt
gemini -p "$(cat <<'EOF'
You are a Security Researcher.

Analyze this code for vulnerabilities:
$(cat src/auth.ts)

Check for OWASP Top 10 issues.
EOF
)" -m gemini-2.5-pro
```

### Model Options

| Model | Description | Use Case |
|-------|-------------|----------|
| `gemini-2.5-pro` | Latest Pro model | Complex analysis |
| `gemini-2.5-flash` | Fast model | Quick tasks |
| `gemini-2.0-flash` | Previous generation | Fallback |

### Tips

- Always use `-p` flag for non-interactive/scripting use
- Use `-m` to specify model explicitly
- Gemini has web search capabilities built-in
- 1M token context window available

---

## Claude Code CLI

### Installation

```bash
# Download from Anthropic
# https://code.claude.com/docs
```

### Commands

```bash
# Non-interactive mode (print and exit)
claude -p "Your prompt here"

# With JSON output
claude -p "Your prompt here" --output-format json

# With tool restrictions
claude -p "Your prompt here" --allowedTools Read,Grep,Glob

# With turn limit
claude -p "Your prompt here" --max-turns 5

# Resume a session
claude --resume session-id

# Combined options
claude -p "Analyze src/auth.ts for security issues" \
  --allowedTools Read,Grep,Glob \
  --max-turns 10 \
  --output-format json
```

### Claude Code Sub-agents (Task Tool)

When running inside Claude Code, use the Task tool for sub-agents:

```
Task tool parameters:
  subagent_type: general-purpose
  prompt: "Your detailed prompt"
  model: sonnet | opus | haiku
```

Example usage in SKILL.md context:

```markdown
For QA analysis, use the Task tool:
- subagent_type: general-purpose
- model: sonnet (fast) or opus (thorough)
- prompt: [QA PERSONA PROMPT]
```

### Model Options (for sub-agents)

| Model | Description | Use Case |
|-------|-------------|----------|
| `opus` | Most capable | Complex analysis, architecture |
| `sonnet` | Balanced | General tasks, fast iteration |
| `haiku` | Fastest | Simple tasks, high volume |

### Tips

- `-p` flag is essential for non-interactive use
- `--allowedTools` restricts what tools the agent can use
- `--max-turns` prevents runaway execution
- Use Task tool for Claude-to-Claude sub-agent calls

---

## Cross-Platform Command Patterns

### Capturing Output

```bash
# Capture Codex output
CODEX_RESULT=$(codex --model gpt-5.2-codex "prompt")

# Capture Gemini output
GEMINI_RESULT=$(gemini -p "prompt" -m gemini-2.5-pro)

# Capture Claude output
CLAUDE_RESULT=$(claude -p "prompt")
```

### Passing File Content

```bash
# Read file into variable
FILE_CONTENT=$(cat src/file.ts)

# Pass to agent
codex --model gpt-5.2-codex "Review this: $FILE_CONTENT"
```

### Chaining Agents

```bash
# Sequential execution
STEP1=$(codex --model gpt-5.2-codex "First analysis")
STEP2=$(gemini -p "Build on this: $STEP1" -m gemini-2.5-pro)
FINAL=$(claude -p "Synthesize: $STEP1 and $STEP2")
```

### Parallel Execution

```bash
# Background execution
codex --model gpt-5.2-codex "Analysis A" > /tmp/result_a.txt &
gemini -p "Analysis B" -m gemini-2.5-pro > /tmp/result_b.txt &
claude -p "Analysis C" > /tmp/result_c.txt &

# Wait for all
wait

# Collect results
RESULT_A=$(cat /tmp/result_a.txt)
RESULT_B=$(cat /tmp/result_b.txt)
RESULT_C=$(cat /tmp/result_c.txt)
```

---

## Error Handling

### Check CLI Availability

```bash
# Check if CLI exists
command -v codex >/dev/null 2>&1 || echo "Codex not installed"
command -v gemini >/dev/null 2>&1 || echo "Gemini not installed"
command -v claude >/dev/null 2>&1 || echo "Claude not installed"
```

### Handle Timeouts

```bash
# Timeout after 5 minutes
timeout 300 codex --model gpt-5.2-codex "Long running analysis"
```

### Retry Logic

```bash
# Simple retry
for i in 1 2 3; do
  result=$(codex --model gpt-5.2-codex "prompt") && break
  sleep $((i * 2))
done
```

---

## Environment Variables

| Variable | CLI | Description |
|----------|-----|-------------|
| `OPENAI_API_KEY` | Codex | OpenAI API key |
| `GEMINI_API_KEY` | Gemini | Google Gemini API key |
| `ANTHROPIC_API_KEY` | Claude | Anthropic API key |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────┐
│                      CLI QUICK REFERENCE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  CODEX CLI                                                          │
│  codex --model gpt-5.2-codex "prompt"                              │
│                                                                     │
│  GEMINI CLI                                                         │
│  gemini -p "prompt" -m gemini-2.5-pro                              │
│                                                                     │
│  CLAUDE CLI                                                         │
│  claude -p "prompt"                                                 │
│                                                                     │
│  CLAUDE SUB-AGENT (Task tool)                                       │
│  subagent_type: general-purpose                                     │
│  model: sonnet                                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```
