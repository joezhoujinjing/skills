#!/usr/bin/env bash
a="$1"
d=$(pwd | tr '/' '-' | sed 's/^-//')
if [ "$a" = "claude" ]; then
  base="$HOME/.claude/projects/-$d"
  if [ -n "$CLAUDE_SESSION_ID" ]; then
    echo "$base/${CLAUDE_SESSION_ID}.jsonl"
  else
    l=$(ls -t "$base"/*.jsonl 2>/dev/null | head -1)
    echo "${l:-$base}"
  fi
elif [ "$a" = "cursor" ]; then
  base="$HOME/.cursor/projects/$d/agent-transcripts"
  l=$(ls -t "$base"/*.txt 2>/dev/null | head -1)
  echo "${l:-$base}"
elif [ "$a" = "codex" ]; then
  base="$HOME/.codex/sessions"
  if [ -n "$CODEX_THREAD_ID" ]; then
    m=$(find "$base" -type f -name "*${CODEX_THREAD_ID}*.jsonl" 2>/dev/null | tail -1)
    if [ -n "$m" ]; then
      echo "$m"
    else
      l=$(find "$base" -type f -name "*.jsonl" 2>/dev/null | xargs ls -t 2>/dev/null | head -1)
      echo "${l:-$base}"
    fi
  else
    l=$(find "$base" -type f -name "*.jsonl" 2>/dev/null | xargs ls -t 2>/dev/null | head -1)
    echo "${l:-$base}"
  fi
fi
