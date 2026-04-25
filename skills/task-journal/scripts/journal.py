#!/usr/bin/env python3
# task-journal 的轻量 helper：仅提供 append 与 read 两个子命令
# 设计原则：stdlib only，不做语义校验（语义校验交给 lint_tasks.py）
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# 用全 Unicode 形式的 em dash 作为协议分隔符
EM_DASH = "—"

# 用于在 read --last N 时切分 entry
HEADING_PREFIX = "## "


def parse_iso8601(value: str) -> datetime:
    # Python 3.10 之前的 fromisoformat 不接受末尾 Z，做一次兼容
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)


def now_iso() -> str:
    # 默认带本地时区，秒级精度，避免 entry 间出现亚秒抖动
    return datetime.now().astimezone().isoformat(timespec="seconds")


def parse_kv_pairs(raw_pairs):
    # 将形如 ["saved=design.md", "note=expanded"] 解析为 [("saved", "design.md"), ...]
    pairs = []
    for raw in raw_pairs or []:
        if "=" not in raw:
            raise ValueError(f"--kv must be key=value, got: {raw!r}")
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"--kv has empty key: {raw!r}")
        pairs.append((key, value))
    return pairs


def cmd_append(args) -> int:
    tasks_dir = Path(args.tasks_dir).resolve()
    task_dir = tasks_dir / args.task_id
    if not task_dir.is_dir():
        print(f"error: task directory not found: {task_dir}", file=sys.stderr)
        return 1

    try:
        kv_pairs = parse_kv_pairs(args.kv)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not kv_pairs:
        print("error: at least one --kv key=value is required", file=sys.stderr)
        return 2

    if args.timestamp:
        try:
            parse_iso8601(args.timestamp)
        except ValueError:
            print(f"error: --timestamp not ISO 8601: {args.timestamp!r}", file=sys.stderr)
            return 2
        timestamp = args.timestamp
    else:
        timestamp = now_iso()

    skill = args.skill.strip()
    if not skill:
        print("error: --skill must be non-empty", file=sys.stderr)
        return 2

    # 拼接 entry 文本：heading -> kv 行 -> body（可选）
    lines = [f"{HEADING_PREFIX}{timestamp} {EM_DASH} {skill}"]
    for key, value in kv_pairs:
        lines.append(f"{key}: {value}")
    if args.body is not None:
        body_text = args.body.rstrip("\n")
        if body_text:
            lines.append(body_text)
    block = "\n".join(lines) + "\n"

    journal = task_dir / "journal.md"
    if journal.exists() and journal.stat().st_size > 0:
        existing = journal.read_bytes()
        with journal.open("ab") as fh:
            # 保证已有内容以换行收尾，再插入一条空行作为视觉分隔
            if not existing.endswith(b"\n"):
                fh.write(b"\n")
            fh.write(b"\n")
            fh.write(block.encode("utf-8"))
    else:
        journal.write_text(block, encoding="utf-8")

    print(f"appended entry to {journal}")
    return 0


def split_entries(text: str):
    # 只按 "## " 行起始切分，简单稳健
    entries = []
    current = None
    for line in text.splitlines():
        if line.startswith(HEADING_PREFIX):
            if current is not None:
                entries.append(current)
            current = [line]
        else:
            if current is None:
                # 在第一个 heading 之前出现的行（罕见）一起丢弃，避免误归属
                continue
            current.append(line)
    if current is not None:
        entries.append(current)
    return entries


def cmd_read(args) -> int:
    tasks_dir = Path(args.tasks_dir).resolve()
    task_dir = tasks_dir / args.task_id
    if not task_dir.is_dir():
        print(f"error: task directory not found: {task_dir}", file=sys.stderr)
        return 1
    journal = task_dir / "journal.md"
    if not journal.is_file():
        print(f"error: journal.md not found: {journal}", file=sys.stderr)
        return 1

    text = journal.read_text(encoding="utf-8")
    if args.last is None:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
        return 0

    n = args.last
    if n <= 0:
        return 0
    entries = split_entries(text)
    chosen = entries[-n:]
    chunks = []
    for entry_lines in chosen:
        # 去掉 entry 内部尾部空白行，避免拼接出大段空行
        while entry_lines and entry_lines[-1].strip() == "":
            entry_lines.pop()
        chunks.append("\n".join(entry_lines))
    sys.stdout.write("\n\n".join(chunks))
    sys.stdout.write("\n")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Append-only task journal helper")
    sub = parser.add_subparsers(dest="command", required=True)

    ap = sub.add_parser("append", help="append a journal entry")
    ap.add_argument("--tasks-dir", required=True)
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--skill", required=True)
    ap.add_argument(
        "--kv",
        action="append",
        help="key=value pair, may be repeated; at least one is required",
    )
    ap.add_argument("--body", default=None, help="optional free-form body, ≤ 15 lines")
    ap.add_argument(
        "--timestamp",
        default=None,
        help="ISO 8601 timestamp; defaults to local now() with timezone",
    )

    rp = sub.add_parser("read", help="read journal entries")
    rp.add_argument("--tasks-dir", required=True)
    rp.add_argument("--task-id", required=True)
    rp.add_argument("--last", type=int, default=None, help="only print the last N entries")

    args = parser.parse_args(argv)
    if args.command == "append":
        return cmd_append(args)
    if args.command == "read":
        return cmd_read(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
