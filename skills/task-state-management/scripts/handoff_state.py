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

SUPPORTED_HANDOFFS = {
    ("design", "planning"),
    ("planning", "execution"),
}

PHASE_TO_STATE_KIND = {
    "design": "design",
    "planning": "plan",
    "execution": "execution",
}

PHASE_TO_SOURCE_PREFIX = {
    "design": "source_design",
    "planning": "source_plan",
}

PHASE_TO_HANDOFF_LABEL = {
    "design": "design",
    "planning": "plan",
    "execution": "execution",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record a task phase handoff")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--owner-id", required=True)
    parser.add_argument("--from-phase", required=True, choices=("design", "planning"))
    parser.add_argument("--to-phase", required=True, choices=("planning", "execution"))
    parser.add_argument("--summary")
    parser.add_argument("--summary-file")
    parser.add_argument("--source-state-version", type=int)
    parser.add_argument("--source-event-id")
    return parser


def load_summary(summary: str | None, summary_file: str | None) -> str:
    if summary and summary_file:
        raise ValueError("only one of --summary or --summary-file can be provided")
    if summary_file:
        with Path(summary_file).open("r", encoding="utf-8") as fh:
            file_summary = fh.read().strip()
        return file_summary or f"Handoff from {summary_file}"
    if summary:
        return summary
    return "handoff completed"


def state_file_for_phase(task_id: str, phase: str) -> Path:
    try:
        return state_file_for_kind(task_id, PHASE_TO_STATE_KIND[phase])
    except KeyError as exc:
        raise ValueError(f"unsupported phase: {phase}") from exc


def handoff_kind(from_phase: str, to_phase: str) -> str:
    return f"{PHASE_TO_HANDOFF_LABEL[from_phase]}_to_{PHASE_TO_HANDOFF_LABEL[to_phase]}"


def main() -> int:
    args = build_parser().parse_args()

    try:
        if (args.from_phase, args.to_phase) not in SUPPORTED_HANDOFFS:
            raise ValueError(f"unsupported handoff: {args.from_phase} -> {args.to_phase}")
        if args.from_phase not in PHASE_TO_SOURCE_PREFIX:
            raise ValueError(f"unsupported phase: {args.from_phase}")

        paths = task_state_paths(args.task_id)
        if not paths["task_dir"].exists():
            raise FileNotFoundError(f"task not found: {args.task_id}")
        validate_ownership(args.task_id, args.owner_id)

        source_state_file = state_file_for_phase(args.task_id, args.from_phase)
        target_state_file = state_file_for_phase(args.task_id, args.to_phase)
        source_state = read_json(source_state_file)
        target_state = read_json(target_state_file)

        if source_state["status"]["phase"] != args.from_phase:
            raise ValueError(
                f"source state phase mismatch: expected {args.from_phase}, got {source_state['status']['phase']}"
            )
        if target_state["status"]["phase"] != args.to_phase:
            raise ValueError(
                f"target state phase mismatch: expected {args.to_phase}, got {target_state['status']['phase']}"
            )

        source_state_version = int(source_state["meta"]["state_version"])
        source_event_id = source_state["meta"]["last_applied_event_id"]
        if args.source_state_version is not None and args.source_state_version != source_state_version:
            raise ValueError(
                "source_state_version mismatch: "
                f"expected {args.source_state_version}, got {source_state_version}"
            )
        if args.source_event_id is not None and args.source_event_id != source_event_id:
            raise ValueError(
                f"source_event_id mismatch: expected {args.source_event_id}, got {source_event_id}"
            )

        summary = load_summary(args.summary, args.summary_file)
        events = load_jsonl(paths["events"])
        event_seq = next_event_seq(events)
        event_id = make_event_id(args.task_id, event_seq)
        timestamp = iso_timestamp()
        source_prefix = PHASE_TO_SOURCE_PREFIX[args.from_phase]

        event = {
            "event_id": event_id,
            "event_seq": event_seq,
            "type": "handoff_completed",
            "task_id": args.task_id,
            "phase": "cross_phase",
            "timestamp": timestamp,
            "source": "task-state-management",
            "summary": summary,
            "handoff_kind": handoff_kind(args.from_phase, args.to_phase),
            "from_phase": args.from_phase,
            "to_phase": args.to_phase,
            "source_state_ref": str(source_state_file),
            "target_state_ref": str(target_state_file),
            "source_state_version": source_state_version,
            "source_event_id": source_event_id,
        }

        append_jsonl(paths["events"], event)

        target_state[source_prefix + "_ref"] = str(source_state_file)
        target_state[source_prefix + "_version"] = source_state_version
        target_state[source_prefix + "_event_id"] = source_event_id
        target_state["meta"]["state_version"] = int(target_state["meta"]["state_version"]) + 1
        target_state["meta"]["last_applied_event_id"] = event_id
        target_state["status"]["lifecycle_state"] = "in_progress"
        target_state["status"]["validity_state"] = "valid"
        target_state["status"]["updated_at"] = timestamp

        atomic_write_json(target_state_file, target_state)

        result = {
            "ok": True,
            "task_id": args.task_id,
            "from_state_file": str(source_state_file),
            "to_state_file": str(target_state_file),
            "changed_files": [str(paths["events"]), str(target_state_file)],
            "state_version": target_state["meta"]["state_version"],
            "last_applied_event_id": event_id,
            "result": {
                "handoff_kind": handoff_kind(args.from_phase, args.to_phase),
                "summary": summary,
                "state_version": target_state["meta"]["state_version"],
                "last_applied_event_id": event_id,
                "source_state_version": source_state_version,
                "source_event_id": source_event_id,
            },
            "event_id": event_id,
            "event_seq": event_seq,
        }
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (FileNotFoundError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
