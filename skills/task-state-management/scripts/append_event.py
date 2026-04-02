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
    iso_timestamp,
    load_jsonl,
    make_event_id,
    next_event_seq,
    task_state_paths,
    validate_ownership,
)

RESERVED_EVENT_FIELDS = {
    "event_id",
    "event_seq",
    "type",
    "task_id",
    "phase",
    "timestamp",
    "source",
    "summary",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Append an event to a task event stream")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--owner-id", required=True)
    parser.add_argument("--event-type", required=True)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--payload-file")
    return parser


def load_payload(payload_file: str | None) -> dict:
    if not payload_file:
        return {}
    with Path(payload_file).open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    conflicting_fields = sorted(RESERVED_EVENT_FIELDS.intersection(payload.keys()))
    if conflicting_fields:
        raise ValueError(
            "payload must not override reserved event fields: "
            + ", ".join(conflicting_fields)
        )
    return payload


def main() -> int:
    args = build_parser().parse_args()

    try:
        paths = task_state_paths(args.task_id)
        if not paths["task_dir"].exists():
            raise FileNotFoundError(f"task not found: {args.task_id}")
        validate_ownership(args.task_id, args.owner_id)

        events = load_jsonl(paths["events"])
        event_seq = next_event_seq(events)
        event_id = make_event_id(args.task_id, event_seq)
        payload = load_payload(args.payload_file)

        event = {
            "event_id": event_id,
            "event_seq": event_seq,
            "type": args.event_type,
            "task_id": args.task_id,
            "phase": args.phase,
            "timestamp": iso_timestamp(),
            "source": args.source,
            "summary": args.summary,
        }
        event.update(payload)

        append_jsonl(paths["events"], event)

        result = {
            "ok": True,
            "task_id": args.task_id,
            "changed_files": [str(paths["events"])],
            "result": {"events_file": str(paths["events"])},
            "event_id": event_id,
            "event_seq": event_seq,
        }
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
