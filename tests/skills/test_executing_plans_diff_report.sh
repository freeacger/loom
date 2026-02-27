#!/usr/bin/env bash
set -euo pipefail

REPORT_FILE="docs/skills/executing-plans-diff-report.md"

assert_contains() {
  local pattern="$1"
  local file="$2"
  if ! rg -q --fixed-strings -- "$pattern" "$file"; then
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
