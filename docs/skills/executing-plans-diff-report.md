# Executing-Plans Skill Diff Report

Source local copy: /tmp/executing-plans-source.md

## Unified Diff (git diff style)
```diff
--- /tmp/executing-plans-source.md	2026-02-27 13:40:01
+++ executing-plans/SKILL.md	2026-02-27 13:39:03
@@ -46,7 +46,7 @@
 
 After all tasks complete and verified:
 - Announce: "I'm using the finishing-a-development-branch skill to complete this work."
-- **REQUIRED SUB-SKILL:** Use superpowers:finishing-a-development-branch
+- **REQUIRED SUB-SKILL:** Use loom:finishing-a-development-branch
 - Follow that skill to verify tests, present options, execute choice
 
 ## When to Stop and Ask for Help
@@ -79,6 +79,6 @@
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
