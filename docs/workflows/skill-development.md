# Skill Development Workflow

Operational guide for editing, evaluating, publishing, and updating skills in this repository.

## Setup

Install the git pre-push hook (one-time per clone):

```bash
mise run install-hooks
```

This symlinks `scripts/hooks/pre-push` → `.git/hooks/pre-push`. The hook runs `mise run check` before every push and aborts if any install path has diverged from the repo.

---

## Directory Layout

```
loom/skills/<name>/SKILL.md   ← canonical source, always edit here
        │
        └── publish ──→  GitHub → skills.sh (auto-discovered)
                                        │
                                        └── pull ──→  ~/.claude/skills/<name>/
                                                       ~/.agents/skills/<name>/
```

Install paths are always populated from skills.sh via `mise run pull`.
Never write to install paths directly.

---

## Standard Workflow: Edit → Release

### 1. Edit

Edit `skills/<name>/SKILL.md` in this repository only.

### 2. Release

```bash
mise run release <name> "<commit message>"
```

This runs in sequence:
1. `git add skills/<name>` → `git commit` → `git push`
2. `cd ~ && npx skills add freeacger/loom -y -g` (updates all skills globally)

If publish finds nothing to commit, it skips gracefully and proceeds to pull.

> **Note:** skills.sh may have a cache delay — if you just pushed, wait 2 minutes and re-run `mise run pull`.

---

## Individual Tasks

```bash
mise run check                          # diff repo vs all install paths
mise run publish <name> "<message>"     # git add + commit + push only
mise run pull                           # npx skills add freeacger/loom -g (all skills)
```

---

## Evaluating a Skill with skill-creator

Always point the subagent at the **repo path**, not the install path:

```
Skill path: /Users/youjunxin/workspace/tools/loom/skills/<name>
```

After the eval loop is complete, run:

```bash
mise run release <name> "<commit message>"
```

---

## Adding a New Skill

1. Create `skills/<new-name>/SKILL.md`.
2. Run skill-creator evals from the repo path.
3. `mise run release <new-name> "feat(<new-name>): initial version"`

---

## Removing a Skill

1. Delete `skills/<name>/` from the repository.
2. Remove installed copies:
   ```bash
   rm -r ~/.claude/skills/<name>
   rm -r ~/.agents/skills/<name>
   ```
3. `git add -A && git commit -m "... " && git push`

---

## Pre-Commit Checklist

- [ ] Edit was made in `skills/<name>/SKILL.md`, not in an install path
- [ ] `mise run check` passes (or divergence is intentional and will be resolved by release)
- [ ] `skills/<name>/CHANGELOG.md` updated if the change is user-visible
- [ ] After push: verify `https://skills.sh/freeacger/loom/<name>` shows the updated version
