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
    parser = argparse.ArgumentParser(description="Acquire task ownership")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--owner-id", required=True)
    parser.add_argument("--lease-seconds", type=int, default=DEFAULT_LEASE_SECONDS)
    parser.add_argument("--force", action="store_true")
    return parser


def ownership_is_active(ownership: dict[str, object], now: datetime) -> bool:
    return parse_iso_timestamp(str(ownership["lease_expires_at"])) > now


def main() -> int:
    args = build_parser().parse_args()

    try:
        if args.lease_seconds <= 0:
            raise ValueError("lease-seconds must be positive")

        paths = task_state_paths(args.task_id)
        if not paths["task_dir"].exists():
            raise FileNotFoundError(f"task not found: {args.task_id}")

        ownership_path = paths["ownership"]
        now = datetime.now().astimezone()
        acquired_at = iso_timestamp()
        lease_until = lease_expires_at(args.lease_seconds, now)
        events = load_jsonl(paths["events"])
        event_seq = next_event_seq(events)
        event_id = make_event_id(args.task_id, event_seq)

        if ownership_path.exists():
            current = read_json(ownership_path)
            current_owner_id = str(current["owner_id"])
            active = ownership_is_active(current, now)

            if current_owner_id != args.owner_id and active and not args.force:
                raise ValueError(f"ownership held by another owner: {current_owner_id}")
        else:
            current = None

        previous_owner_id = None if current is None else str(current["owner_id"])
        is_renewal = previous_owner_id == args.owner_id and current is not None
        event = {
            "event_id": event_id,
            "event_seq": event_seq,
            "type": "ownership_acquired",
            "task_id": args.task_id,
            "phase": "cross_phase",
            "timestamp": acquired_at,
            "source": "task-state-management",
            "summary": f"Ownership acquired by {args.owner_id}",
            "owner_id": args.owner_id,
            "previous_owner_id": previous_owner_id,
            "lease_expires_at": lease_until,
            "force": args.force,
            "renewed": is_renewal,
        }
        append_jsonl(paths["events"], event)

        ownership = {
            "task_id": args.task_id,
            "owner_id": args.owner_id,
            "acquired_at": acquired_at,
            "lease_expires_at": lease_until,
        }
        atomic_write_json(ownership_path, ownership)

        result = {
            "ok": True,
            "task_id": args.task_id,
            "changed_files": [str(paths["events"]), str(ownership_path)],
            "result": {
                "ownership_file": str(ownership_path),
                "owner_id": args.owner_id,
                "lease_expires_at": lease_until,
                "replaced_existing": current is not None,
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
