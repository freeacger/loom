# Skill Development Workflow

Operational guide for editing, evaluating, publishing, and updating skills in this repository.

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

Install paths are always populated from skills.sh via `npx skills add`.
Never write to install paths directly.

---

## Standard Workflow: Edit → Publish → Pull

### 1. Edit

Edit `skills/<name>/SKILL.md` in this repository only.

Check divergence before editing if unsure:
```bash
diff skills/<name>/SKILL.md ~/.claude/skills/<name>/SKILL.md
```

### 2. Publish

Commit and push to GitHub. skills.sh re-scans the repo automatically.

```bash
git add skills/<name>
git commit -m "..."
git push
```

Verify the publish (allow a few minutes):
```
https://skills.sh/freeacger/loom/<name>
```

### 3. Pull

Once skills.sh is updated, pull to both install paths:

```bash
npx skills add freeacger/loom/<name>
```

---

## Evaluating a Skill with skill-creator

Always point the subagent at the **repo path**, not the install path:

```
Skill path: /Users/youjunxin/workspace/tools/loom/skills/<name>
```

After the eval loop is complete, publish and pull (steps 2–3 above).

---

## Adding a New Skill

1. Create `skills/<new-name>/SKILL.md`.
2. Run skill-creator evals from the repo path.
3. Publish and pull (steps 2–3 above).

---

## Removing a Skill

1. Delete `skills/<name>/` from the repository.
2. Remove installed copies:
   ```bash
   rm -r ~/.claude/skills/<name>
   rm -r ~/.agents/skills/<name>
   ```
3. Commit and push.

---

## Checking for Divergence

To detect any install path that has drifted from the repo (e.g. direct edits made by mistake):

```bash
for skill in skills/*/; do
  name=$(basename "$skill")
  diff -q "$skill/SKILL.md" ~/.claude/skills/$name/SKILL.md 2>/dev/null \
    && echo "✓ $name" || echo "✗ $name (diverged)"
done
```

---

## Pre-Commit Checklist

- [ ] Edit was made in `skills/<name>/SKILL.md`, not in an install path
- [ ] `git diff` reflects only the intended change
- [ ] `skills/<name>/CHANGELOG.md` updated if the change is user-visible
- [ ] After push: verify `https://skills.sh/freeacger/loom/<name>` shows the updated version
- [ ] `npx skills add freeacger/loom/<name>` run to update install paths
