# AGENTS.md — Workflow Rules for loom

This file defines mandatory workflows for modifying, evaluating, and releasing skills in this repository.
All contributors (human or agent) must follow these rules.

---

## Single Source of Truth

**The canonical version of every skill lives in `skills/<name>/SKILL.md` inside this repository.**

The installed path (`~/.claude/skills/<name>/SKILL.md`) is a deployment target, not a source.
Never edit the installed path directly. If you do, the installed version diverges from the repo and
the change is invisible to git, code review, and future installers.

```
loom/skills/<name>/SKILL.md   ← edit here
        │
        └── install ──→  ~/.claude/skills/<name>/SKILL.md   ← do NOT edit here
```

---

## Editing a Skill

1. Open and edit `skills/<name>/SKILL.md` in this repository.
2. Verify the change looks correct (`git diff`).
3. Sync the updated file to the installed location:
   ```bash
   cp skills/<name>/SKILL.md ~/.claude/skills/<name>/SKILL.md
   ```
4. Stage and commit the repo file, then push.

If you need to check what the installed version contains before editing, diff first:

```bash
diff skills/<name>/SKILL.md ~/.claude/skills/<name>/SKILL.md
```

If there is divergence, investigate which version is newer before proceeding.

---

## Evaluating a Skill with skill-creator

When running skill-creator evals, point the subagent at the **repo path**, not the installed path:

```
Skill path: /Users/youjunxin/workspace/tools/loom/skills/<name>
```

This ensures the eval measures the version tracked in git.

After the eval loop is complete and you are satisfied with the result, sync to the installed path (step 3 above), then commit.

---

## Adding a New Skill

1. Create `skills/<new-name>/SKILL.md` in this repository.
2. Run skill-creator evals from the repo path.
3. When the skill is ready, install it:
   ```bash
   cp -r skills/<new-name> ~/.claude/skills/<new-name>
   ```
4. Commit and push.

---

## Removing a Skill

1. Delete the directory from `skills/` in this repository.
2. Remove the installed copy:
   ```bash
   rm -r ~/.claude/skills/<name>
   ```
3. Commit and push.

---

## Checklist Before Committing a Skill Change

- [ ] Edit was made in `skills/<name>/SKILL.md` (not in `~/.claude/skills/`)
- [ ] `diff skills/<name>/SKILL.md ~/.claude/skills/<name>/SKILL.md` shows no divergence
- [ ] `git diff` reflects the intended change
- [ ] CHANGELOG.md updated if the change is user-visible
