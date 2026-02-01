#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: setup-worktrees.sh --repo-url <repo-url> [--bare <path>]

Defaults:
  --bare ~/skills

This initializes a bare repo (if missing), creates worktrees for
claude/codex/cursor on branches agents/<name>, enables auto upstream,
then runs the sync script.
USAGE
}

repo_url=""
bare_path="$HOME/skills"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-url)
      repo_url="$2"
      shift 2
      ;;
    --bare)
      bare_path="$2"
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

if [[ -z "$repo_url" ]]; then
  echo "--repo-url is required" >&2
  usage
  exit 1
fi

script_dir="$(cd "$(dirname "$0")" && pwd)"

if [[ ! -d "$bare_path" ]]; then
  git clone --bare "$repo_url" "$bare_path"
fi

for agent in claude codex cursor; do
  worktree="$HOME/.${agent}/skills"
  branch="agents/${agent}"
  if [[ ! -d "$worktree" ]]; then
    git --git-dir="$bare_path" worktree add -b "$branch" "$worktree" main
  fi
done

git config --global push.autoSetupRemote true

"$script_dir/sync-agent-branches.sh" all --repo "$bare_path"
