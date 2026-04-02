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


SOURCE_VERSION_FIELD = {
    "design": None,
    "plan": "source_design_version",
    "execution": "source_plan_version",
}

SOURCE_STATE_KIND = {
    "plan": "design",
    "execution": "plan",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Revalidate a stale task state")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--owner-id", required=True)
    parser.add_argument("--state-kind", required=True, choices=("design", "plan", "execution"))
    parser.add_argument("--against-source-version", required=True, type=int)
    parser.add_argument("--reason", required=True)
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
        current_validity = state["status"]["validity_state"]
        if current_validity != "stale":
            raise ValueError(f"state must be stale before revalidation: {current_validity}")

        source_version_field = SOURCE_VERSION_FIELD[args.state_kind]
        if source_version_field and source_version_field in state:
            current_source_version = int(state[source_version_field])
            if args.against_source_version < current_source_version:
                raise ValueError(
                    "against_source_version must not be older than current source version"
                )

            source_state_kind = SOURCE_STATE_KIND[args.state_kind]
            source_state_file = state_file_for_kind(args.task_id, source_state_kind)
            source_state = read_json(source_state_file)
            actual_source_version = int(source_state["meta"]["state_version"])
            if args.against_source_version != actual_source_version:
                raise ValueError(
                    "against_source_version must match actual upstream state_version"
                )

        events = load_jsonl(paths["events"])
        event_seq = next_event_seq(events)
        event_id = make_event_id(args.task_id, event_seq)
        timestamp = iso_timestamp()

        event = {
            "event_id": event_id,
            "event_seq": event_seq,
            "type": "state_revalidated",
            "task_id": args.task_id,
            "phase": state["status"]["phase"],
            "timestamp": timestamp,
            "source": "task-state-management",
            "summary": args.reason,
            "state_kind": args.state_kind,
            "from_validity_state": current_validity,
            "to_validity_state": "valid",
            "against_source_version": args.against_source_version,
        }
        append_jsonl(paths["events"], event)

        if source_version_field and source_version_field in state:
            state[source_version_field] = args.against_source_version

        state["status"]["validity_state"] = "valid"
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
                "validity_state": state["status"]["validity_state"],
                "against_source_version": args.against_source_version,
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
