---
name: skills-worktree-sync
description: "Set up and maintain a shared skills Git repo using git worktrees across multiple agent folders (e.g., ~/.claude/skills, ~/.codex/skills, ~/.cursor/skills). Use when a user wants skills synced across tools, needs to convert an existing skills repo to worktrees, add new agent worktrees, or keep local-only folders (like .system) preserved as untracked content."
---

# Skills Worktree Sync

## Quick start (convert an existing skills repo)

1. Identify the current skills repo (default: `~/.claude/skills`).
2. Back up any local-only/untracked folders before moving the repo.
3. Create a bare parent repo (canonical store) at the agreed path.
4. Add per-agent worktrees with unique branches (use `claude` for `~/.claude/skills`).
5. Restore local-only folders (e.g., `.system` under Codex) as untracked.
6. Verify worktrees with `git worktree list`.

Example (use the user's chosen parent repo path):

```bash
# 1) Back up local-only folders (adjust names as needed)
mkdir -p ~/.skills-untracked-backup ~/.skills-worktree-backup
mv ~/.claude/skills/agent-session-organizer ~/.skills-untracked-backup/

# 2) Move the existing repo aside instead of deleting it
mv ~/.claude/skills ~/.skills-worktree-backup/claude-skills

# 3) Create the bare repo store
# (source repo can be any existing skills repo)
git clone --bare ~/.skills-worktree-backup/claude-skills /Users/jinjingzhou/skills

# 4) Add worktrees (main can only be checked out once)
git --git-dir=/Users/jinjingzhou/skills worktree add -b claude ~/.claude/skills main
git --git-dir=/Users/jinjingzhou/skills worktree add -b codex ~/.codex/skills main
git --git-dir=/Users/jinjingzhou/skills worktree add -b cursor ~/.cursor/skills main

# 5) Restore local-only folders
mv ~/.skills-untracked-backup/agent-session-organizer ~/.claude/skills/
# For Codex, restore .system if it existed
# mv ~/.skills-worktree-backup/codex-skills/.system ~/.codex/skills/

# 6) Verify
git --git-dir=/Users/jinjingzhou/skills worktree list
```

## Sync workflow

Use this to keep branches aligned with `origin/main` while allowing edits from any agent folder.

```bash
# Update claude worktree (tracks claude branch)
cd ~/.claude/skills
git fetch origin
git pull --rebase origin claude

# Update other worktrees (rebases their branch onto origin/main)
cd ~/.codex/skills
git fetch origin
git pull --rebase origin main

cd ~/.cursor/skills
git fetch origin
git pull --rebase origin main
```

If you commit from a non-main worktree and want it on `main`, either:

```bash
# Option A: push the branch and merge on GitHub
git push origin codex

# Option B: push directly to main (only if you know it's safe)
git push origin HEAD:main
```

## Add a new agent folder

```bash
git --git-dir=/Users/jinjingzhou/skills worktree add -b <agent-branch> <path-to-agent-skills> main
```

Pick a unique branch name per agent folder (e.g., `windsurf`, `zed`, `copilot`).

## Remove a worktree

```bash
git --git-dir=/Users/jinjingzhou/skills worktree remove <path-to-agent-skills>
```

If the folder contains untracked files you want to keep, move them out first.
