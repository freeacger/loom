# Skill Development Workflow

Operational guide for editing, evaluating, publishing, and updating skills in this repository.

## Setup

Install the git pre-push hook (one-time per clone):

```bash
mise install
mise run install-hooks
```

This symlinks `scripts/hooks/pre-push` → `.git/hooks/pre-push`. The hook runs `mise run check-publish` before every push and aborts if publish-safe repo checks fail.

The repository pins Python in `mise.toml`. Run Python-dependent commands inside the repo through the `mise` environment instead of depending on the system `python3`.

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

`mise run check-publish` is the push-safe gate. It validates repo-local publish prerequisites without checking install-path divergence, so it works with the required `publish -> pull` order.

`Agent Skills` validation is tracked separately in phase 1. Use `mise run check-skill-spec` when you want to validate all project skill directories against the reference specification. This command is intentionally not part of `mise run check`, the pre-push hook, or the publish/release flow yet.

For breaking design-tree rollouts, additional family-specific checks are required:
- `mise run check-design-tree-evals`
- `mise run check-design-tree-canonical`

---

## Standard Workflow: Edit → Release

### 1. Edit

Edit `skills/<name>/SKILL.md` in this repository only.

### 2. Release

```bash
mise run release <name> "<commit message>"
```

This runs in sequence:
1. `mise run check-publish`
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
- `mise/tasks/check-design-tree-evals`
- `mise/tasks/check-design-tree-canonical`
- `skills/design-tree-core`
- `skills/design-orchestrator`
- `skills/design-structure`
- `skills/design-refinement`
- `skills/design-readiness-check`
- `skills/decision-evaluation`
- `mise/tasks/check`
- related workflow / README documentation

Use this path for shared derivation rules, target-type contract changes, handoff rules, anti-bloat governance changes, and any breaking `design_state` rollout.

---

## Individual Tasks

```bash
mise run check-skill-json               # validate skills/*/evals/evals.json
mise run check-publish                  # push-safe repo health gate without install sync checks
mise run check                          # repo health gate: JSON validity + install divergence
mise run check-skill-spec               # optional Agent Skills spec validation for all project skills
mise run check-design-tree-evals        # validate design-tree eval metadata and design_target_type coverage
mise run check-design-tree-canonical    # validate minimal canonical behavior matrix coverage
mise run publish <name> "<message>"     # git add + commit + push only
mise run pull                           # npx skills add freeacger/loom -g (all skills)
mise run release-design-tree "<msg>"    # publish shared design-tree changes + pull
```

`release-design-tree` now runs these checks in order before publishing:
1. `mise run check-publish`
2. `mise run check-skill-spec`
3. `mise run check-design-tree-evals`
4. `mise run check-design-tree-canonical`

## Agent Skills Validation (Phase 1)

`Agent Skills` is a compatibility target and reference specification for this repository. In phase 1, `check-skill-spec` validates every top-level directory under `skills/`.

Run:

```bash
mise run check-skill-spec
```

Behavior contract:

- If `skills-ref` is installed, the command validates all project skills and returns a non-zero exit code on any spec failure.
- If `skills-ref` is missing, the command fails fast with installation guidance instead of pretending the check passed.
- This check is recommended during the pilot, but it is not a push gate and is not called by `mise run check`.

Phase 1 intentionally does **not**:

- replace `skills.sh`
- auto-install `agentskills` or `skills-ref`
- require repo-wide frontmatter cleanup
- change `mise run release`, `mise run pull`, or `mise run publish`

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
- [ ] `mise run check-publish` passes before pushing
- [ ] `mise run check` passes after pull when install paths are expected to be in sync
- [ ] `mise run check-skill-spec` was run when touching any project skill
- [ ] `mise run check-design-tree-evals` was run for design-tree contract changes
- [ ] `mise run check-design-tree-canonical` was run for design-tree contract changes
- [ ] `skills/<name>/CHANGELOG.md` updated if the change is user-visible
- [ ] After push: verify `https://skills.sh/freeacger/loom/<name>` shows the updated version
