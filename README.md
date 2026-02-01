# Skills Repo

Shared skills for multiple coding agents. Each agent works in its own worktree and
branch, while a central `main` branch distributes updates to everyone.

## One-command setup

```bash
./skills-worktree-sync/scripts/setup-worktrees.sh --repo-url <repo-url> --bare ~/skills
```

## How it works

- A bare repo at `~/skills` is the canonical store.
- Each agent has a worktree at `~/.<agent>/skills` on `agents/<agent>`.
- The sync script rebases agent branches onto `main` and pushes updates.
- When `main` updates, running the sync script pulls changes back to each agent.
