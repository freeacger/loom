from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (  # noqa: E402
    atomic_write_text,
    iso_timestamp,
    read_json,
    task_state_paths,
    validate_ownership,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Refresh a task status markdown view")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--owner-id", required=True)
    parser.add_argument("--state-kind", choices=("design", "plan", "execution"))
    parser.add_argument("--template")
    return parser


def summarize_state(state_kind: str, state: dict) -> str:
    status = state["status"]
    meta = state["meta"]
    label = state_kind.capitalize()
    return "\n".join(
        [
            f"### {label} State ({label} State)",
            "",
            f"- {label} phase: `{status['phase']}`",
            f"- {label} lifecycle: `{status['lifecycle_state']}`",
            f"- {label} validity: `{status['validity_state']}`",
            f"- {label} owner: `{status['owner']}`",
            f"- {label} state version: `{meta['state_version']}`",
            f"- {label} last applied event: `{meta['last_applied_event_id']}`",
            "",
        ]
    )


def build_status_markdown(task_id: str, states: dict[str, dict]) -> str:
    sections = []
    for state_kind in ("design", "plan", "execution"):
        if state_kind in states:
            sections.append(summarize_state(state_kind, states[state_kind]))

    return "\n".join(
        [
            "# 任务状态 (Task Status)",
            "",
            f"- Task ID: `{task_id}`",
            f"- Refreshed at: `{iso_timestamp()}`",
            "",
            *sections,
        ]
    )


def main() -> int:
    args = build_parser().parse_args()

    try:
        paths = task_state_paths(args.task_id)
        if not paths["task_dir"].exists():
            raise FileNotFoundError(f"task not found: {args.task_id}")
        validate_ownership(args.task_id, args.owner_id)

        state_kinds = (args.state_kind,) if args.state_kind else ("design", "plan", "execution")
        states: dict[str, dict] = {}
        for state_kind in state_kinds:
            state_path = paths[state_kind]
            states[state_kind] = read_json(state_path)

        markdown = build_status_markdown(args.task_id, states)
        atomic_write_text(paths["status"], markdown + "\n")

        result = {
            "ok": True,
            "task_id": args.task_id,
            "changed_files": [str(paths["status"])],
            "result": {
                "summary": f"Refreshed status view for {args.task_id}",
                "status_file": str(paths["status"]),
            },
        }
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (FileNotFoundError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
