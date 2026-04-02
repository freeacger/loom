from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (  # noqa: E402
    atomic_write_json,
    iso_timestamp,
    merge_patch,
    read_json,
    state_file_for_kind,
    task_state_paths,
    validate_ownership,
)

STATE_KIND_TO_PHASE = {
    "design": "design",
    "plan": "planning",
    "execution": "execution",
}


def event_is_relevant_to_state(kind: str, event: dict) -> bool:
    phase = STATE_KIND_TO_PHASE[kind]
    if event["phase"] == phase:
        return True
    if event["phase"] != "cross_phase":
        return False
    if event["type"] == "task_created":
        return True
    if event["type"] == "handoff_completed":
        return event.get("to_phase") == phase
    if event["type"] == "task_completed":
        return kind == "execution"
    return False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update a task state snapshot")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--owner-id", required=True)
    parser.add_argument("--state-kind", required=True, choices=("design", "plan", "execution"))
    parser.add_argument("--patch-file", required=True)
    parser.add_argument("--expected-last-applied-event-id", required=True)
    parser.add_argument("--expected-state-version", type=int)
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        paths = task_state_paths(args.task_id)
        if not paths["task_dir"].exists():
            raise FileNotFoundError(f"task not found: {args.task_id}")
        validate_ownership(args.task_id, args.owner_id)

        state_file = state_file_for_kind(args.task_id, args.state_kind)
        state = read_json(state_file)
        patch = read_json(Path(args.patch_file))

        current_event_id = state["meta"]["last_applied_event_id"]

        events_path = paths["events"]
        with events_path.open("r", encoding="utf-8") as fh:
            event_seq_by_id = {
                row["event_id"]: int(row["event_seq"])
                for row in (
                    json.loads(line)
                    for line in fh
                    if line.strip()
                )
            }
        if args.expected_last_applied_event_id not in event_seq_by_id:
            raise ValueError(f"event not found: {args.expected_last_applied_event_id}")
        if current_event_id not in event_seq_by_id:
            raise ValueError(f"current last_applied_event_id not found: {current_event_id}")

        current_event_seq = event_seq_by_id[current_event_id]
        next_event_seq = event_seq_by_id[args.expected_last_applied_event_id]
        if next_event_seq <= current_event_seq:
            raise ValueError("expected_last_applied_event_id must point to a newer event")
        target_event = next(
            event for event in (
                json.loads(line)
                for line in events_path.open("r", encoding="utf-8")
                if line.strip()
            )
            if event["event_id"] == args.expected_last_applied_event_id
        )
        if not event_is_relevant_to_state(args.state_kind, target_event):
            raise ValueError("expected_last_applied_event_id must reference an event relevant to the target state")

        current_version = int(state["meta"]["state_version"])
        if args.expected_state_version is not None and current_version != args.expected_state_version:
            raise ValueError(
                f"state_version mismatch: expected {args.expected_state_version}, got {current_version}"
            )

        merged = merge_patch(state, patch)
        merged["meta"]["state_version"] = current_version + 1
        merged["meta"]["last_applied_event_id"] = args.expected_last_applied_event_id
        merged["status"]["updated_at"] = iso_timestamp()

        atomic_write_json(state_file, merged)

        result = {
            "ok": True,
            "task_id": args.task_id,
            "changed_files": [str(state_file)],
            "result": {"state_file": str(state_file)},
            "state_version": merged["meta"]["state_version"],
            "last_applied_event_id": merged["meta"]["last_applied_event_id"],
        }
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (FileNotFoundError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
