# Executing-Plans Skill Diff Report

Source local copy: /tmp/executing-plans-source.md

## Unified Diff (git diff style)
```diff
--- /tmp/executing-plans-source.md	2026-02-27 13:40:01
+++ executing-plans/SKILL.md	2026-02-27 13:40:39
@@ -46,9 +46,18 @@
 
 After all tasks complete and verified:
 - Announce: "I'm using the finishing-a-development-branch skill to complete this work."
-- **REQUIRED SUB-SKILL:** Use superpowers:finishing-a-development-branch
+- **REQUIRED SUB-SKILL:** Use loom:finishing-a-development-branch
 - Follow that skill to verify tests, present options, execute choice
 
+**Archive the executed plan after successful completion:**
+
+```bash
+mkdir -p docs/exec-plans/completed
+mv docs/exec-plans/active/<filename>.md docs/exec-plans/completed/<filename>.md
+```
+
+Then report which plan file was moved so the reviewer can verify archival state.
+
 ## When to Stop and Ask for Help
 
 **STOP executing immediately when:**
@@ -79,6 +88,6 @@
 ## Integration
 
 **Required workflow skills:**
-- **superpowers:using-git-worktrees** - REQUIRED: Set up isolated workspace before starting
-- **superpowers:writing-plans** - Creates the plan this skill executes
-- **superpowers:finishing-a-development-branch** - Complete development after all tasks
+- **loom:using-git-worktrees** - REQUIRED: Set up isolated workspace before starting
+- **loom:writing-plans** - Creates the plan this skill executes
+- **loom:finishing-a-development-branch** - Complete development after all tasks
```

## Difference Summary for Reviewer
- Namespace localization: `superpowers:*` references were intentionally changed to `loom:*`.
- Added explicit archive rule for moving completed plans from `docs/exec-plans/active/<filename>.md` to `docs/exec-plans/completed/<filename>.md`.
- Core execution flow (review -> batch execution -> report checkpoints -> blocker escalation) is preserved.
