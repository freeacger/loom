from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (  # noqa: E402
    load_jsonl,
    read_json,
    task_state_paths,
)


STATE_KIND_TO_PHASE = {
    "design": "design",
    "plan": "planning",
    "execution": "execution",
}


def event_is_relevant_to_state(kind: str, phase: str, event: dict) -> bool:
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
    parser = argparse.ArgumentParser(description="Validate a task state directory")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--state-kind", choices=("design", "plan", "execution"))
    return parser


def validate_state(task_id: str, strict: bool, state_kind: str | None) -> dict:
    paths = task_state_paths(task_id)
    findings: list[str] = []
    recommended_actions: list[str] = []
    status = "ok"

    if not paths["task_dir"].exists():
        return {
            "status": "invalid",
            "findings": [f"task directory missing: {paths['task_dir']}"],
            "recommended_actions": ["create the task directory again"],
        }

    try:
        events = load_jsonl(paths["events"])
    except json.JSONDecodeError as exc:
        return {
            "status": "invalid",
            "findings": [f"events.jsonl is invalid JSONL: {exc}"],
            "recommended_actions": ["repair or replay the event stream"],
        }

    if not paths["events"].exists():
        return {
            "status": "invalid",
            "findings": ["events.jsonl is missing"],
            "recommended_actions": ["recreate the task events file"],
        }

    if not events:
        return {
            "status": "recovery_needed",
            "findings": ["events.jsonl has no events"],
            "recommended_actions": ["replay or recreate the task event stream"],
        }

    event_seq_by_id = {
        event["event_id"]: int(event["event_seq"])
        for event in events
    }

    state_kinds = (state_kind,) if state_kind else ("design", "plan", "execution")
    for kind in state_kinds:
        state_path = paths[kind]
        if not state_path.exists():
            return {
                "status": "invalid",
                "findings": [f"missing state file: {state_path}"],
                "recommended_actions": [f"recreate {kind}-state.json from the event stream"],
            }
        try:
            state = read_json(state_path)
        except json.JSONDecodeError as exc:
            return {
                "status": "invalid",
                "findings": [f"invalid JSON in {state_path}: {exc}"],
                "recommended_actions": [f"repair or replay {kind}-state.json"],
            }

        meta = state.get("meta", {})
        state_version = meta.get("state_version")
        last_applied_event_id = meta.get("last_applied_event_id")
        state_phase = STATE_KIND_TO_PHASE[kind]

        if not isinstance(state_version, int):
            return {
                "status": "invalid",
                "findings": [f"state_version is not an integer in {state_path}"],
                "recommended_actions": [f"repair {kind}-state.json"],
            }

        if state_version < 1:
            return {
                "status": "invalid",
                "findings": [f"state_version must be positive in {state_path}"],
                "recommended_actions": [f"repair {kind}-state.json"],
            }

        if not last_applied_event_id:
            return {
                "status": "recovery_needed",
                "findings": [f"last_applied_event_id missing in {state_path}"],
                "recommended_actions": [f"replay events into {kind}-state.json"],
            }

        if not any(event["event_id"] == last_applied_event_id for event in events):
            return {
                "status": "recovery_needed",
                "findings": [
                    f"last_applied_event_id not found in event stream for {state_path}",
                ],
                "recommended_actions": [f"replay events into {kind}-state.json"],
            }

        last_applied_event = next(
            event for event in events
            if event["event_id"] == last_applied_event_id
        )
        if not event_is_relevant_to_state(kind, state_phase, last_applied_event):
            return {
                "status": "recovery_needed",
                "findings": [
                    f"last_applied_event_id is not relevant to {kind}-state.json",
                ],
                "recommended_actions": [f"repair or replay {kind}-state.json"],
            }

        last_applied_event_seq = event_seq_by_id[last_applied_event_id]
        newer_relevant_events = [
            event
            for event in events
            if int(event["event_seq"]) > last_applied_event_seq
            and event_is_relevant_to_state(kind, state_phase, event)
        ]
        if newer_relevant_events:
            return {
                "status": "recovery_needed",
                "findings": [
                    f"newer events are present after last_applied_event_id in {state_path}",
                ],
                "recommended_actions": [f"replay events into {kind}-state.json"],
            }

    if not paths["status"].exists():
        status = "warning"
        findings.append("status.md is missing")
        recommended_actions.append("refresh the status view")

    if strict and status == "warning":
        status = "recovery_needed"
        recommended_actions.append("treat missing status.md as a recovery action in strict mode")

    return {
        "status": status,
        "findings": findings,
        "recommended_actions": recommended_actions,
    }


def main() -> int:
    args = build_parser().parse_args()

    try:
        result = validate_state(args.task_id, args.strict, args.state_kind)
        payload = {
            "ok": result["status"] in {"ok", "warning"},
            "task_id": args.task_id,
            "changed_files": [],
            "result": result,
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    except (FileNotFoundError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
