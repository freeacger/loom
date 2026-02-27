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
