# Skill Development Workflow

Operational guide for editing, evaluating, publishing, and updating skills in this repository.

## Setup

Install the git pre-push hook (one-time per clone):

```bash
mise run install-hooks
```

This symlinks `scripts/hooks/pre-push` → `.git/hooks/pre-push`. The hook runs `mise run check` before every push and aborts if repo health checks fail.

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

`mise run check` is the unified health gate for this repo. It currently verifies:
- `skills/*/evals/evals.json` syntax via `python3 -m json.tool`
- divergence between repo skill directories and installed copies

---

## Standard Workflow: Edit → Release

### 1. Edit

Edit `skills/<name>/SKILL.md` in this repository only.

### 2. Release

```bash
mise run release <name> "<commit message>"
```

This runs in sequence:
1. `mise run check`
2. `git add skills/<name>` → `git commit` → `git push`
3. `cd ~ && npx skills add freeacger/loom -y -g` (updates all skills globally)

If publish finds nothing to commit, it skips gracefully and proceeds to pull.

> **Note:** skills.sh may have a cache delay — if you just pushed, wait 2 minutes and re-run `mise run pull`.

### Shared Design-Tree Changes

When a change spans the shared design-tree core and multiple design skills, do not publish each skill separately by memory.

Use:

```bash
mise run release-design-tree "<commit message>"
```

This stages and publishes:
- `mise/tasks/check-skill-json`
- `skills/design-tree-core`
- `skills/design-orchestrator`
- `skills/design-structure`
- `skills/design-refinement`
- `skills/design-readiness-check`
- `mise/tasks/check`
- related workflow / README documentation

Use this path for shared derivation rules, handoff rules, and anti-bloat governance changes.

---

## Individual Tasks

```bash
mise run check-skill-json               # validate skills/*/evals/evals.json
mise run check                          # repo health gate: JSON validity + install divergence
mise run publish <name> "<message>"     # git add + commit + push only
mise run pull                           # npx skills add freeacger/loom -g (all skills)
mise run release-design-tree "<msg>"    # publish shared design-tree changes + pull
```

---

## Evaluating a Skill with skill-creator

Always point the subagent at the **repo path**, not the install path:

```
Skill path: /Users/youjunxin/workspace/tools/loom/skills/<name>
```

Eval 工作目录（`*-workspace/`）必须放在 `tests/` 下，不要留在 `skills/` 内——pre-push hook 会将 `skills/` 下非标准目录识别为未安装技能并报警。

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
- [ ] `mise run check` passes (eval JSON syntax + install divergence), or any temporary divergence is expected and will be resolved by release
- [ ] `skills/<name>/CHANGELOG.md` updated if the change is user-visible
- [ ] After push: verify `https://skills.sh/freeacger/loom/<name>` shows the updated version
