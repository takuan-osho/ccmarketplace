#!/bin/bash

# detect-agents.sh
# Detects which AI agent CLIs are available on the system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Multi-AI Collaboration Agent Detector"
echo "=========================================="
echo ""

# Track available agents
AVAILABLE_AGENTS=()

# Check Codex CLI
echo -n "Checking Codex CLI... "
if command -v codex &> /dev/null; then
    CODEX_VERSION=$(codex --version 2>/dev/null || echo "version unknown")
    echo -e "${GREEN}✓ Found${NC} ($CODEX_VERSION)"
    AVAILABLE_AGENTS+=("codex")
else
    echo -e "${RED}✗ Not found${NC}"
    echo "  Install: See https://developers.openai.com/codex/cli/"
fi

# Check Gemini CLI
echo -n "Checking Gemini CLI... "
if command -v gemini &> /dev/null; then
    GEMINI_VERSION=$(gemini --version 2>/dev/null || echo "version unknown")
    echo -e "${GREEN}✓ Found${NC} ($GEMINI_VERSION)"
    AVAILABLE_AGENTS+=("gemini")
else
    echo -e "${RED}✗ Not found${NC}"
    echo "  Install: npm install -g @google/gemini-cli"
    echo "       or: brew install gemini-cli"
fi

# Check Claude CLI
echo -n "Checking Claude CLI... "
if command -v claude &> /dev/null; then
    CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "version unknown")
    echo -e "${GREEN}✓ Found${NC} ($CLAUDE_VERSION)"
    AVAILABLE_AGENTS+=("claude")
else
    echo -e "${RED}✗ Not found${NC}"
    echo "  Install: See https://code.claude.com/docs"
fi

echo ""
echo "=========================================="
echo "  Environment Variables"
echo "=========================================="
echo ""

# Check API keys (existence only, not values)
echo -n "OPENAI_API_KEY... "
if [ -n "$OPENAI_API_KEY" ]; then
    echo -e "${GREEN}✓ Set${NC}"
else
    echo -e "${YELLOW}○ Not set${NC} (required for Codex)"
fi

echo -n "GEMINI_API_KEY... "
if [ -n "$GEMINI_API_KEY" ]; then
    echo -e "${GREEN}✓ Set${NC}"
else
    echo -e "${YELLOW}○ Not set${NC} (optional, can use Google login)"
fi

echo -n "ANTHROPIC_API_KEY... "
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo -e "${GREEN}✓ Set${NC}"
else
    echo -e "${YELLOW}○ Not set${NC} (required for Claude CLI)"
fi

echo ""
echo "=========================================="
echo "  Summary"
echo "=========================================="
echo ""

if [ ${#AVAILABLE_AGENTS[@]} -eq 0 ]; then
    echo -e "${RED}No AI agents found!${NC}"
    echo "Please install at least one CLI to use multi-ai-collab."
    exit 1
elif [ ${#AVAILABLE_AGENTS[@]} -eq 1 ]; then
    echo -e "${YELLOW}Only 1 agent available: ${AVAILABLE_AGENTS[*]}${NC}"
    echo "Cross-review requires at least 2 agents."
    echo "Consider installing additional CLIs for full functionality."
elif [ ${#AVAILABLE_AGENTS[@]} -eq 2 ]; then
    echo -e "${GREEN}2 agents available: ${AVAILABLE_AGENTS[*]}${NC}"
    echo "Ready for basic cross-review!"
else
    echo -e "${GREEN}All 3 agents available: ${AVAILABLE_AGENTS[*]}${NC}"
    echo "Ready for full multi-AI collaboration!"
fi

echo ""
echo "Available agents: ${AVAILABLE_AGENTS[*]}"
echo ""

# Output JSON for programmatic use
if [ "$1" == "--json" ]; then
    echo ""
    echo "JSON output:"
    echo "{"
    echo "  \"agents\": ["
    for i in "${!AVAILABLE_AGENTS[@]}"; do
        if [ $i -eq $((${#AVAILABLE_AGENTS[@]} - 1)) ]; then
            echo "    \"${AVAILABLE_AGENTS[$i]}\""
        else
            echo "    \"${AVAILABLE_AGENTS[$i]}\","
        fi
    done
    echo "  ],"
    echo "  \"count\": ${#AVAILABLE_AGENTS[@]},"
    echo "  \"ready_for_cross_review\": $([ ${#AVAILABLE_AGENTS[@]} -ge 2 ] && echo 'true' || echo 'false')"
    echo "}"
fi
