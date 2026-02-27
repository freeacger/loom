#!/usr/bin/env bash
set -euo pipefail

SKILL_FILE="executing-plans/SKILL.md"
NOTES_FILE="docs/skills/executing-plans-porting.md"

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
assert_contains "**REQUIRED SUB-SKILL:** Use loom:finishing-a-development-branch" "$SKILL_FILE"
assert_contains "**loom:using-git-worktrees**" "$SKILL_FILE"
assert_contains "**loom:writing-plans**" "$SKILL_FILE"
assert_contains "**loom:finishing-a-development-branch**" "$SKILL_FILE"

if [[ ! -f "$NOTES_FILE" ]]; then
  echo "FAIL: missing $NOTES_FILE" >&2
  exit 1
fi

assert_contains "Source:" "$NOTES_FILE"
assert_contains "https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md" "$NOTES_FILE"
assert_contains "Local Changes:" "$NOTES_FILE"
assert_contains "Replaced superpowers namespace with loom namespace" "$NOTES_FILE"

echo "PASS: full executing-plans workflow contract checks passed"
