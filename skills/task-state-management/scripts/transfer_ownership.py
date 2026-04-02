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
    lease_expires_at,
    load_jsonl,
    make_event_id,
    next_event_seq,
    parse_iso_timestamp,
    read_json,
    task_state_paths,
)


DEFAULT_LEASE_SECONDS = 900


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transfer task ownership")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--from-owner-id", required=True)
    parser.add_argument("--to-owner-id", required=True)
    parser.add_argument("--reason")
    parser.add_argument("--lease-seconds", type=int, default=DEFAULT_LEASE_SECONDS)
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        if args.lease_seconds <= 0:
            raise ValueError("lease-seconds must be positive")

        paths = task_state_paths(args.task_id)
        if not paths["task_dir"].exists():
            raise FileNotFoundError(f"task not found: {args.task_id}")
        if not paths["ownership"].exists():
            raise FileNotFoundError(f"ownership not found: {args.task_id}")

        current = read_json(paths["ownership"])
        current_owner_id = str(current["owner_id"])
        if current_owner_id != args.from_owner_id:
            raise ValueError(f"ownership held by another owner: {current_owner_id}")
        if parse_iso_timestamp(str(current["lease_expires_at"])) <= parse_iso_timestamp(iso_timestamp()):
            raise ValueError(f"ownership lease expired for owner: {current_owner_id}")

        transferred_at = iso_timestamp()
        events = load_jsonl(paths["events"])
        event_seq = next_event_seq(events)
        event_id = make_event_id(args.task_id, event_seq)
        updated = {
            "task_id": args.task_id,
            "owner_id": args.to_owner_id,
            "acquired_at": transferred_at,
            "lease_expires_at": lease_expires_at(args.lease_seconds),
        }
        if args.reason:
            updated["transfer_reason"] = args.reason

        event = {
            "event_id": event_id,
            "event_seq": event_seq,
            "type": "ownership_transferred",
            "task_id": args.task_id,
            "phase": "cross_phase",
            "timestamp": transferred_at,
            "source": "task-state-management",
            "summary": args.reason or f"Ownership transferred to {args.to_owner_id}",
            "from_owner_id": args.from_owner_id,
            "to_owner_id": args.to_owner_id,
            "lease_expires_at": updated["lease_expires_at"],
        }
        if args.reason:
            event["transfer_reason"] = args.reason
        append_jsonl(paths["events"], event)

        atomic_write_json(paths["ownership"], updated)

        result = {
            "ok": True,
            "task_id": args.task_id,
            "changed_files": [str(paths["events"]), str(paths["ownership"])],
            "result": {
                "previous_owner_id": current_owner_id,
                "owner_id": args.to_owner_id,
                "lease_expires_at": updated["lease_expires_at"],
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
