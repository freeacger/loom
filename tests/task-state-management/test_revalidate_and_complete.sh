#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TASK_DATE="20260402"

TASK_A_ID="${TASK_DATE}-revalidate-flow-rv"
TASK_B_ID="${TASK_DATE}-complete-invalid-iv"
TASK_C_ID="${TASK_DATE}-complete-blocked-bk"
TASK_A_DIR="$ROOT/docs/tasks/$TASK_A_ID"
TASK_B_DIR="$ROOT/docs/tasks/$TASK_B_ID"
TASK_C_DIR="$ROOT/docs/tasks/$TASK_C_ID"
TASK_D_ID="${TASK_DATE}-revalidate-plan-rg"
TASK_E_ID="${TASK_DATE}-revalidate-mismatch-mm"
TASK_D_DIR="$ROOT/docs/tasks/$TASK_D_ID"
TASK_E_DIR="$ROOT/docs/tasks/$TASK_E_ID"

PATCH_A="$(mktemp)"
PATCH_B="$(mktemp)"
PATCH_D="$(mktemp)"
PATCH_E="$(mktemp)"
trap 'rm -rf "$TASK_A_DIR" "$TASK_B_DIR" "$TASK_C_DIR" "$TASK_D_DIR" "$TASK_E_DIR"; rm -f "$PATCH_A" "$PATCH_B" "$PATCH_D" "$PATCH_E"' EXIT

rm -rf "$TASK_A_DIR" "$TASK_B_DIR" "$TASK_C_DIR" "$TASK_D_DIR" "$TASK_E_DIR"

python3 "$ROOT/skills/task-state-management/scripts/create_task.py" \
  --task-name revalidate-flow \
  --date "$TASK_DATE" \
  --random-suffix rv \
  --owner-id execution-owner \
  --initial-goal "Exercise revalidation and successful completion" >/dev/null

python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
  --task-id "$TASK_A_ID" \
  --owner-id execution-owner \
  --event-type state_marked_stale \
  --phase execution \
  --source system \
  --summary "Execution state became stale" >/dev/null

TASK_A_STALE_EVENT_ID="$(python3 - "$TASK_A_DIR" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
with (task_dir / "events.jsonl").open("r", encoding="utf-8") as fh:
    rows = [json.loads(line) for line in fh if line.strip()]
print(rows[-1]["event_id"])
PY
)"

printf '%s\n' '{
  "status": {
    "lifecycle_state": "in_progress",
    "validity_state": "stale",
    "owner": "executing-plans"
  }
}' >"$PATCH_A"

python3 "$ROOT/skills/task-state-management/scripts/update_state.py" \
  --task-id "$TASK_A_ID" \
  --owner-id execution-owner \
  --state-kind execution \
  --patch-file "$PATCH_A" \
  --expected-last-applied-event-id "$TASK_A_STALE_EVENT_ID" >/dev/null

REVALIDATE_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/revalidate_state.py" \
    --task-id "$TASK_A_ID" \
    --owner-id execution-owner \
    --state-kind execution \
    --against-source-version 1 \
    --reason "Execution state revalidated after review"
)"

REVALIDATE_EVENT_ID="$(printf '%s' "$REVALIDATE_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_id"])')"
REVALIDATE_EVENT_SEQ="$(printf '%s' "$REVALIDATE_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_seq"])')"
REVALIDATE_STATE_VERSION="$(printf '%s' "$REVALIDATE_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["state_version"])')"
REVALIDATE_VALIDITY="$(printf '%s' "$REVALIDATE_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["validity_state"])')"

if [ "$REVALIDATE_EVENT_SEQ" != "4" ]; then
  echo "unexpected revalidate event_seq: $REVALIDATE_EVENT_SEQ"
  exit 1
fi

if [ "$REVALIDATE_STATE_VERSION" != "3" ]; then
  echo "unexpected state_version after revalidate: $REVALIDATE_STATE_VERSION"
  exit 1
fi

if [ "$REVALIDATE_VALIDITY" != "valid" ]; then
  echo "unexpected validity after revalidate: $REVALIDATE_VALIDITY"
  exit 1
fi

python3 - "$TASK_A_DIR" "$REVALIDATE_EVENT_ID" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
event_id = sys.argv[2]

with (task_dir / "states" / "execution-state.json").open("r", encoding="utf-8") as fh:
    execution_state = json.load(fh)

with (task_dir / "events.jsonl").open("r", encoding="utf-8") as fh:
    rows = [json.loads(line) for line in fh if line.strip()]

assert rows[-1]["type"] == "state_revalidated"
assert rows[-1]["event_id"] == event_id
assert execution_state["status"]["validity_state"] == "valid"
assert execution_state["meta"]["last_applied_event_id"] == event_id
assert execution_state["meta"]["state_version"] == 3
PY

COMPLETE_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/complete_task.py" \
    --task-id "$TASK_A_ID" \
    --owner-id execution-owner \
    --completion-summary "Execution finished successfully"
)"

COMPLETE_EVENT_ID="$(printf '%s' "$COMPLETE_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_id"])')"
COMPLETE_EVENT_SEQ="$(printf '%s' "$COMPLETE_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_seq"])')"
COMPLETE_STATE_VERSION="$(printf '%s' "$COMPLETE_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["state_version"])')"
COMPLETE_LIFECYCLE="$(printf '%s' "$COMPLETE_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["lifecycle_state"])')"

if [ "$COMPLETE_EVENT_SEQ" != "5" ]; then
  echo "unexpected complete event_seq: $COMPLETE_EVENT_SEQ"
  exit 1
fi

if [ "$COMPLETE_STATE_VERSION" != "4" ]; then
  echo "unexpected state_version after complete: $COMPLETE_STATE_VERSION"
  exit 1
fi

if [ "$COMPLETE_LIFECYCLE" != "completed" ]; then
  echo "unexpected lifecycle after complete: $COMPLETE_LIFECYCLE"
  exit 1
fi

python3 - "$TASK_A_DIR" "$COMPLETE_EVENT_ID" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
event_id = sys.argv[2]

with (task_dir / "states" / "execution-state.json").open("r", encoding="utf-8") as fh:
    execution_state = json.load(fh)

with (task_dir / "events.jsonl").open("r", encoding="utf-8") as fh:
    rows = [json.loads(line) for line in fh if line.strip()]

assert rows[-1]["type"] == "task_completed"
assert rows[-1]["event_id"] == event_id
assert execution_state["status"]["lifecycle_state"] == "completed"
assert execution_state["meta"]["last_applied_event_id"] == event_id
assert execution_state["meta"]["state_version"] == 4
PY

python3 "$ROOT/skills/task-state-management/scripts/create_task.py" \
  --task-name complete-invalid \
  --date "$TASK_DATE" \
  --random-suffix iv \
  --owner-id invalid-owner \
  --initial-goal "Exercise invalid completion" >/dev/null

python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
  --task-id "$TASK_B_ID" \
  --owner-id invalid-owner \
  --event-type state_marked_stale \
  --phase execution \
  --source system \
  --summary "Execution state became stale" >/dev/null

TASK_B_STALE_EVENT_ID="$(python3 - "$TASK_B_DIR" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
with (task_dir / "events.jsonl").open("r", encoding="utf-8") as fh:
    rows = [json.loads(line) for line in fh if line.strip()]
print(rows[-1]["event_id"])
PY
)"

printf '%s\n' '{
  "status": {
    "lifecycle_state": "in_progress",
    "validity_state": "stale",
    "owner": "executing-plans"
  }
}' >"$PATCH_B"

python3 "$ROOT/skills/task-state-management/scripts/update_state.py" \
  --task-id "$TASK_B_ID" \
  --owner-id invalid-owner \
  --state-kind execution \
  --patch-file "$PATCH_B" \
  --expected-last-applied-event-id "$TASK_B_STALE_EVENT_ID" >/dev/null

set +e
INVALID_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/complete_task.py" \
    --task-id "$TASK_B_ID" \
    --owner-id invalid-owner \
    --completion-summary "Should fail because state is stale" 2>&1
)"
INVALID_EXIT=$?
set -e

if [ "$INVALID_EXIT" -eq 0 ]; then
  echo "expected complete_task.py to fail for stale execution state"
  exit 1
fi

if ! printf '%s' "$INVALID_OUTPUT" | grep -q "unexpected validity_state"; then
  echo "missing stale validity failure message"
  exit 1
fi

python3 "$ROOT/skills/task-state-management/scripts/create_task.py" \
  --task-name complete-blocked \
  --date "$TASK_DATE" \
  --random-suffix bk \
  --owner-id blocked-owner \
  --initial-goal "Exercise blocked completion" >/dev/null

python3 "$ROOT/skills/task-state-management/scripts/add_blocker.py" \
  --task-id "$TASK_C_ID" \
  --owner-id blocked-owner \
  --state-kind execution \
  --reason "Waiting for deployment approval" \
  --severity medium \
  --source external >/dev/null

set +e
BLOCKED_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/complete_task.py" \
    --task-id "$TASK_C_ID" \
    --owner-id blocked-owner \
    --completion-summary "Should fail because blockers remain" 2>&1
)"
BLOCKED_EXIT=$?
set -e

if [ "$BLOCKED_EXIT" -eq 0 ]; then
  echo "expected complete_task.py to fail when blockers remain"
  exit 1
fi

if ! printf '%s' "$BLOCKED_OUTPUT" | grep -q "blocking_issues must be empty"; then
  echo "missing blocker failure message"
  exit 1
fi

python3 "$ROOT/skills/task-state-management/scripts/create_task.py" \
  --task-name revalidate-plan \
  --date "$TASK_DATE" \
  --random-suffix rg \
  --owner-id plan-owner \
  --initial-goal "Exercise plan revalidation regression guard" >/dev/null

python3 "$ROOT/skills/task-state-management/scripts/handoff_state.py" \
  --task-id "$TASK_D_ID" \
  --owner-id plan-owner \
  --from-phase design \
  --to-phase planning >/dev/null

python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
  --task-id "$TASK_D_ID" \
  --owner-id plan-owner \
  --event-type state_marked_stale \
  --phase planning \
  --source system \
  --summary "Plan state became stale" >/dev/null

printf '%s\n' '{
  "status": {
    "lifecycle_state": "in_progress",
    "validity_state": "stale",
    "owner": "writing-plans"
  },
  "source_design_version": 2
}' >"$PATCH_D"

TASK_D_STALE_EVENT_ID="$(python3 - "$TASK_D_DIR" <<'PY'
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
  --task-id "$TASK_D_ID" \
  --owner-id plan-owner \
  --state-kind plan \
  --patch-file "$PATCH_D" \
  --expected-last-applied-event-id "$TASK_D_STALE_EVENT_ID" >/dev/null

set +e
REGRESSION_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/revalidate_state.py" \
    --task-id "$TASK_D_ID" \
    --owner-id plan-owner \
    --state-kind plan \
    --against-source-version 1 \
    --reason "Should fail because version regresses" 2>&1
)"
REGRESSION_EXIT=$?
set -e

if [ "$REGRESSION_EXIT" -eq 0 ]; then
  echo "expected revalidate_state.py to reject older source version"
  exit 1
fi

if ! printf '%s' "$REGRESSION_OUTPUT" | grep -q "must not be older"; then
  echo "missing source version regression error"
  exit 1
fi

python3 "$ROOT/skills/task-state-management/scripts/create_task.py" \
  --task-name revalidate-mismatch \
  --date "$TASK_DATE" \
  --random-suffix mm \
  --owner-id mismatch-owner \
  --initial-goal "Exercise upstream version mismatch guard" >/dev/null

python3 "$ROOT/skills/task-state-management/scripts/handoff_state.py" \
  --task-id "$TASK_E_ID" \
  --owner-id mismatch-owner \
  --from-phase design \
  --to-phase planning >/dev/null

python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
  --task-id "$TASK_E_ID" \
  --owner-id mismatch-owner \
  --event-type state_marked_stale \
  --phase planning \
  --source system \
  --summary "Plan state became stale" >/dev/null

printf '%s\n' '{
  "status": {
    "lifecycle_state": "in_progress",
    "validity_state": "stale",
    "owner": "writing-plans"
  }
}' >"$PATCH_E"

TASK_E_STALE_EVENT_ID="$(python3 - "$TASK_E_DIR" <<'PY'
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
  --task-id "$TASK_E_ID" \
  --owner-id mismatch-owner \
  --state-kind plan \
  --patch-file "$PATCH_E" \
  --expected-last-applied-event-id "$TASK_E_STALE_EVENT_ID" >/dev/null

set +e
MISMATCH_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/revalidate_state.py" \
    --task-id "$TASK_E_ID" \
    --owner-id mismatch-owner \
    --state-kind plan \
    --against-source-version 2 \
    --reason "Should fail because upstream version no longer matches" 2>&1
)"
MISMATCH_EXIT=$?
set -e

if [ "$MISMATCH_EXIT" -eq 0 ]; then
  echo "expected revalidate_state.py to reject mismatched upstream version"
  exit 1
fi

if ! printf '%s' "$MISMATCH_OUTPUT" | grep -q "must match actual upstream"; then
  echo "missing upstream mismatch error"
  exit 1
fi

echo "ok: revalidate_state.py and complete_task.py enforce recovery and completion rules"
