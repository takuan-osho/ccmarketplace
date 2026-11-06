#!/bin/sh
# Start llama.cpp's llama-server for PLaMo 3 Translate (Q4_K_M). 127.0.0.1 only.
# PLAMO_MODEL picks the size: 0.8b (default, about 2.6x faster) or 2b (slightly more accurate).
# -hf downloads the GGUF on first run into the Hugging Face cache (~/.cache/huggingface/hub, or $HF_HOME / $LLAMA_CACHE if set).
# --jinja + --no-prefill-assistant: from the model card.
# --yarn-beta-*: workaround for the ignored GGUF yarn_truncate=false (see README, "YaRN workaround").
#   Same values for 0.8b and 2b (checked with yarn_args.py). Same values pfnet/plamo-translate-cli computes (src/plamo_translate/servers/llama_cpp/server.py:52-80, used at :165).
#   Recompute for a GGUF with: python3 yarn_args.py <file.gguf>. Remove once llama.cpp honors yarn_truncate.
exec llama-server \
  -hf "pfnet/plamo-3-translate-${PLAMO_MODEL:-0.8b}-GGUF:Q4_K_M" \
  -c 16384 \
  --host 127.0.0.1 --port "${LLAMA_PORT:-8766}" \
  --alias plamo-3-translate \
  --jinja --no-prefill-assistant \
  --yarn-beta-fast 31.738495 --yarn-beta-slow 1.0040927 \
  "$@"
