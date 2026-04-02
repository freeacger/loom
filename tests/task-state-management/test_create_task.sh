#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TASK_NAME="state-loop"
TASK_DATE="20260402"
TASK_SUFFIX="zz"
TASK_ID="${TASK_DATE}-${TASK_NAME}-${TASK_SUFFIX}"
TASK_DIR="$ROOT/docs/tasks/$TASK_ID"

rm -rf "$TASK_DIR"
trap 'rm -rf "$TASK_DIR"' EXIT

OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/create_task.py" \
    --task-name "$TASK_NAME" \
    --date "$TASK_DATE" \
    --random-suffix "$TASK_SUFFIX" \
    --owner-id owner-a \
    --initial-goal "Create task state skeleton"
)"

TASK_ID_ACTUAL="$(printf '%s' "$OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["task_id"])')"
EXPECTED_PATHS="$(printf '%s' "$OUTPUT" | python3 -c 'import json,sys; data=json.load(sys.stdin); print("\n".join(data["result"]["state_files"]))')"
EVENT_ID="$(printf '%s' "$OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_id"])')"
EVENT_SEQ="$(printf '%s' "$OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_seq"])')"

if [ "$TASK_ID_ACTUAL" != "$TASK_ID" ]; then
  echo "unexpected task_id: $TASK_ID_ACTUAL"
  exit 1
fi

case "$TASK_ID_ACTUAL" in
  20260402-state-loop-zz) ;;
  *)
    echo "task_id format mismatch: $TASK_ID_ACTUAL"
    exit 1
    ;;
esac

test -d "$TASK_DIR"
test -f "$TASK_DIR/status.md"
test -f "$TASK_DIR/events.jsonl"
test -f "$TASK_DIR/ownership.json"
test -f "$TASK_DIR/states/design-state.json"
test -f "$TASK_DIR/states/plan-state.json"
test -f "$TASK_DIR/states/execution-state.json"

printf '%s' "$EXPECTED_PATHS" | grep -qx "$TASK_DIR/states/design-state.json"
printf '%s' "$EXPECTED_PATHS" | grep -qx "$TASK_DIR/states/plan-state.json"
printf '%s' "$EXPECTED_PATHS" | grep -qx "$TASK_DIR/states/execution-state.json"

python3 - "$TASK_DIR" "$EVENT_ID" "$EVENT_SEQ" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
event_id = sys.argv[2]
event_seq = int(sys.argv[3])

with (task_dir / "events.jsonl").open("r", encoding="utf-8") as fh:
    lines = [line.strip() for line in fh if line.strip()]

assert len(lines) == 2, lines
event = json.loads(lines[0])
ownership_event = json.loads(lines[1])
assert event["event_id"] == event_id
assert event["event_seq"] == event_seq
assert event["type"] == "task_created"
assert event["task_id"] == task_dir.name
assert event["summary"] == "Create task state skeleton"
assert ownership_event["event_seq"] == 2
assert ownership_event["type"] == "ownership_acquired"
assert ownership_event["owner_id"] == "owner-a"

for rel in [
    "status.md",
    "ownership.json",
    "states/design-state.json",
    "states/plan-state.json",
    "states/execution-state.json",
]:
    assert (task_dir / rel).exists(), rel
PY

echo "ok: create_task.py created task scaffolding"
