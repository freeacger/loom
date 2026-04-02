#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TASK_NAME="status-view"
TASK_DATE="20260402"
TASK_SUFFIX="bb"
TASK_ID="${TASK_DATE}-${TASK_NAME}-${TASK_SUFFIX}"
TASK_DIR="$ROOT/docs/tasks/$TASK_ID"
PATCH_FILE="$(mktemp)"
PAYLOAD_FILE="$(mktemp)"
trap 'rm -rf "$TASK_DIR"; rm -f "$PATCH_FILE" "$PAYLOAD_FILE"' EXIT

rm -rf "$TASK_DIR"

python3 "$ROOT/skills/task-state-management/scripts/create_task.py" \
  --task-name "$TASK_NAME" \
  --date "$TASK_DATE" \
  --random-suffix "$TASK_SUFFIX" \
  --owner-id design-owner \
  --initial-goal "Refresh task status view" >/dev/null

python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
  --task-id "$TASK_ID" \
  --owner-id design-owner \
  --event-type decision_recorded \
  --phase design \
  --source design-orchestrator \
  --summary "Prepare state summary for status view" >/dev/null

printf '%s\n' '{
  "status": {
    "lifecycle_state": "in_progress",
    "validity_state": "valid",
    "owner": "design-orchestrator"
  },
  "decisions": [
    {
      "id": "dec-001",
      "summary": "Prepare state summary for status view"
    }
  ]
}' >"$PATCH_FILE"

EVENT_ID="$(python3 - "$TASK_DIR" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
with (task_dir / "events.jsonl").open("r", encoding="utf-8") as fh:
    rows = [json.loads(line) for line in fh if line.strip()]
print(rows[-1]["event_id"])
PY
)"

python3 "$ROOT/skills/task-state-management/scripts/update_state.py" \
  --task-id "$TASK_ID" \
  --owner-id design-owner \
  --state-kind design \
  --patch-file "$PATCH_FILE" \
  --expected-last-applied-event-id "$EVENT_ID" >/dev/null

REFRESH_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/refresh_status_view.py" \
    --task-id "$TASK_ID" \
    --owner-id design-owner
)"

REFRESH_TASK_ID="$(printf '%s' "$REFRESH_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["task_id"])')"
REFRESH_SUMMARY="$(printf '%s' "$REFRESH_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["summary"])')"
CHANGED_FILES="$(printf '%s' "$REFRESH_OUTPUT" | python3 -c 'import json,sys; print("\n".join(json.load(sys.stdin)["changed_files"]))')"

if [ "$REFRESH_TASK_ID" != "$TASK_ID" ]; then
  echo "unexpected refresh task_id: $REFRESH_TASK_ID"
  exit 1
fi

printf '%s' "$CHANGED_FILES" | grep -qx "$TASK_DIR/status.md"

if ! printf '%s' "$REFRESH_SUMMARY" | grep -q "Refreshed status view"; then
  echo "unexpected summary: $REFRESH_SUMMARY"
  exit 1
fi

HEALTHY_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/validate_state.py" \
    --task-id "$TASK_ID"
)"

HEALTHY_RESULT="$(printf '%s' "$HEALTHY_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["status"])')"

if [ "$HEALTHY_RESULT" != "ok" ]; then
  echo "unexpected healthy validation status: $HEALTHY_RESULT"
  exit 1
fi

python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
  --task-id "$TASK_ID" \
  --owner-id design-owner \
  --event-type decision_recorded \
  --phase design \
  --source design-orchestrator \
  --summary "Append a newer event without updating snapshot" >/dev/null

NEWER_EVENT_ID="$(python3 - "$TASK_DIR" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
with (task_dir / "events.jsonl").open("r", encoding="utf-8") as fh:
    rows = [json.loads(line) for line in fh if line.strip()]
print(rows[-1]["event_id"])
PY
)"

STALE_SNAPSHOT_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/validate_state.py" \
    --task-id "$TASK_ID"
)"

STALE_SNAPSHOT_RESULT="$(printf '%s' "$STALE_SNAPSHOT_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["status"])')"
STALE_SNAPSHOT_FINDINGS="$(printf '%s' "$STALE_SNAPSHOT_OUTPUT" | python3 -c 'import json,sys; print("\\n".join(json.load(sys.stdin)["result"]["findings"]))')"

if [ "$STALE_SNAPSHOT_RESULT" != "recovery_needed" ]; then
  echo "unexpected stale snapshot validation status: $STALE_SNAPSHOT_RESULT"
  exit 1
fi

if ! printf '%s' "$STALE_SNAPSHOT_FINDINGS" | grep -q "newer events"; then
  echo "missing recovery finding for newer events"
  exit 1
fi

printf '%s\n' '{}' >"$PAYLOAD_FILE"

PLANNING_EVENT_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
    --task-id "$TASK_ID" \
    --owner-id design-owner \
    --event-type decision_recorded \
    --phase planning \
    --source writing-plans \
    --summary "Planning event should not bind to design state" \
    --payload-file "$PAYLOAD_FILE"
)"

PLANNING_EVENT_ID="$(printf '%s' "$PLANNING_EVENT_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_id"])')"

set +e
IRRELEVANT_UPDATE_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/update_state.py" \
    --task-id "$TASK_ID" \
    --owner-id design-owner \
    --state-kind design \
    --patch-file "$PATCH_FILE" \
    --expected-last-applied-event-id "$PLANNING_EVENT_ID" 2>&1
)"
IRRELEVANT_UPDATE_EXIT=$?
set -e

if [ "$IRRELEVANT_UPDATE_EXIT" -eq 0 ]; then
  echo "expected update_state.py to reject irrelevant event binding"
  exit 1
fi

if ! printf '%s' "$IRRELEVANT_UPDATE_OUTPUT" | grep -q "relevant to the target state"; then
  echo "missing irrelevant event binding error"
  exit 1
fi

python3 "$ROOT/skills/task-state-management/scripts/update_state.py" \
  --task-id "$TASK_ID" \
  --owner-id design-owner \
  --state-kind design \
  --patch-file "$PATCH_FILE" \
  --expected-last-applied-event-id "$NEWER_EVENT_ID" >/dev/null

rm -f "$TASK_DIR/status.md"

WARNING_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/validate_state.py" \
    --task-id "$TASK_ID" \
    --state-kind design
)"

WARNING_RESULT="$(printf '%s' "$WARNING_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["status"])')"
WARNING_FINDINGS="$(printf '%s' "$WARNING_OUTPUT" | python3 -c 'import json,sys; print("\\n".join(json.load(sys.stdin)["result"]["findings"]))')"

if [ "$WARNING_RESULT" != "warning" ]; then
  echo "unexpected warning validation status: $WARNING_RESULT"
  exit 1
fi

if ! printf '%s' "$WARNING_FINDINGS" | grep -q "status.md"; then
  echo "missing warning about status.md"
  exit 1
fi

python3 - "$TASK_DIR" "$PLANNING_EVENT_ID" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
planning_event_id = sys.argv[2]
state_path = task_dir / "states" / "design-state.json"

with state_path.open("r", encoding="utf-8") as fh:
    state = json.load(fh)

state["meta"]["last_applied_event_id"] = planning_event_id

with state_path.open("w", encoding="utf-8") as fh:
    json.dump(state, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
PY

IRRELEVANT_VALIDATE_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/validate_state.py" \
    --task-id "$TASK_ID" \
    --state-kind design
)"

IRRELEVANT_VALIDATE_STATUS="$(printf '%s' "$IRRELEVANT_VALIDATE_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["status"])')"
IRRELEVANT_VALIDATE_FINDINGS="$(printf '%s' "$IRRELEVANT_VALIDATE_OUTPUT" | python3 -c 'import json,sys; print("\\n".join(json.load(sys.stdin)["result"]["findings"]))')"

if [ "$IRRELEVANT_VALIDATE_STATUS" != "recovery_needed" ]; then
  echo "unexpected irrelevant binding validation status: $IRRELEVANT_VALIDATE_STATUS"
  exit 1
fi

if ! printf '%s' "$IRRELEVANT_VALIDATE_FINDINGS" | grep -q "not relevant"; then
  echo "missing irrelevant last_applied_event_id finding"
  exit 1
fi

printf '%s\n' '{"broken":' >"$TASK_DIR/states/design-state.json"

CORRUPTED_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/validate_state.py" \
    --task-id "$TASK_ID"
)"
python3 - "$CORRUPTED_OUTPUT" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
status = payload["result"]["status"]
findings = "\n".join(payload["result"]["findings"])

assert status in {"invalid", "recovery_needed"}, status
assert "design-state.json" in findings, findings
PY

python3 - "$TASK_DIR" <<'PY'
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])

assert (task_dir / "events.jsonl").exists()
assert (task_dir / "states" / "plan-state.json").exists()
assert (task_dir / "states" / "execution-state.json").exists()
PY

echo "ok: refresh_status_view.py refreshed status view from states"
