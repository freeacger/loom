#!/usr/bin/env python3
# task-journal 漂移检测器：扫描 .agents/tasks/ 报告 error / warn
# 严重度规则：
#   error  - heading / kv / 保留 key 格式损坏；时间戳无法解析；缺少 brief.md
#   warn   - body 超长；done 之后再追加；journal.md 缺失；超长 stale（暂不实现）
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

EM_DASH = "—"
# 头行：## <timestamp> — <skill>
HEADING_RE = re.compile(rf"^## (\S.+?) {EM_DASH} (\S.+?)\s*$")
# kv 行：key 是 ASCII kebab/snake；冒号后允许任意值（含空值，由保留 key 校验拒绝）
KV_RE = re.compile(r"^([a-z][a-z0-9_-]*):\s*(.*)$")

RESERVED_KEYS = {"saved", "decision", "readiness", "blocker", "done"}
READINESS_VALUES = {"ready", "not-ready"}
BODY_LIMIT = 15


def parse_iso8601(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)


class Report:
    # 收集所有 error/warn，最后统一打印；避免顺序耦合
    def __init__(self):
        self.errors = []
        self.warnings = []

    def err(self, where: str, message: str) -> None:
        self.errors.append((where, message))

    def warn(self, where: str, message: str) -> None:
        self.warnings.append((where, message))

    def flush(self) -> None:
        for where, message in self.errors:
            print(f"error: {where}: {message}")
        for where, message in self.warnings:
            print(f"warn: {where}: {message}")


def parse_entries(text: str):
    # 把 journal.md 的全文切成 [{heading_raw, line_no, kvs, body}]
    raw_entries = []
    current = None
    line_no = 0
    for line in text.splitlines():
        line_no += 1
        if line.startswith("## "):
            if current is not None:
                raw_entries.append(current)
            current = {
                "heading_raw": line,
                "line_no": line_no,
                "_lines": [],
            }
        else:
            if current is None:
                # heading 之前的内容不属于任何 entry，忽略
                continue
            current["_lines"].append(line)
    if current is not None:
        raw_entries.append(current)

    for entry in raw_entries:
        kvs = []
        body = []
        in_kv_section = True
        for line in entry["_lines"]:
            if in_kv_section:
                m = KV_RE.match(line)
                if m:
                    kvs.append((m.group(1), m.group(2).strip()))
                    continue
                # 第一条非 kv 行即进入 body 段
                in_kv_section = False
            body.append(line)
        entry["kvs"] = kvs
        entry["body"] = body
        del entry["_lines"]
    return raw_entries


def lint_task(task_dir: Path, report: Report) -> None:
    name = task_dir.name

    brief = task_dir / "brief.md"
    if not brief.is_file():
        report.err(name, "brief.md missing")

    journal = task_dir / "journal.md"
    if not journal.is_file():
        # 任务刚被 task-brief 创建、还没有里程碑写入是正常态，但也提示一下
        report.warn(name, "journal.md missing")
        return

    text = journal.read_text(encoding="utf-8")
    entries = parse_entries(text)
    if not entries:
        report.warn(name, "journal.md has no entries")
        return

    done_seen = False
    for idx, entry in enumerate(entries, start=1):
        eid = f"{name}#entry{idx}"
        heading = entry["heading_raw"]
        match = HEADING_RE.match(heading)
        heading_ok = False
        if match is None:
            report.err(eid, f"malformed heading: {heading!r}")
        else:
            ts_str = match.group(1)
            try:
                parse_iso8601(ts_str)
                heading_ok = True
            except ValueError:
                report.err(eid, f"unparseable timestamp: {ts_str!r}")

        kvs = entry["kvs"]
        if not kvs:
            # heading 格式即便错了，也仍提示缺 kv 行，方便修复定位
            report.err(eid, "no key:value line under heading")

        for key, value in kvs:
            if key in RESERVED_KEYS:
                if value == "":
                    report.err(eid, f"reserved key {key!r} has empty value")
                if key == "readiness" and value != "" and value not in READINESS_VALUES:
                    report.err(
                        eid,
                        f"readiness must be 'ready' or 'not-ready', got {value!r}",
                    )

        body_lines = [line for line in entry["body"] if line.strip() != ""]
        if len(body_lines) > BODY_LIMIT:
            report.warn(
                eid,
                f"body exceeds {BODY_LIMIT} lines (got {len(body_lines)}); move long content to artifacts/",
            )

        has_done_kv = any(key == "done" for key, _ in kvs)
        if done_seen and not has_done_kv:
            report.warn(
                eid,
                "entry written after a 'done' entry — looks like reopen; check task lifecycle",
            )
        if has_done_kv:
            done_seen = True

        # 仅在 heading_ok 时不再做时间戳相关推断；其他严重度交给上面的 kv 检查
        _ = heading_ok


def iter_tasks(tasks_dir: Path, only: str | None):
    # 跳过非目录与隐藏目录（例如 .current 文件、可能的 .git 等）
    if only is not None:
        candidate = tasks_dir / only
        if candidate.is_dir():
            yield candidate
        return
    for entry in sorted(tasks_dir.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        yield entry


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Lint .agents/tasks/ for journal drift")
    parser.add_argument("--tasks-dir", required=True)
    parser.add_argument(
        "--task-id",
        default=None,
        help="lint only this task instead of the whole tree",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat warnings as errors (exit 1 on any warning)",
    )
    args = parser.parse_args(argv)

    tasks_dir = Path(args.tasks_dir).resolve()
    if not tasks_dir.is_dir():
        print(f"error: tasks-dir not found: {tasks_dir}", file=sys.stderr)
        return 1

    if args.task_id is not None:
        if not (tasks_dir / args.task_id).is_dir():
            print(
                f"error: task directory not found: {tasks_dir / args.task_id}",
                file=sys.stderr,
            )
            return 1

    report = Report()
    task_count = 0
    for task_dir in iter_tasks(tasks_dir, args.task_id):
        task_count += 1
        lint_task(task_dir, report)

    report.flush()

    if task_count == 0 and args.task_id is None:
        # 空 tasks-dir 是合法的初始态
        print("✓ no tasks under tasks-dir")
        return 0

    if report.errors:
        print(
            f"✗ {len(report.errors)} error(s), {len(report.warnings)} warning(s) across {task_count} task(s)"
        )
        return 1
    if args.strict and report.warnings:
        print(
            f"✗ {len(report.warnings)} warning(s) under --strict across {task_count} task(s)"
        )
        return 1
    if report.warnings:
        print(f"✓ no errors, {len(report.warnings)} warning(s) across {task_count} task(s)")
    else:
        print(f"✓ clean across {task_count} task(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
