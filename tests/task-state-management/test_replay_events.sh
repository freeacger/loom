#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TASK_NAME="replay-flow"
TASK_DATE="20260402"
TASK_SUFFIX="rp"
TASK_ID="${TASK_DATE}-${TASK_NAME}-${TASK_SUFFIX}"
TASK_DIR="$ROOT/docs/tasks/$TASK_ID"
OWNERSHIP_TASK_NAME="replay-ownership"
OWNERSHIP_TASK_SUFFIX="ro"
OWNERSHIP_TASK_ID="${TASK_DATE}-${OWNERSHIP_TASK_NAME}-${OWNERSHIP_TASK_SUFFIX}"
OWNERSHIP_TASK_DIR="$ROOT/docs/tasks/$OWNERSHIP_TASK_ID"
PAYLOAD_FILE="$(mktemp)"
trap 'rm -rf "$TASK_DIR" "$OWNERSHIP_TASK_DIR"; rm -f "$PAYLOAD_FILE"' EXIT

rm -rf "$TASK_DIR" "$OWNERSHIP_TASK_DIR"

python3 "$ROOT/skills/task-state-management/scripts/create_task.py" \
  --task-name "$TASK_NAME" \
  --date "$TASK_DATE" \
  --random-suffix "$TASK_SUFFIX" \
  --owner-id replay-owner \
  --initial-goal "Exercise event replay" >/dev/null

printf '%s\n' '{
  "blocking_issue": {
    "id": "blk-replay-001",
    "reason": "Replay blocker into plan state",
    "severity": "high",
    "source": "external",
    "created_at": "2026-04-02T10:00:00+08:00",
    "cleared": false
  },
  "state_kind": "plan"
}' >"$PAYLOAD_FILE"

python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
  --task-id "$TASK_ID" \
  --owner-id replay-owner \
  --event-type blocking_issue_added \
  --phase planning \
  --source task-state-management \
  --summary "Append replayable blocker event without snapshot update" \
  --payload-file "$PAYLOAD_FILE" >/dev/null

VALIDATE_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/validate_state.py" \
    --task-id "$TASK_ID" \
    --state-kind plan
)"

VALIDATE_STATUS="$(printf '%s' "$VALIDATE_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["status"])')"

if [ "$VALIDATE_STATUS" != "recovery_needed" ]; then
  echo "expected recovery_needed before replay"
  exit 1
fi

REPLAY_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/replay_events.py" \
    --task-id "$TASK_ID" \
    --owner-id replay-owner \
    --state-kind plan
)"

python3 - "$TASK_DIR" "$REPLAY_OUTPUT" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
payload = json.loads(sys.argv[2])

with (task_dir / "states" / "plan-state.json").open("r", encoding="utf-8") as fh:
    plan_state = json.load(fh)

assert payload["result"]["replayed_states"][0]["state_kind"] == "plan"
assert payload["result"]["replayed_states"][0]["replayed_event_count"] == 1
assert plan_state["status"]["lifecycle_state"] == "blocked"
assert len(plan_state["status"]["blocking_issues"]) == 1
assert plan_state["status"]["blocking_issues"][0]["id"] == "blk-replay-001"
assert plan_state["meta"]["state_version"] == 2
PY

VALIDATE_AFTER_REPLAY="$(
  python3 "$ROOT/skills/task-state-management/scripts/validate_state.py" \
    --task-id "$TASK_ID" \
    --state-kind plan
)"

VALIDATE_AFTER_REPLAY_STATUS="$(printf '%s' "$VALIDATE_AFTER_REPLAY" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["status"])')"

if [ "$VALIDATE_AFTER_REPLAY_STATUS" != "ok" ]; then
  echo "expected ok after replay, got $VALIDATE_AFTER_REPLAY_STATUS"
  exit 1
fi

REPLAY_OUTPUT_2="$(
  python3 "$ROOT/skills/task-state-management/scripts/replay_events.py" \
    --task-id "$TASK_ID" \
    --owner-id replay-owner \
    --state-kind plan
)"

python3 - "$TASK_DIR" "$REPLAY_OUTPUT_2" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
payload = json.loads(sys.argv[2])

with (task_dir / "states" / "plan-state.json").open("r", encoding="utf-8") as fh:
    plan_state = json.load(fh)

assert payload["result"]["replayed_states"][0]["replayed_event_count"] == 0
assert plan_state["meta"]["state_version"] == 2
PY

echo "ok: replay_events.py recovered state snapshots idempotently"

python3 "$ROOT/skills/task-state-management/scripts/create_task.py" \
  --task-name "$OWNERSHIP_TASK_NAME" \
  --date "$TASK_DATE" \
  --random-suffix "$OWNERSHIP_TASK_SUFFIX" \
  --owner-id owner-a \
  --initial-goal "Exercise ownership replay" >/dev/null

python3 "$ROOT/skills/task-state-management/scripts/acquire_ownership.py" \
  --task-id "$OWNERSHIP_TASK_ID" \
  --owner-id owner-b \
  --force >/dev/null

python3 "$ROOT/skills/task-state-management/scripts/transfer_ownership.py" \
  --task-id "$OWNERSHIP_TASK_ID" \
  --from-owner-id owner-b \
  --to-owner-id owner-c \
  --reason "replay-handoff" >/dev/null

printf '%s\n' '{
  "task_id": "'"$OWNERSHIP_TASK_ID"'",
  "owner_id": "owner-a",
  "acquired_at": "2026-04-02T09:00:00+08:00",
  "lease_expires_at": "2026-04-02T09:15:00+08:00"
}' >"$OWNERSHIP_TASK_DIR/ownership.json"

OWNERSHIP_REPLAY_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/replay_events.py" \
    --task-id "$OWNERSHIP_TASK_ID" \
    --owner-id owner-c \
    --include-ownership
)"

python3 - "$OWNERSHIP_TASK_DIR" "$OWNERSHIP_REPLAY_OUTPUT" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
payload = json.loads(sys.argv[2])

with (task_dir / "ownership.json").open("r", encoding="utf-8") as fh:
    ownership = json.load(fh)

ownership_result = payload["result"]["ownership"]
assert ownership_result["replayed_event_count"] == 3
assert ownership_result["owner_id"] == "owner-c"
assert ownership["owner_id"] == "owner-c"
assert ownership["transfer_reason"] == "replay-handoff"
PY

OWNERSHIP_REPLAY_OUTPUT_2="$(
  python3 "$ROOT/skills/task-state-management/scripts/replay_events.py" \
    --task-id "$OWNERSHIP_TASK_ID" \
    --owner-id owner-c \
    --include-ownership
)"

python3 - "$OWNERSHIP_TASK_DIR" "$OWNERSHIP_REPLAY_OUTPUT_2" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
payload = json.loads(sys.argv[2])

with (task_dir / "ownership.json").open("r", encoding="utf-8") as fh:
    ownership = json.load(fh)

ownership_result = payload["result"]["ownership"]
assert ownership_result["replayed_event_count"] == 0
assert ownership["owner_id"] == "owner-c"
PY

echo "ok: replay_events.py recovered ownership snapshots idempotently"
