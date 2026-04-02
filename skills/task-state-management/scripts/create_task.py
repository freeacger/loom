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
    atomic_write_text,
    build_task_id,
    current_date_string,
    iso_timestamp,
    is_valid_task_name,
    lease_expires_at,
    make_event_id,
    task_state_paths,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a task state skeleton")
    parser.add_argument("--task-name", required=True)
    parser.add_argument("--date")
    parser.add_argument("--random-suffix")
    parser.add_argument("--owner-id", required=True)
    parser.add_argument("--initial-goal", default="")
    return parser


def build_initial_state(task_id: str, phase: str, event_id: str) -> dict:
    return {
        "task_id": task_id,
        "problem": "",
        "scope": {"included": [], "excluded": []},
        "design_tree": [],
        "open_branches": [],
        "decision_nodes": [],
        "external_dependencies": [],
        "decisions": [],
        "risks": [],
        "validation": [],
        "meta": {
            "state_version": 1,
            "last_applied_event_id": event_id,
        },
        "status": {
            "phase": phase,
            "lifecycle_state": "draft",
            "validity_state": "valid",
            "blocking_issues": [],
            "updated_at": iso_timestamp(),
            "owner": "",
        },
    }


def main() -> int:
    args = build_parser().parse_args()

    try:
        if not is_valid_task_name(args.task_name):
            raise ValueError("task-name must be kebab-case lower ASCII letters and digits")

        task_id = build_task_id(args.task_name, args.date or current_date_string(), args.random_suffix)
        paths = task_state_paths(task_id)
        if paths["task_dir"].exists():
            raise ValueError(f"task already exists: {task_id}")

        for path in [paths["task_dir"] / "states", paths["task_dir"]]:
            path.mkdir(parents=True, exist_ok=True)

        event_seq = 1
        event_id = make_event_id(task_id, event_seq)
        task_created_at = iso_timestamp()
        event = {
            "event_id": event_id,
            "event_seq": event_seq,
            "type": "task_created",
            "task_id": task_id,
            "phase": "cross_phase",
            "timestamp": task_created_at,
            "source": "system",
            "summary": args.initial_goal or "Task created",
            "initial_goal": args.initial_goal,
        }

        append_jsonl(paths["events"], event)

        design_state = build_initial_state(task_id, "design", event_id)
        plan_state = build_initial_state(task_id, "planning", event_id)
        execution_state = build_initial_state(task_id, "execution", event_id)
        ownership_acquired_at = iso_timestamp()
        ownership = {
            "task_id": task_id,
            "owner_id": args.owner_id,
            "acquired_at": ownership_acquired_at,
            "lease_expires_at": lease_expires_at(900),
        }
        ownership_event = {
            "event_id": make_event_id(task_id, 2),
            "event_seq": 2,
            "type": "ownership_acquired",
            "task_id": task_id,
            "phase": "cross_phase",
            "timestamp": ownership_acquired_at,
            "source": "task-state-management",
            "summary": f"Initial ownership assigned to {args.owner_id}",
            "owner_id": args.owner_id,
            "previous_owner_id": None,
            "lease_expires_at": ownership["lease_expires_at"],
            "force": False,
            "renewed": False,
        }
        append_jsonl(paths["events"], ownership_event)

        atomic_write_json(paths["design"], design_state)
        atomic_write_json(paths["plan"], plan_state)
        atomic_write_json(paths["execution"], execution_state)
        atomic_write_json(paths["ownership"], ownership)

        status_markdown = "\n".join(
            [
                f"# 任务状态 (Task Status)",
                "",
                f"- Task ID: `{task_id}`",
                f"- Phase: `design`",
                f"- Lifecycle: `draft`",
                f"- Validity: `valid`",
                f"- Goal: {args.initial_goal or ''}",
                f"- Last event: `{event_id}`",
                "",
            ]
        )
        atomic_write_text(paths["status"], status_markdown)

        payload = {
            "ok": True,
            "task_id": task_id,
            "changed_files": [
                str(paths["status"]),
                str(paths["events"]),
                str(paths["design"]),
                str(paths["plan"]),
                str(paths["execution"]),
                str(paths["ownership"]),
            ],
            "result": {
                "task_dir": str(paths["task_dir"]),
                "state_files": [
                    str(paths["design"]),
                    str(paths["plan"]),
                    str(paths["execution"]),
                ],
                "status_file": str(paths["status"]),
                "events_file": str(paths["events"]),
                "ownership_file": str(paths["ownership"]),
            },
            "event_id": event_id,
            "event_seq": event_seq,
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
