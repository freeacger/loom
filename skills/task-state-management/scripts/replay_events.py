from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (  # noqa: E402
    atomic_write_json,
    load_jsonl,
    parse_iso_timestamp,
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

SUPPORTED_REPLAY_EVENT_TYPES = {
    "handoff_completed",
    "blocking_issue_added",
    "blocking_issue_cleared",
    "state_revalidated",
    "task_completed",
}
SUPPORTED_OWNERSHIP_EVENT_TYPES = {
    "ownership_acquired",
    "ownership_transferred",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay task events into state snapshots")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--owner-id", required=True)
    parser.add_argument("--state-kind", choices=("design", "plan", "execution"))
    parser.add_argument("--include-ownership", action="store_true")
    parser.add_argument("--from-event-seq", type=int)
    parser.add_argument("--to-event-seq", type=int)
    return parser


def event_is_relevant_to_state(kind: str, phase: str, event: dict) -> bool:
    if event["phase"] == phase:
        return True
    if event["phase"] != "cross_phase":
        return False
    if event["type"] == "handoff_completed":
        return event.get("to_phase") == phase
    if event["type"] == "task_completed":
        return kind == "execution"
    return False


def apply_event(state: dict, kind: str, event: dict) -> None:
    event_type = event["type"]
    if event_type == "handoff_completed":
        if kind == "plan":
            state["source_design_ref"] = event["source_state_ref"]
            state["source_design_version"] = event["source_state_version"]
            state["source_design_event_id"] = event["source_event_id"]
        elif kind == "execution":
            state["source_plan_ref"] = event["source_state_ref"]
            state["source_plan_version"] = event["source_state_version"]
            state["source_plan_event_id"] = event["source_event_id"]
        state["status"]["lifecycle_state"] = "in_progress"
        state["status"]["validity_state"] = "valid"
        return

    if event_type == "blocking_issue_added":
        blocking_issue = event["blocking_issue"]
        existing_ids = {issue["id"] for issue in state["status"]["blocking_issues"]}
        if blocking_issue["id"] not in existing_ids:
            state["status"]["blocking_issues"].append(blocking_issue)
        state["status"]["lifecycle_state"] = "blocked"
        return

    if event_type == "blocking_issue_cleared":
        blocking_issue_id = event["blocking_issue_id"]
        state["status"]["blocking_issues"] = [
            issue for issue in state["status"]["blocking_issues"]
            if issue["id"] != blocking_issue_id
        ]
        state["status"]["lifecycle_state"] = "in_progress" if not state["status"]["blocking_issues"] else "blocked"
        return

    if event_type == "state_revalidated":
        state["status"]["validity_state"] = "valid"
        if kind == "plan" and "against_source_version" in event:
            state["source_design_version"] = event["against_source_version"]
        if kind == "execution" and "against_source_version" in event:
            state["source_plan_version"] = event["against_source_version"]
        return

    if event_type == "task_completed":
        state["status"]["lifecycle_state"] = "completed"
        return

    raise ValueError(f"unsupported replay event type: {event_type}")


def derive_ownership_from_event(task_id: str, event: dict) -> dict:
    if event["type"] == "ownership_acquired":
        return {
            "task_id": task_id,
            "owner_id": event["owner_id"],
            "acquired_at": event["timestamp"],
            "lease_expires_at": event["lease_expires_at"],
        }
    if event["type"] == "ownership_transferred":
        payload = {
            "task_id": task_id,
            "owner_id": event["to_owner_id"],
            "acquired_at": event["timestamp"],
            "lease_expires_at": event["lease_expires_at"],
        }
        if "transfer_reason" in event:
            payload["transfer_reason"] = event["transfer_reason"]
        return payload
    raise ValueError(f"unsupported ownership replay event type: {event['type']}")


def latest_ownership_event(
    events: list[dict],
    from_event_seq: int | None,
    to_event_seq: int | None,
) -> dict | None:
    candidates = [
        event
        for event in events
        if event["type"] in SUPPORTED_OWNERSHIP_EVENT_TYPES
        and (from_event_seq is None or int(event["event_seq"]) >= from_event_seq)
        and (to_event_seq is None or int(event["event_seq"]) <= to_event_seq)
    ]
    if not candidates:
        return None
    return candidates[-1]


def authorize_replay(
    task_id: str,
    owner_id: str,
    events: list[dict],
    include_ownership: bool,
    from_event_seq: int | None,
    to_event_seq: int | None,
) -> None:
    try:
        validate_ownership(task_id, owner_id)
        return
    except (FileNotFoundError, ValueError):
        if not include_ownership:
            raise

    ownership_event = latest_ownership_event(events, None, to_event_seq)
    if ownership_event is None:
        raise ValueError("cannot authorize replay without ownership events")

    derived = derive_ownership_from_event(task_id, ownership_event)
    if derived["owner_id"] != owner_id:
        raise ValueError(f"ownership held by another owner: {derived['owner_id']}")

    if parse_iso_timestamp(str(derived["lease_expires_at"])) <= datetime.now().astimezone():
        raise ValueError(f"ownership lease expired for owner: {derived['owner_id']}")


def main() -> int:
    args = build_parser().parse_args()

    try:
        paths = task_state_paths(args.task_id)
        if not paths["task_dir"].exists():
            raise FileNotFoundError(f"task not found: {args.task_id}")
        events = load_jsonl(paths["events"])
        authorize_replay(
            args.task_id,
            args.owner_id,
            events,
            args.include_ownership,
            args.from_event_seq,
            args.to_event_seq,
        )
        event_seq_by_id = {
            event["event_id"]: int(event["event_seq"])
            for event in events
        }
        state_kinds = (args.state_kind,) if args.state_kind else ("design", "plan", "execution")
        changed_files: list[str] = []
        repaired_states: list[dict[str, object]] = []

        for kind in state_kinds:
            state_file = state_file_for_kind(args.task_id, kind)
            state = read_json(state_file)
            last_applied_event_id = state["meta"]["last_applied_event_id"]
            if last_applied_event_id not in event_seq_by_id:
                raise ValueError(f"last_applied_event_id not found for replay: {last_applied_event_id}")

            last_applied_event_seq = event_seq_by_id[last_applied_event_id]
            phase = STATE_KIND_TO_PHASE[kind]
            candidate_events = [
                event
                for event in events
                if int(event["event_seq"]) > last_applied_event_seq
                and (args.from_event_seq is None or int(event["event_seq"]) >= args.from_event_seq)
                and (args.to_event_seq is None or int(event["event_seq"]) <= args.to_event_seq)
                and event_is_relevant_to_state(kind, phase, event)
            ]

            if not candidate_events:
                repaired_states.append(
                    {
                        "state_kind": kind,
                        "state_version": state["meta"]["state_version"],
                        "replayed_event_count": 0,
                    }
                )
                continue

            unsupported_types = sorted(
                {
                    event["type"]
                    for event in candidate_events
                    if event["type"] not in SUPPORTED_REPLAY_EVENT_TYPES
                }
            )
            if unsupported_types:
                raise ValueError(
                    f"unsupported replay event types for {kind}: {', '.join(unsupported_types)}"
                )

            for event in candidate_events:
                apply_event(state, kind, event)
                state["meta"]["state_version"] = int(state["meta"]["state_version"]) + 1
                state["meta"]["last_applied_event_id"] = event["event_id"]
                state["status"]["updated_at"] = event["timestamp"]

            atomic_write_json(state_file, state)
            changed_files.append(str(state_file))
            repaired_states.append(
                {
                    "state_kind": kind,
                    "state_version": state["meta"]["state_version"],
                    "replayed_event_count": len(candidate_events),
                }
            )

        ownership_result: dict[str, object] | None = None
        if args.include_ownership:
            ownership_event = latest_ownership_event(events, args.from_event_seq, args.to_event_seq)
            if ownership_event is None:
                ownership_result = {
                    "replayed_event_count": 0,
                    "owner_id": None,
                }
            else:
                target_ownership = derive_ownership_from_event(args.task_id, ownership_event)
                current_ownership = read_json(paths["ownership"]) if paths["ownership"].exists() else None
                if current_ownership == target_ownership:
                    ownership_result = {
                        "replayed_event_count": 0,
                        "owner_id": target_ownership["owner_id"],
                    }
                else:
                    candidate_events = [
                        event
                        for event in events
                        if event["type"] in SUPPORTED_OWNERSHIP_EVENT_TYPES
                        and (args.from_event_seq is None or int(event["event_seq"]) >= args.from_event_seq)
                        and (args.to_event_seq is None or int(event["event_seq"]) <= args.to_event_seq)
                    ]
                    atomic_write_json(paths["ownership"], target_ownership)
                    changed_files.append(str(paths["ownership"]))
                    ownership_result = {
                        "replayed_event_count": len(candidate_events),
                        "owner_id": target_ownership["owner_id"],
                    }

        result = {
            "ok": True,
            "task_id": args.task_id,
            "changed_files": changed_files,
            "result": {
                "replayed_states": repaired_states,
            },
        }
        if ownership_result is not None:
            result["result"]["ownership"] = ownership_result
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (FileNotFoundError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
