# Executing-Plans Skill Port Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use loom:executing-plans to implement this plan task-by-task.

**Goal:** Port `skills/executing-plans` from the upstream superpowers repository into this loom repository with local namespace alignment, contract checks, and migration notes.

**Architecture:** Build the migration with strict TDD using a shell-based contract test that validates required skill text. Start with a minimal stub, then progressively port the full workflow content, localize cross-skill references from `superpowers:*` to `loom:*`, and finally capture provenance/decisions in docs. Keep the implementation DRY and YAGNI: only add files needed for a maintainable skill port.

**Tech Stack:** Markdown (`SKILL.md`), Bash, `rg` (ripgrep), Git commits, local skill conventions (`@writing-plans`, `@executing-plans`).

---

### Task 1: Create Contract Test Harness and Minimal Skill Stub

**Files:**
- Create: `tests/skills/test_executing_plans_skill.sh`
- Create: `executing-plans/SKILL.md`

**Step 1: Write the failing test**

```bash
#!/usr/bin/env bash
set -euo pipefail

SKILL_FILE="executing-plans/SKILL.md"

assert_contains() {
  local pattern="$1"
  local file="$2"
  if ! rg -q --fixed-strings "$pattern" "$file"; then
    echo "FAIL: missing '$pattern' in $file" >&2
    exit 1
  fi
}

if [[ ! -f "$SKILL_FILE" ]]; then
  echo "FAIL: missing $SKILL_FILE" >&2
  exit 1
fi

assert_contains "name: executing-plans" "$SKILL_FILE"
assert_contains "description: Use when you have a written implementation plan to execute in a separate session with review checkpoints" "$SKILL_FILE"
assert_contains "I'm using the executing-plans skill to implement this plan." "$SKILL_FILE"

echo "PASS: base executing-plans skill contract checks passed"
```

**Step 2: Run test to verify it fails**

Run: `bash tests/skills/test_executing_plans_skill.sh`
Expected: FAIL with `missing executing-plans/SKILL.md`

**Step 3: Write minimal implementation**

```markdown
---
name: executing-plans
description: Use when you have a written implementation plan to execute in a separate session with review checkpoints
---

# Executing Plans

## Overview

**Announce at start:** "I'm using the executing-plans skill to implement this plan."
```

**Step 4: Run test to verify it passes**

Run: `bash tests/skills/test_executing_plans_skill.sh`
Expected: PASS with `base executing-plans skill contract checks passed`

**Step 5: Commit**

```bash
git add tests/skills/test_executing_plans_skill.sh executing-plans/SKILL.md
git commit -m "test: add executing-plans contract harness and minimal stub"
```

### Task 2: Port Full Upstream Workflow Content

**Files:**
- Modify: `tests/skills/test_executing_plans_skill.sh`
- Modify: `executing-plans/SKILL.md`

**Step 1: Write the failing test**

Replace `tests/skills/test_executing_plans_skill.sh` with:

```bash
#!/usr/bin/env bash
set -euo pipefail

SKILL_FILE="executing-plans/SKILL.md"

assert_contains() {
  local pattern="$1"
  local file="$2"
  if ! rg -q --fixed-strings "$pattern" "$file"; then
    echo "FAIL: missing '$pattern' in $file" >&2
    exit 1
  fi
}

if [[ ! -f "$SKILL_FILE" ]]; then
  echo "FAIL: missing $SKILL_FILE" >&2
  exit 1
fi

assert_contains "name: executing-plans" "$SKILL_FILE"
assert_contains "# Executing Plans" "$SKILL_FILE"
assert_contains "## The Process" "$SKILL_FILE"
assert_contains "### Step 1: Load and Review Plan" "$SKILL_FILE"
assert_contains "### Step 2: Execute Batch" "$SKILL_FILE"
assert_contains "### Step 3: Report" "$SKILL_FILE"
assert_contains "### Step 4: Continue" "$SKILL_FILE"
assert_contains "### Step 5: Complete Development" "$SKILL_FILE"
assert_contains "## When to Stop and Ask for Help" "$SKILL_FILE"
assert_contains "## When to Revisit Earlier Steps" "$SKILL_FILE"
assert_contains "## Remember" "$SKILL_FILE"
assert_contains "## Integration" "$SKILL_FILE"
assert_contains "Ready for feedback." "$SKILL_FILE"
assert_contains "Never start implementation on main/master branch without explicit user consent" "$SKILL_FILE"

echo "PASS: full executing-plans workflow contract checks passed"
```

**Step 2: Run test to verify it fails**

Run: `bash tests/skills/test_executing_plans_skill.sh`
Expected: FAIL with missing process section lines (for example `missing '## The Process'`)

**Step 3: Write minimal implementation**

Replace `executing-plans/SKILL.md` with the upstream structure and wording from:
`https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md`

```markdown
---
name: executing-plans
description: Use when you have a written implementation plan to execute in a separate session with review checkpoints
---

# Executing Plans

## Overview

Load plan, review critically, execute tasks in batches, report for review between batches.

**Core principle:** Batch execution with checkpoints for architect review.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

## The Process

### Step 1: Load and Review Plan
1. Read plan file
2. Review critically - identify any questions or concerns about the plan
3. If concerns: Raise them with your human partner before starting
4. If no concerns: Create TodoWrite and proceed

### Step 2: Execute Batch
**Default: First 3 tasks**

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed

### Step 3: Report
When batch complete:
- Show what was implemented
- Show verification output
- Say: "Ready for feedback."

### Step 4: Continue
Based on feedback:
- Apply changes if needed
- Execute next batch
- Repeat until complete

### Step 5: Complete Development

After all tasks complete and verified:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use superpowers:finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker mid-batch (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Between batches: just report and wait
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent

## Integration

**Required workflow skills:**
- **superpowers:using-git-worktrees** - REQUIRED: Set up isolated workspace before starting
- **superpowers:writing-plans** - Creates the plan this skill executes
- **superpowers:finishing-a-development-branch** - Complete development after all tasks
```

**Step 4: Run test to verify it passes**

Run: `bash tests/skills/test_executing_plans_skill.sh`
Expected: PASS with `full executing-plans workflow contract checks passed`

**Step 5: Commit**

```bash
git add tests/skills/test_executing_plans_skill.sh executing-plans/SKILL.md
git commit -m "feat: port upstream executing-plans workflow"
```

### Task 3: Localize Integration References to Loom Namespace

**Files:**
- Modify: `tests/skills/test_executing_plans_skill.sh`
- Modify: `executing-plans/SKILL.md`

**Step 1: Write the failing test**

Update assertions in `tests/skills/test_executing_plans_skill.sh`:

```bash
assert_contains "**REQUIRED SUB-SKILL:** Use loom:finishing-a-development-branch" "$SKILL_FILE"
assert_contains "**loom:using-git-worktrees**" "$SKILL_FILE"
assert_contains "**loom:writing-plans**" "$SKILL_FILE"
assert_contains "**loom:finishing-a-development-branch**" "$SKILL_FILE"
```

**Step 2: Run test to verify it fails**

Run: `bash tests/skills/test_executing_plans_skill.sh`
Expected: FAIL with missing `loom:` assertions while `superpowers:` references still exist

**Step 3: Write minimal implementation**

Apply this patch to `executing-plans/SKILL.md`:

```diff
-- **REQUIRED SUB-SKILL:** Use superpowers:finishing-a-development-branch
+- **REQUIRED SUB-SKILL:** Use loom:finishing-a-development-branch
@@
-- **superpowers:using-git-worktrees** - REQUIRED: Set up isolated workspace before starting
-- **superpowers:writing-plans** - Creates the plan this skill executes
-- **superpowers:finishing-a-development-branch** - Complete development after all tasks
+- **loom:using-git-worktrees** - REQUIRED: Set up isolated workspace before starting
+- **loom:writing-plans** - Creates the plan this skill executes
+- **loom:finishing-a-development-branch** - Complete development after all tasks
```

**Step 4: Run test to verify it passes**

Run: `bash tests/skills/test_executing_plans_skill.sh`
Expected: PASS with no missing assertions and exit code `0`

**Step 5: Commit**

```bash
git add tests/skills/test_executing_plans_skill.sh executing-plans/SKILL.md
git commit -m "refactor: localize executing-plans skill references to loom namespace"
```

### Task 4: Add Porting Provenance Notes

**Files:**
- Modify: `tests/skills/test_executing_plans_skill.sh`
- Create: `docs/skills/executing-plans-porting.md`

**Step 1: Write the failing test**

Append to `tests/skills/test_executing_plans_skill.sh`:

```bash
NOTES_FILE="docs/skills/executing-plans-porting.md"

if [[ ! -f "$NOTES_FILE" ]]; then
  echo "FAIL: missing $NOTES_FILE" >&2
  exit 1
fi

assert_contains "Source:" "$NOTES_FILE"
assert_contains "https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md" "$NOTES_FILE"
assert_contains "Local Changes:" "$NOTES_FILE"
assert_contains "Replaced superpowers namespace with loom namespace" "$NOTES_FILE"
```

**Step 2: Run test to verify it fails**

Run: `bash tests/skills/test_executing_plans_skill.sh`
Expected: FAIL with `missing docs/skills/executing-plans-porting.md`

**Step 3: Write minimal implementation**

Create `docs/skills/executing-plans-porting.md`:

```markdown
# Executing-Plans Skill Porting Notes

## Source
- Source: https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md
- Retrieved on: 2026-02-27

## Local Changes
- Replaced superpowers namespace with loom namespace in required sub-skill and integration references.
- Added repository-local contract test coverage in `tests/skills/test_executing_plans_skill.sh`.
- Preserved the original execution workflow semantics (review, batch execution, checkpoint reporting, blocker stop rules).
```

**Step 4: Run test to verify it passes**

Run: `bash tests/skills/test_executing_plans_skill.sh`
Expected: PASS with workflow + docs checks and exit code `0`

**Step 5: Commit**

```bash
git add tests/skills/test_executing_plans_skill.sh docs/skills/executing-plans-porting.md
git commit -m "docs: add executing-plans skill migration provenance"
```

### Task 5: Final Proofread with Local Source Download and Diff Report

**Files:**
- Create: `tests/skills/test_executing_plans_diff_report.sh`
- Create: `docs/skills/executing-plans-diff-report.md`
- Temp artifact (do not commit): `/tmp/executing-plans-source.md`
- Temp artifact (do not commit): `/tmp/executing-plans.diff`

**Step 1: Write the failing test**

Create `tests/skills/test_executing_plans_diff_report.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

REPORT_FILE="docs/skills/executing-plans-diff-report.md"

assert_contains() {
  local pattern="$1"
  local file="$2"
  if ! rg -q --fixed-strings "$pattern" "$file"; then
    echo "FAIL: missing '$pattern' in $file" >&2
    exit 1
  fi
}

if [[ ! -f "$REPORT_FILE" ]]; then
  echo "FAIL: missing $REPORT_FILE" >&2
  exit 1
fi

assert_contains "Source local copy: /tmp/executing-plans-source.md" "$REPORT_FILE"
assert_contains "## Unified Diff (git diff style)" "$REPORT_FILE"
assert_contains '```diff' "$REPORT_FILE"
assert_contains "--- /tmp/executing-plans-source.md" "$REPORT_FILE"
assert_contains "+++ executing-plans/SKILL.md" "$REPORT_FILE"
assert_contains "## Difference Summary for Reviewer" "$REPORT_FILE"

echo "PASS: executing-plans diff report contract checks passed"
```

**Step 2: Run test to verify it fails**

Run: `bash tests/skills/test_executing_plans_diff_report.sh`
Expected: FAIL with `missing docs/skills/executing-plans-diff-report.md`

**Step 3: Write minimal implementation**

1) Download upstream source to local `/tmp/<filename>.md` path:

```bash
curl -L https://raw.githubusercontent.com/obra/superpowers/main/skills/executing-plans/SKILL.md -o /tmp/executing-plans-source.md
```

2) Generate unified diff (`git diff` style) between source and implemented artifact:

```bash
diff -u /tmp/executing-plans-source.md executing-plans/SKILL.md > /tmp/executing-plans.diff || true
```

3) Create `docs/skills/executing-plans-diff-report.md`:

````markdown
# Executing-Plans Skill Diff Report

Source local copy: /tmp/executing-plans-source.md

## Unified Diff (git diff style)
```diff
--- /tmp/executing-plans-source.md
+++ executing-plans/SKILL.md
@@
- **REQUIRED SUB-SKILL:** Use superpowers:finishing-a-development-branch
+ **REQUIRED SUB-SKILL:** Use loom:finishing-a-development-branch
```

## Difference Summary for Reviewer
- Namespace localization: `superpowers:*` references were intentionally changed to `loom:*`.
- No behavioral workflow section was removed; only integration naming was localized for this repository.
````

4) Output diff points to reviewer in session response:

Run: `cat docs/skills/executing-plans-diff-report.md`
Expected: includes unified diff block and a concise difference summary delivered to the human reviewer.

**Step 4: Run test to verify it passes**

Run: `bash tests/skills/test_executing_plans_diff_report.sh`
Expected: PASS with `executing-plans diff report contract checks passed`

**Step 5: Commit**

```bash
git add tests/skills/test_executing_plans_diff_report.sh docs/skills/executing-plans-diff-report.md
git commit -m "test: add final proofreading diff report for executing-plans port"
```

### Task 6: Bake Plan Archiving Rule into Executing-Plans Skill

**Files:**
- Modify: `tests/skills/test_executing_plans_skill.sh`
- Modify: `executing-plans/SKILL.md`

**Step 1: Write the failing test**

Append these assertions to `tests/skills/test_executing_plans_skill.sh`:

```bash
assert_contains "Archive the executed plan after successful completion" "$SKILL_FILE"
assert_contains "docs/exec-plans/active/<filename>.md" "$SKILL_FILE"
assert_contains "docs/exec-plans/completed/<filename>.md" "$SKILL_FILE"
assert_contains "mkdir -p docs/exec-plans/completed" "$SKILL_FILE"
assert_contains "mv docs/exec-plans/active/<filename>.md docs/exec-plans/completed/<filename>.md" "$SKILL_FILE"
```

**Step 2: Run test to verify it fails**

Run: `bash tests/skills/test_executing_plans_skill.sh`
Expected: FAIL with missing archive rule assertions

**Step 3: Write minimal implementation**

Add this subsection to `executing-plans/SKILL.md` under `### Step 5: Complete Development`:

````markdown
**Archive the executed plan after successful completion:**

```bash
mkdir -p docs/exec-plans/completed
mv docs/exec-plans/active/<filename>.md docs/exec-plans/completed/<filename>.md
```

Then report which plan file was moved so the reviewer can verify archival state.
````

**Step 4: Run test to verify it passes**

Run: `bash tests/skills/test_executing_plans_skill.sh`
Expected: PASS with workflow contract checks and exit code `0`

**Step 5: Commit**

```bash
git add tests/skills/test_executing_plans_skill.sh executing-plans/SKILL.md
git commit -m "feat: require executed-plan archival in executing-plans skill"
```
