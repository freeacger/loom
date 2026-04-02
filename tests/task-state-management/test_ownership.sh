#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TASK_NAME="ownership-flow"
TASK_DATE="20260402"
TASK_SUFFIX="ow"
TASK_ID="${TASK_DATE}-${TASK_NAME}-${TASK_SUFFIX}"
TASK_DIR="$ROOT/docs/tasks/$TASK_ID"
trap 'rm -rf "$TASK_DIR"' EXIT

rm -rf "$TASK_DIR"

python3 "$ROOT/skills/task-state-management/scripts/create_task.py" \
  --task-name "$TASK_NAME" \
  --date "$TASK_DATE" \
  --random-suffix "$TASK_SUFFIX" \
  --owner-id owner-a \
  --initial-goal "Exercise ownership flow" >/dev/null

python3 - "$TASK_DIR" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])

with (task_dir / "ownership.json").open("r", encoding="utf-8") as fh:
    ownership = json.load(fh)

assert ownership["owner_id"] == "owner-a"
PY

OWNER_A_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/acquire_ownership.py" \
    --task-id "$TASK_ID" \
    --owner-id owner-a \
    --lease-seconds 900
)"

OWNER_A_LEASE="$(printf '%s' "$OWNER_A_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["lease_expires_at"])')"
OWNER_A_EVENT_SEQ="$(printf '%s' "$OWNER_A_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_seq"])')"

if ! printf '%s' "$OWNER_A_OUTPUT" | python3 -c 'import json,sys; assert json.load(sys.stdin)["result"]["owner_id"] == "owner-a"'; then
  echo "unexpected owner in first acquisition"
  exit 1
fi

if [ "$OWNER_A_EVENT_SEQ" != "3" ]; then
  echo "unexpected first ownership event_seq: $OWNER_A_EVENT_SEQ"
  exit 1
fi

OWNER_A_RENEW_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/acquire_ownership.py" \
    --task-id "$TASK_ID" \
    --owner-id owner-a \
    --lease-seconds 1200
)"

OWNER_A_RENEW_LEASE="$(printf '%s' "$OWNER_A_RENEW_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["lease_expires_at"])')"
OWNER_A_RENEW_EVENT_SEQ="$(printf '%s' "$OWNER_A_RENEW_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_seq"])')"

if [ "$OWNER_A_LEASE" = "$OWNER_A_RENEW_LEASE" ]; then
  echo "expected owner-a renew to change lease_expires_at"
  exit 1
fi

if [ "$OWNER_A_RENEW_EVENT_SEQ" != "4" ]; then
  echo "unexpected renew ownership event_seq: $OWNER_A_RENEW_EVENT_SEQ"
  exit 1
fi

set +e
OWNER_B_CONFLICT="$(
  python3 "$ROOT/skills/task-state-management/scripts/acquire_ownership.py" \
    --task-id "$TASK_ID" \
    --owner-id owner-b 2>&1
)"
OWNER_B_CONFLICT_EXIT=$?
set -e

if [ "$OWNER_B_CONFLICT_EXIT" -eq 0 ]; then
  echo "expected owner-b acquisition to fail while lease is active"
  exit 1
fi

if ! printf '%s' "$OWNER_B_CONFLICT" | grep -q "ownership held by another owner"; then
  echo "missing ownership conflict error"
  exit 1
fi

OWNER_B_FORCE_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/acquire_ownership.py" \
    --task-id "$TASK_ID" \
    --owner-id owner-b \
    --force
)"

OWNER_B_FORCE_EVENT_SEQ="$(printf '%s' "$OWNER_B_FORCE_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_seq"])')"

python3 - "$TASK_DIR" "$OWNER_B_FORCE_OUTPUT" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
payload = json.loads(sys.argv[2])

with (task_dir / "ownership.json").open("r", encoding="utf-8") as fh:
    ownership = json.load(fh)

assert payload["result"]["owner_id"] == "owner-b"
assert ownership["owner_id"] == "owner-b"
PY

if [ "$OWNER_B_FORCE_EVENT_SEQ" != "5" ]; then
  echo "unexpected forced ownership event_seq: $OWNER_B_FORCE_EVENT_SEQ"
  exit 1
fi

set +e
INVALID_TRANSFER_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/transfer_ownership.py" \
    --task-id "$TASK_ID" \
    --from-owner-id owner-a \
    --to-owner-id owner-c 2>&1
)"
INVALID_TRANSFER_EXIT=$?
set -e

if [ "$INVALID_TRANSFER_EXIT" -eq 0 ]; then
  echo "expected transfer by non-owner to fail"
  exit 1
fi

if ! printf '%s' "$INVALID_TRANSFER_OUTPUT" | grep -q "ownership held by another owner"; then
  echo "missing invalid transfer error"
  exit 1
fi

TRANSFER_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/transfer_ownership.py" \
    --task-id "$TASK_ID" \
    --from-owner-id owner-b \
    --to-owner-id owner-c \
    --reason "handoff"
)"

TRANSFER_EVENT_SEQ="$(printf '%s' "$TRANSFER_OUTPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["event_seq"])')"

python3 - "$TASK_DIR" "$TRANSFER_OUTPUT" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
payload = json.loads(sys.argv[2])

with (task_dir / "ownership.json").open("r", encoding="utf-8") as fh:
    ownership = json.load(fh)

assert payload["result"]["previous_owner_id"] == "owner-b"
assert payload["result"]["owner_id"] == "owner-c"
assert ownership["owner_id"] == "owner-c"
assert ownership["transfer_reason"] == "handoff"
PY

if [ "$TRANSFER_EVENT_SEQ" != "6" ]; then
  echo "unexpected transfer ownership event_seq: $TRANSFER_EVENT_SEQ"
  exit 1
fi

OWNER_C_RENEW_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/acquire_ownership.py" \
    --task-id "$TASK_ID" \
    --owner-id owner-c \
    --lease-seconds 600
)"

if ! printf '%s' "$OWNER_C_RENEW_OUTPUT" | python3 -c 'import json,sys; assert json.load(sys.stdin)["result"]["owner_id"] == "owner-c"'; then
  echo "unexpected owner after transfer renew"
  exit 1
fi

set +e
NO_OWNER_APPEND_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
    --task-id "$TASK_ID" \
    --event-type decision_recorded \
    --phase design \
    --source design-orchestrator \
    --summary "Should fail without owner" 2>&1
)"
NO_OWNER_APPEND_EXIT=$?
set -e

if [ "$NO_OWNER_APPEND_EXIT" -eq 0 ]; then
  echo "expected append_event.py to require owner-id"
  exit 1
fi

set +e
WRONG_OWNER_APPEND_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
    --task-id "$TASK_ID" \
    --owner-id owner-a \
    --event-type decision_recorded \
    --phase design \
    --source design-orchestrator \
    --summary "Should fail for stale owner" 2>&1
)"
WRONG_OWNER_APPEND_EXIT=$?
set -e

if [ "$WRONG_OWNER_APPEND_EXIT" -eq 0 ]; then
  echo "expected append_event.py to reject non-owner writer"
  exit 1
fi

if ! printf '%s' "$WRONG_OWNER_APPEND_OUTPUT" | grep -q "ownership held by another owner"; then
  echo "missing ownership gate error"
  exit 1
fi

python3 - "$TASK_DIR" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
ownership_path = task_dir / "ownership.json"
with ownership_path.open("r", encoding="utf-8") as fh:
    ownership = json.load(fh)
ownership["lease_expires_at"] = "2026-04-02T00:00:00+08:00"
with ownership_path.open("w", encoding="utf-8") as fh:
    json.dump(ownership, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
PY

set +e
EXPIRED_TRANSFER_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/transfer_ownership.py" \
    --task-id "$TASK_ID" \
    --from-owner-id owner-c \
    --to-owner-id owner-d 2>&1
)"
EXPIRED_TRANSFER_EXIT=$?
set -e

if [ "$EXPIRED_TRANSFER_EXIT" -eq 0 ]; then
  echo "expected transfer_ownership.py to reject expired owner lease"
  exit 1
fi

if ! printf '%s' "$EXPIRED_TRANSFER_OUTPUT" | grep -q "lease expired"; then
  echo "missing expired lease transfer error"
  exit 1
fi

python3 "$ROOT/skills/task-state-management/scripts/acquire_ownership.py" \
  --task-id "$TASK_ID" \
  --owner-id owner-c \
  --force >/dev/null

APPEND_OK_OUTPUT="$(
  python3 "$ROOT/skills/task-state-management/scripts/append_event.py" \
    --task-id "$TASK_ID" \
    --owner-id owner-c \
    --event-type decision_recorded \
    --phase design \
    --source design-orchestrator \
    --summary "Owner can append event"
)"

if ! printf '%s' "$APPEND_OK_OUTPUT" | python3 -c 'import json,sys; assert json.load(sys.stdin)["event_seq"] == 9'; then
  echo "expected owner append to succeed"
  exit 1
fi

python3 - "$TASK_DIR" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
with (task_dir / "events.jsonl").open("r", encoding="utf-8") as fh:
    rows = [json.loads(line) for line in fh if line.strip()]

ownership_rows = [row for row in rows if row["type"] in {"ownership_acquired", "ownership_transferred"}]

assert len(ownership_rows) == 7
assert ownership_rows[0]["type"] == "ownership_acquired"
assert ownership_rows[0]["owner_id"] == "owner-a"
assert ownership_rows[0]["renewed"] is False
assert ownership_rows[1]["renewed"] is True
assert ownership_rows[2]["renewed"] is True
assert ownership_rows[3]["force"] is True
assert ownership_rows[4]["type"] == "ownership_transferred"
assert ownership_rows[4]["from_owner_id"] == "owner-b"
assert ownership_rows[4]["to_owner_id"] == "owner-c"
assert ownership_rows[4]["transfer_reason"] == "handoff"
assert ownership_rows[5]["owner_id"] == "owner-c"
assert ownership_rows[5]["force"] is False
assert ownership_rows[6]["owner_id"] == "owner-c"
PY

echo "ok: ownership scripts acquired, renewed, rejected conflict, transferred, and gated writes"
