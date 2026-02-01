---
name: skills-worktree-sync
description: "Set up and maintain a shared skills Git repo using git worktrees across multiple agent folders (e.g., ~/.claude/skills, ~/.codex/skills, ~/.cursor/skills). Use when a user wants skills synced across tools, needs to clone a canonical repo to ~/skills, add agent worktrees with per-agent branches, keep local-only folders (like .system) preserved as untracked content, or use the sync script to rebase agent branches onto main and push updates."
---

# Skills Worktree Sync

## One-command setup (recommended)

```bash
./skills-worktree-sync/scripts/setup-worktrees.sh --repo-url <repo-url> --bare ~/skills
```

This creates the bare repo, adds `agents/<name>` worktrees for `claude`, `codex`, and `cursor`,
enables auto upstream tracking, then runs the sync script.

## Quick start (clone + create worktrees)

1. Clone the skills repo to `~/skills` (bare repo; canonical store).
2. Create a worktree for each agent folder with its own branch (recommended: `agents/<name>`).
3. Restore any local-only folders (e.g., `.system` under Codex) as untracked.
4. Verify worktrees with `git worktree list`.

Example (use the user's chosen parent repo path):

```bash
# 1) Clone as a bare repo (canonical store)
git clone --bare <repo-url> ~/skills

# 2) Create agent worktrees (each agent has its own branch)
git --git-dir=~/skills worktree add -b agents/claude ~/.claude/skills main
git --git-dir=~/skills worktree add -b agents/codex ~/.codex/skills main
git --git-dir=~/skills worktree add -b agents/cursor ~/.cursor/skills main

# 3) Restore local-only folders (if any)
# mv ~/.skills-untracked-backup/agent-session-organizer ~/.claude/skills/
# mv ~/.skills-worktree-backup/codex-skills/.system ~/.codex/skills/

# 4) Verify
git --git-dir=~/skills worktree list
```

## Remote branch tracking (recommended during setup)

Enable automatic upstream tracking for new branches:

```bash
git config --global push.autoSetupRemote true
```

## Sync workflow

Use the bundled script to sync agent branches to `main` and push updates:

```bash
./skills-worktree-sync/scripts/sync-agent-branches.sh all --repo ~/skills
./skills-worktree-sync/scripts/sync-agent-branches.sh claude --repo ~/skills
```

If you commit from an agent worktree, the script will rebase onto `main` and push `HEAD:agents/<agent>`.
Merge to `main` via your preferred flow (PR or direct push).

If the script isn't executable:

```bash
chmod +x skills-worktree-sync/scripts/sync-agent-branches.sh
```

## Agent registry (extendable)

Default agents are `claude`, `codex`, and `cursor` with worktrees at:

```
~/.claude/skills
~/.codex/skills
~/.cursor/skills
```

To add more agents, create a new worktree and update the agent map in:
`skills-worktree-sync/scripts/sync-agent-branches.sh`.

When updating a skill inside an agent worktree, commit and push to that agent's branch (e.g., `agents/codex`, `agents/cursor`) by default.

## Add a new agent folder

```bash
git --git-dir=~/skills worktree add -b <agent-branch> <path-to-agent-skills> main
```

Pick a unique branch name per agent folder (e.g., `windsurf`, `zed`, `copilot`).

## Remove a worktree

```bash
git --git-dir=/Users/jinjingzhou/skills worktree remove <path-to-agent-skills>
```

If the folder contains untracked files you want to keep, move them out first.
