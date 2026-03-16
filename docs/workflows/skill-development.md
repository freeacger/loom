# Skill Development Workflow

Operational guide for editing, evaluating, publishing, and updating skills in this repository.

---

## Directory Layout

```
loom/skills/<name>/SKILL.md   ← canonical source, always edit here
        │
        ├── install ──→  ~/.claude/skills/<name>/    ← Claude Code
        └── install ──→  ~/.agents/skills/<name>/    ← other agents
```

skills.sh auto-discovers skills by scanning `skills/` in the GitHub repo.
`git push` is the publish step — no separate publish command needed.

---

## Editing a Skill

1. Edit `skills/<name>/SKILL.md` in this repository.
2. Check the diff: `git diff`
3. Sync to both install paths:
   ```bash
   cp -r skills/<name> ~/.claude/skills/<name>
   cp -r skills/<name> ~/.agents/skills/<name>
   ```
4. Commit and push.

If you suspect divergence before editing, diff first:
```bash
diff skills/<name>/SKILL.md ~/.claude/skills/<name>/SKILL.md
```
Investigate which side is newer before proceeding.

---

## Publishing to skills.sh

Publishing is automatic — `git push` triggers skills.sh to re-scan the repo.

**Verify the publish:**
```
https://skills.sh/freeacger/loom/<name>
```
Allow a few minutes for the registry to refresh.

---

## Pulling an Updated Skill Locally

After verifying the skill is live on skills.sh, pull it to both install paths with one command:

```bash
npx skills add freeacger/loom/<name>
```

For routine maintenance (update all installed skills):
```bash
npx skills update
```

---

## Evaluating a Skill with skill-creator

Always point the subagent at the **repo path**, not the installed path:

```
Skill path: /Users/youjunxin/workspace/tools/loom/skills/<name>
```

After the eval loop is complete, sync to install paths (see Editing a Skill, step 3), then commit.

---

## Adding a New Skill

1. Create `skills/<new-name>/SKILL.md`.
2. Run skill-creator evals from the repo path.
3. When ready, sync to install paths and commit.
4. Push — skills.sh will pick it up automatically.

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

## Pre-Commit Checklist

- [ ] Edit was made in `skills/<name>/SKILL.md`, not in an install path
- [ ] Both install paths are in sync with the repo file
- [ ] `git diff` reflects only the intended change
- [ ] `skills/<name>/CHANGELOG.md` updated if the change is user-visible
- [ ] After push: verify `https://skills.sh/freeacger/loom/<name>` shows the updated version
