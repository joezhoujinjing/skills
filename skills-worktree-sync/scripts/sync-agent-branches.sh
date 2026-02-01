#!/usr/bin/env bash
set -euo pipefail

# Sync agent-specific branches to main and push updates.
# Usage: sync-agent-branches.sh <agent|all> [--repo <bare-repo-path>]
# Defaults assume the bare repo is ~/skills and worktrees live under ~/.<agent>/skills.

usage() {
  cat <<'USAGE'
Usage: sync-agent-branches.sh <agent|all> [--repo <bare-repo-path>]

Agents supported by default: claude, codex, cursor

Examples:
  sync-agent-branches.sh claude
  sync-agent-branches.sh all
  sync-agent-branches.sh all --repo /Users/jinjingzhou/skills
USAGE
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

agent_arg="$1"
shift

repo_path="$HOME/skills"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      repo_path="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ ! -d "$repo_path" ]]; then
  echo "Bare repo not found at: $repo_path" >&2
  exit 1
fi

# Map agents to worktree paths.
agent_worktree() {
  case "$1" in
    claude) echo "$HOME/.claude/skills" ;;
    codex)  echo "$HOME/.codex/skills" ;;
    cursor) echo "$HOME/.cursor/skills" ;;
    *)
      echo "Unknown agent: $1" >&2
      exit 1
      ;;
  esac
}

# Fetch once at the bare repo to ensure origin/main is up to date.
git --git-dir="$repo_path" fetch origin

sync_one() {
  local agent="$1"
  local worktree
  worktree="$(agent_worktree "$agent")"

  if [[ ! -d "$worktree" ]]; then
    echo "Missing worktree for $agent at $worktree" >&2
    exit 1
  fi

  echo "==> Syncing $agent ($worktree)"
  git -C "$worktree" fetch origin main:refs/remotes/origin/main
  git -C "$worktree" pull --rebase origin main
  git -C "$worktree" push origin "HEAD:agents/$agent"
  echo "==> Pushing $agent changes to main"
  git -C "$worktree" push origin "HEAD:main"
}

if [[ "$agent_arg" == "all" ]]; then
  for agent in claude codex cursor; do
    sync_one "$agent"
  done
else
  sync_one "$agent_arg"
fi
