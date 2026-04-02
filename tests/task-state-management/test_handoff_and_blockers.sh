#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TASK_NAME="handoff-flow"
TASK_DATE="20260402"
TASK_SUFFIX="hc"
TASK_ID="${TASK_DATE}-${TASK_NAME}-${TASK_SUFFIX}"
TASK_DIR="$ROOT/docs/tasks/$TASK_ID"
PATCH_FILE="$(mktemp)"
trap 'rm -rf "$TASK_DIR"; rm -f "$PATCH_FILE"' EXIT

rm -rf "$TASK_DIR"

python3 "$ROOT/skills/task-state-management/scripts/create_task.py" \
  --task-name "$TASK_NAME" \
  --date "$TASK_DATE" \
  --random-suffix "$TASK_SUFFIX" \
  --owner-id design-owner \
  --initial-goal "Exercise handoff state flow" >/dev/null

python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
  --task-id "$TASK_ID" \
  --owner-id design-owner \
  --event-type decision_recorded \
  --phase design \
  --source design-orchestrator \
  --summary "Freeze design before handoff" >/dev/null

printf '%s\n' '{
  "decisions": [
    {
      "id": "dec-handoff-001",
      "summary": "Freeze design before handoff"
    }
  ],
  "status": {
    "owner": "design-orchestrator"
  }
}' >"$PATCH_FILE"

SOURCE_EVENT_ID="$(python3 - "$TASK_DIR" <<'PY'
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
  --expected-last-applied-event-id "$SOURCE_EVENT_ID" >/dev/null

HANDOFF_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/handoff_state.py" \
    --task-id "$TASK_ID" \
    --owner-id design-owner \
    --from-phase design \
    --to-phase planning
)"

HANDOFF_EVENT_ID="$(printf '%s' "$HANDOFF_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_id"])')"
HANDOFF_EVENT_SEQ="$(printf '%s' "$HANDOFF_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_seq"])')"
STATE_VERSION="$(printf '%s' "$HANDOFF_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["state_version"])')"

if [ "$HANDOFF_EVENT_SEQ" != "4" ]; then
  echo "unexpected handoff event_seq: $HANDOFF_EVENT_SEQ"
  exit 1
fi

if [ "$STATE_VERSION" != "2" ]; then
  echo "unexpected plan state version after handoff: $STATE_VERSION"
  exit 1
fi

python3 - "$TASK_DIR" "$SOURCE_EVENT_ID" "$HANDOFF_EVENT_ID" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
source_event_id = sys.argv[2]
handoff_event_id = sys.argv[3]

with (task_dir / "states" / "design-state.json").open("r", encoding="utf-8") as fh:
    design_state = json.load(fh)

with (task_dir / "states" / "plan-state.json").open("r", encoding="utf-8") as fh:
    plan_state = json.load(fh)

with (task_dir / "events.jsonl").open("r", encoding="utf-8") as fh:
    rows = [json.loads(line) for line in fh if line.strip()]

assert len(rows) == 4, rows
assert rows[-1]["type"] == "handoff_completed"
assert rows[-1]["event_id"] == handoff_event_id
assert rows[-1]["handoff_kind"] == "design_to_plan"

assert plan_state["source_design_ref"] == str(task_dir / "states" / "design-state.json")
assert plan_state["source_design_version"] == design_state["meta"]["state_version"]
assert plan_state["source_design_event_id"] == source_event_id
assert plan_state["meta"]["last_applied_event_id"] == handoff_event_id
assert plan_state["meta"]["state_version"] == 2
PY

BLOCKER_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/add_blocker.py" \
    --task-id "$TASK_ID" \
    --owner-id design-owner \
    --state-kind plan \
    --reason "Waiting for external sign-off" \
    --severity high \
    --source external
)"

BLOCKER_ID="$(printf '%s' "$BLOCKER_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["blocking_issue_id"])')"
BLOCKER_EVENT_ID="$(printf '%s' "$BLOCKER_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_id"])')"
BLOCKER_EVENT_SEQ="$(printf '%s' "$BLOCKER_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_seq"])')"
BLOCKER_STATE_VERSION="$(printf '%s' "$BLOCKER_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["state_version"])')"

if [ "$BLOCKER_EVENT_SEQ" != "5" ]; then
  echo "unexpected blocker event_seq: $BLOCKER_EVENT_SEQ"
  exit 1
fi

if [ "$BLOCKER_STATE_VERSION" != "3" ]; then
  echo "unexpected plan state version after add_blocker: $BLOCKER_STATE_VERSION"
  exit 1
fi

python3 - "$TASK_DIR" "$BLOCKER_ID" "$BLOCKER_EVENT_ID" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
blocking_issue_id = sys.argv[2]
event_id = sys.argv[3]

with (task_dir / "states" / "plan-state.json").open("r", encoding="utf-8") as fh:
    plan_state = json.load(fh)

with (task_dir / "events.jsonl").open("r", encoding="utf-8") as fh:
    rows = [json.loads(line) for line in fh if line.strip()]

assert rows[-1]["type"] == "blocking_issue_added"
assert rows[-1]["event_id"] == event_id
assert plan_state["status"]["lifecycle_state"] == "blocked"
assert plan_state["meta"]["last_applied_event_id"] == event_id
assert plan_state["meta"]["state_version"] == 3
assert len(plan_state["status"]["blocking_issues"]) == 1
assert plan_state["status"]["blocking_issues"][0]["id"] == blocking_issue_id
assert plan_state["status"]["blocking_issues"][0]["severity"] == "high"
PY

CLEAR_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/clear_blocker.py" \
    --task-id "$TASK_ID" \
    --owner-id design-owner \
    --state-kind plan \
    --blocking-issue-id "$BLOCKER_ID"
)"

CLEAR_EVENT_ID="$(printf '%s' "$CLEAR_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_id"])')"
CLEAR_EVENT_SEQ="$(printf '%s' "$CLEAR_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_seq"])')"
CLEAR_STATE_VERSION="$(printf '%s' "$CLEAR_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["state_version"])')"
CLEAR_LIFECYCLE="$(printf '%s' "$CLEAR_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["lifecycle_state"])')"

if [ "$CLEAR_EVENT_SEQ" != "6" ]; then
  echo "unexpected clear blocker event_seq: $CLEAR_EVENT_SEQ"
  exit 1
fi

if [ "$CLEAR_STATE_VERSION" != "4" ]; then
  echo "unexpected plan state version after clear_blocker: $CLEAR_STATE_VERSION"
  exit 1
fi

if [ "$CLEAR_LIFECYCLE" != "in_progress" ]; then
  echo "unexpected lifecycle after clear_blocker: $CLEAR_LIFECYCLE"
  exit 1
fi

python3 - "$TASK_DIR" "$CLEAR_EVENT_ID" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
event_id = sys.argv[2]

with (task_dir / "states" / "plan-state.json").open("r", encoding="utf-8") as fh:
    plan_state = json.load(fh)

with (task_dir / "events.jsonl").open("r", encoding="utf-8") as fh:
    rows = [json.loads(line) for line in fh if line.strip()]

assert rows[-1]["type"] == "blocking_issue_cleared"
assert rows[-1]["event_id"] == event_id
assert plan_state["status"]["lifecycle_state"] == "in_progress"
assert plan_state["meta"]["last_applied_event_id"] == event_id
assert plan_state["meta"]["state_version"] == 4
assert plan_state["status"]["blocking_issues"] == []
PY

echo "ok: handoff_state.py and blocker scripts maintained downstream state"
