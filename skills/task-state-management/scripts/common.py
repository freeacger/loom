from __future__ import annotations

import json
import os
import random
import re
import string
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


TASK_ID_PATTERN = re.compile(r"^\d{8}-[a-z0-9]+(?:-[a-z0-9]+)*-[a-z0-9]{2}$")
TASK_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def docs_root() -> Path:
    return repo_root() / "docs"


def tasks_root() -> Path:
    return docs_root() / "tasks"


def task_dir(task_id: str) -> Path:
    return tasks_root() / task_id


def is_valid_task_name(task_name: str) -> bool:
    return bool(TASK_NAME_PATTERN.fullmatch(task_name))


def is_valid_task_id(task_id: str) -> bool:
    return bool(TASK_ID_PATTERN.fullmatch(task_id))


def current_date_string() -> str:
    return datetime.now().astimezone().strftime("%Y%m%d")


def generate_suffix() -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(2))


def build_task_id(task_name: str, date_str: str | None = None, suffix: str | None = None) -> str:
    if not is_valid_task_name(task_name):
        raise ValueError("task_name must be kebab-case lower ASCII letters and digits")
    date_part = date_str or current_date_string()
    if not re.fullmatch(r"\d{8}", date_part):
        raise ValueError("date must be YYYYMMDD")
    suffix_part = suffix or generate_suffix()
    if not re.fullmatch(r"[a-z0-9]{2}", suffix_part):
        raise ValueError("random suffix must be exactly two lowercase letters or digits")
    return f"{date_part}-{task_name}-{suffix_part}"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as fh:
        content = fh.read().strip()
    if not content:
        if default is not None:
            return default
        raise ValueError(f"empty json file: {path}")
    return json.loads(content)


def atomic_write_text(path: Path, content: str) -> None:
    ensure_parent(path)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        delete=False,
        dir=str(path.parent),
        prefix=f".{path.name}.",
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, path)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    line = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)
        fh.write("\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        rows = []
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
        return rows


def next_event_seq(events: list[dict[str, Any]]) -> int:
    if not events:
        return 1
    return int(events[-1]["event_seq"]) + 1


def make_event_id(task_id: str, event_seq: int) -> str:
    return f"{task_id}-evt-{event_seq:04d}"


def iso_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def task_state_paths(task_id: str) -> dict[str, Path]:
    base = task_dir(task_id)
    return {
        "task_dir": base,
        "ownership": base / "ownership.json",
        "status": base / "status.md",
        "events": base / "events.jsonl",
        "design": base / "states" / "design-state.json",
        "plan": base / "states" / "plan-state.json",
        "execution": base / "states" / "execution-state.json",
    }


def state_file_for_kind(task_id: str, state_kind: str) -> Path:
    paths = task_state_paths(task_id)
    mapping = {
        "design": paths["design"],
        "plan": paths["plan"],
        "execution": paths["execution"],
    }
    try:
        return mapping[state_kind]
    except KeyError as exc:
        raise ValueError(f"unsupported state kind: {state_kind}") from exc


def merge_patch(base: Any, patch: Any) -> Any:
    if isinstance(base, dict) and isinstance(patch, dict):
        merged = dict(base)
        for key, value in patch.items():
            if key in merged:
                merged[key] = merge_patch(merged[key], value)
            else:
                merged[key] = value
        return merged
    return patch


@dataclass(frozen=True)
class TaskCreationResult:
    task_id: str
    task_dir: str
    state_files: list[str]
    status_file: str
    events_file: str
    event_id: str
    event_seq: int
    changed_files: list[str]


def parse_iso_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


def lease_expires_at(lease_seconds: int, now: datetime | None = None) -> str:
    current = now or datetime.now().astimezone()
    return (current + timedelta(seconds=lease_seconds)).isoformat(timespec="seconds")


def validate_ownership(task_id: str, owner_id: str) -> dict[str, Any]:
    paths = task_state_paths(task_id)
    ownership_path = paths["ownership"]
    if not ownership_path.exists():
        raise FileNotFoundError(f"ownership not found: {task_id}")

    ownership = read_json(ownership_path)
    current_owner_id = str(ownership["owner_id"])
    if current_owner_id != owner_id:
        raise ValueError(f"ownership held by another owner: {current_owner_id}")

    expires_at = parse_iso_timestamp(str(ownership["lease_expires_at"]))
    if expires_at <= datetime.now().astimezone():
        raise ValueError(f"ownership lease expired for owner: {current_owner_id}")

    return ownership
