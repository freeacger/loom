from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (  # noqa: E402
    append_jsonl,
    atomic_write_json,
    iso_timestamp,
    load_jsonl,
    make_event_id,
    next_event_seq,
    read_json,
    state_file_for_kind,
    task_state_paths,
    validate_ownership,
)


def parse_bool(value: str) -> bool:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise argparse.ArgumentTypeError("expected-no-blockers must be true or false")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mark an execution task as completed")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--owner-id", required=True)
    parser.add_argument("--completion-summary", required=True)
    parser.add_argument("--expected-validity-state", default="valid")
    parser.add_argument("--expected-no-blockers", type=parse_bool, default=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        paths = task_state_paths(args.task_id)
        if not paths["task_dir"].exists():
            raise FileNotFoundError(f"task not found: {args.task_id}")
        validate_ownership(args.task_id, args.owner_id)

        state_file = state_file_for_kind(args.task_id, "execution")
        state = read_json(state_file)
        if state["status"]["phase"] != "execution":
            raise ValueError("execution-state phase mismatch")
        if state["status"]["lifecycle_state"] == "completed":
            raise ValueError("task is already completed")
        if state["status"]["validity_state"] != args.expected_validity_state:
            raise ValueError(
                "unexpected validity_state: "
                f"expected {args.expected_validity_state}, got {state['status']['validity_state']}"
            )
        if args.expected_no_blockers and state["status"]["blocking_issues"]:
            raise ValueError("blocking_issues must be empty before completion")

        events = load_jsonl(paths["events"])
        event_seq = next_event_seq(events)
        event_id = make_event_id(args.task_id, event_seq)
        timestamp = iso_timestamp()

        event = {
            "event_id": event_id,
            "event_seq": event_seq,
            "type": "task_completed",
            "task_id": args.task_id,
            "phase": "cross_phase",
            "timestamp": timestamp,
            "source": "task-state-management",
            "summary": args.completion_summary,
            "final_state_ref": str(state_file),
        }
        append_jsonl(paths["events"], event)

        state["status"]["lifecycle_state"] = "completed"
        state["status"]["updated_at"] = timestamp
        state["meta"]["state_version"] = int(state["meta"]["state_version"]) + 1
        state["meta"]["last_applied_event_id"] = event_id

        atomic_write_json(state_file, state)

        result = {
            "ok": True,
            "task_id": args.task_id,
            "state_file": str(state_file),
            "changed_files": [str(paths["events"]), str(state_file)],
            "result": {
                "lifecycle_state": state["status"]["lifecycle_state"],
            },
            "event_id": event_id,
            "event_seq": event_seq,
            "state_version": state["meta"]["state_version"],
            "last_applied_event_id": event_id,
        }
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (FileNotFoundError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
