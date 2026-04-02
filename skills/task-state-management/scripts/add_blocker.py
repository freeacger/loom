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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Add a blocking issue to a task state")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--owner-id", required=True)
    parser.add_argument("--state-kind", required=True, choices=("design", "plan", "execution"))
    parser.add_argument("--reason", required=True)
    parser.add_argument("--severity", required=True, choices=("low", "medium", "high"))
    parser.add_argument("--source", required=True, choices=("design", "planning", "execution", "external"))
    parser.add_argument("--summary")
    parser.add_argument("--blocking-issue-id")
    return parser


def build_blocking_issue(
    blocking_issue_id: str,
    reason: str,
    severity: str,
    source: str,
    created_at: str,
) -> dict[str, object]:
    return {
        "id": blocking_issue_id,
        "reason": reason,
        "severity": severity,
        "source": source,
        "created_at": created_at,
        "cleared": False,
    }


def main() -> int:
    args = build_parser().parse_args()

    try:
        paths = task_state_paths(args.task_id)
        if not paths["task_dir"].exists():
            raise FileNotFoundError(f"task not found: {args.task_id}")
        validate_ownership(args.task_id, args.owner_id)

        state_file = state_file_for_kind(args.task_id, args.state_kind)
        state = read_json(state_file)
        events = load_jsonl(paths["events"])
        event_seq = next_event_seq(events)
        event_id = make_event_id(args.task_id, event_seq)
        timestamp = iso_timestamp()
        blocking_issue_id = args.blocking_issue_id or f"blk-{event_seq:04d}"

        for issue in state["status"]["blocking_issues"]:
            if issue["id"] == blocking_issue_id:
                raise ValueError(f"blocking issue already exists: {blocking_issue_id}")

        blocking_issue = build_blocking_issue(
            blocking_issue_id=blocking_issue_id,
            reason=args.reason,
            severity=args.severity,
            source=args.source,
            created_at=timestamp,
        )
        summary = args.summary or args.reason

        event = {
            "event_id": event_id,
            "event_seq": event_seq,
            "type": "blocking_issue_added",
            "task_id": args.task_id,
            "phase": state["status"]["phase"],
            "timestamp": timestamp,
            "source": "task-state-management",
            "summary": summary,
            "blocking_issue": blocking_issue,
            "state_kind": args.state_kind,
        }
        append_jsonl(paths["events"], event)

        state["status"]["blocking_issues"].append(blocking_issue)
        state["status"]["lifecycle_state"] = "blocked"
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
                "blocking_issue_id": blocking_issue_id,
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
