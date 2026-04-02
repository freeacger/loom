#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TASK_NAME="event-state"
TASK_DATE="20260402"
TASK_SUFFIX="aa"
TASK_ID="${TASK_DATE}-${TASK_NAME}-${TASK_SUFFIX}"
TASK_DIR="$ROOT/docs/tasks/$TASK_ID"
PATCH_FILE="$(mktemp)"
PAYLOAD_FILE="$(mktemp)"
trap 'rm -rf "$TASK_DIR"; rm -f "$PATCH_FILE" "$PAYLOAD_FILE"' EXIT

rm -rf "$TASK_DIR"

TASK_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/create_task.py" \
    --task-name "$TASK_NAME" \
    --date "$TASK_DATE" \
    --random-suffix "$TASK_SUFFIX" \
    --owner-id design-owner \
    --initial-goal "Exercise append_event and update_state"
)"

printf '%s\n' '{
  "decisions": [
    {
      "id": "dec-001",
      "summary": "Record first design decision"
    }
  ],
  "status": {
    "owner": "design-orchestrator"
  }
}' >"$PATCH_FILE"

EVENT_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
    --task-id "$TASK_ID" \
    --owner-id design-owner \
    --event-type decision_recorded \
    --phase design \
    --source design-orchestrator \
    --summary "Record first design decision"
)"

EVENT_ID="$(printf '%s' "$EVENT_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_id"])')"
EVENT_SEQ="$(printf '%s' "$EVENT_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_seq"])')"

STATE_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/update_state.py" \
    --task-id "$TASK_ID" \
    --owner-id design-owner \
    --state-kind design \
    --patch-file "$PATCH_FILE" \
    --expected-last-applied-event-id "$EVENT_ID"
)"

STATE_VERSION="$(printf '%s' "$STATE_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["state_version"])')"
LAST_APPLIED_EVENT_ID="$(printf '%s' "$STATE_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["last_applied_event_id"])')"

if [ "$EVENT_SEQ" != "3" ]; then
  echo "unexpected event_seq: $EVENT_SEQ"
  exit 1
fi

if [ "$LAST_APPLIED_EVENT_ID" != "$EVENT_ID" ]; then
  echo "unexpected last_applied_event_id: $LAST_APPLIED_EVENT_ID"
  exit 1
fi

if [ "$STATE_VERSION" != "2" ]; then
  echo "unexpected state_version: $STATE_VERSION"
  exit 1
fi

python3 - "$TASK_DIR" "$EVENT_ID" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
event_id = sys.argv[2]

with (task_dir / "events.jsonl").open("r", encoding="utf-8") as fh:
    rows = [json.loads(line) for line in fh if line.strip()]

assert len(rows) == 3, rows
assert rows[0]["event_seq"] == 1
assert rows[1]["event_seq"] == 2
assert rows[1]["type"] == "ownership_acquired"
assert rows[2]["event_seq"] == 3
assert rows[2]["event_id"] == event_id
assert rows[2]["type"] == "decision_recorded"

with (task_dir / "states" / "design-state.json").open("r", encoding="utf-8") as fh:
    state = json.load(fh)

assert state["meta"]["last_applied_event_id"] == event_id
assert state["meta"]["state_version"] == 2
assert state["status"]["owner"] == "design-orchestrator"
assert state["decisions"][0]["id"] == "dec-001"
PY

EVENT_OUTPUT_2="$(
  python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
    --task-id "$TASK_ID" \
    --owner-id design-owner \
    --event-type decision_recorded \
    --phase design \
    --source design-orchestrator \
    --summary "Record second design decision"
)"

EVENT_ID_2="$(printf '%s' "$EVENT_OUTPUT_2" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_id"])')"

printf '%s\n' '{
  "decisions": [
    {
      "id": "dec-001",
      "summary": "Record first design decision"
    },
    {
      "id": "dec-002",
      "summary": "Record second design decision"
    }
  ]
}' >"$PATCH_FILE"

python3 "$ROOT/skills/task-state-management/scripts/update_state.py" \
  --task-id "$TASK_ID" \
  --owner-id design-owner \
  --state-kind design \
  --patch-file "$PATCH_FILE" \
  --expected-last-applied-event-id "$EVENT_ID_2" >/dev/null

set +e
ROLLBACK_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/update_state.py" \
    --task-id "$TASK_ID" \
    --owner-id design-owner \
    --state-kind design \
    --patch-file "$PATCH_FILE" \
    --expected-last-applied-event-id "$EVENT_ID" 2>&1
)"
ROLLBACK_EXIT=$?
set -e

if [ "$ROLLBACK_EXIT" -eq 0 ]; then
  echo "expected update_state.py to reject older last_applied_event_id"
  exit 1
fi

if ! printf '%s' "$ROLLBACK_OUTPUT" | grep -q "must point to a newer event"; then
  echo "missing rollback protection error"
  exit 1
fi

printf '%s\n' '{
  "event_id": "forged-event-id",
  "task_id": "forged-task-id"
}' >"$PAYLOAD_FILE"

set +e
RESERVED_FIELD_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
    --task-id "$TASK_ID" \
    --owner-id design-owner \
    --event-type decision_recorded \
    --phase design \
    --source design-orchestrator \
    --summary "Should fail for reserved payload fields" \
    --payload-file "$PAYLOAD_FILE" 2>&1
)"
RESERVED_FIELD_EXIT=$?
set -e

if [ "$RESERVED_FIELD_EXIT" -eq 0 ]; then
  echo "expected append_event.py to reject reserved payload fields"
  exit 1
fi

if ! printf '%s' "$RESERVED_FIELD_OUTPUT" | grep -q "reserved event fields"; then
  echo "missing reserved field protection error"
  exit 1
fi

echo "ok: append_event.py and update_state.py updated task state"
