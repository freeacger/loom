# 参考说明 (Reference)

## 目录约定 (Directory Conventions)

```text
skills/task-state-management/
  SKILL.md
  REFERENCE.md
  scripts/
    README.md
    common.py
    create_task.py
    append_event.py
    update_state.py
    handoff_state.py
    add_blocker.py
    clear_blocker.py
    revalidate_state.py
    complete_task.py
    acquire_ownership.py
    transfer_ownership.py
    replay_events.py
    refresh_status_view.py
    validate_state.py
```

```text
docs/
  tasks/
    <task-id>/
      status.md
      events.jsonl
      states/
        design-state.json
        plan-state.json
        execution-state.json
```

## `task-id` 规则 (Task ID Rule)

- 格式：`YYYYMMDD-<task-name>-<2位随机字符>`
- `<task-name>` 使用稳定、可读的 `kebab-case`
- 同一仓库内必须唯一

## 脚本接口约定 (Script Interface Conventions)

- 输入优先使用显式命令行参数（CLI arguments）
- 复杂结构化输入可使用 JSON 文件路径
- 输出默认写到标准输出（stdout）
- 输出只允许单个 JSON 对象
- 错误写到标准错误（stderr），并返回非零退出码
- 任何会修改状态的脚本都必须显式接收 `task-id`
- 除 `validate_state.py` 外，任何会写入任务状态的脚本都必须显式接收 `owner_id`
- `create_task.py` 必须返回 `task_id`、`event_id`、`event_seq`、`changed_files` 和 `result`
- `result` 至少应包含任务目录、三份状态文件路径、`status.md` 路径与 `events.jsonl` 路径
- `create_task.py` 必须创建首个 `ownership.json`
- `create_task.py` 必须追加初始 `ownership_acquired` 审计事件，确保初始 ownership 可追溯、可重放
- `acquire_ownership.py` 必须返回当前 owner、ownership 文件位置与 lease 过期时间
- `transfer_ownership.py` 必须返回原 owner 与新 owner 摘要
- 事件追加脚本必须返回本次写入的事件标识与顺序号
- `append_event.py` 的扩展 payload 不得覆盖保留事件字段，例如 `event_id`、`event_seq`、`task_id`、`phase`、`timestamp`、`source`、`summary`、`type`
- 状态更新脚本必须返回更新后的 `state_version` 与 `last_applied_event_id`
- `handoff_state.py` 必须支持 `design -> planning` 与 `planning -> execution`，并返回上游/下游状态文件、交接事件标识与下游版本锚点
- `add_blocker.py` 必须返回新增 blocker 的 `blocking_issue_id`、事件标识与更新后的 `state_version`
- `clear_blocker.py` 必须返回被清除的 blocker 标识、当前 `lifecycle_state` 与更新后的 `state_version`
- `revalidate_state.py` 必须只接受 `stale` 状态，并返回新的 `validity_state`
- 对 `plan` 与 `execution`，`revalidate_state.py` 必须拒绝回退 `source_*_version`，并要求 `against_source_version` 与真实上游 `meta.state_version` 一致
- `complete_task.py` 必须只操作 `execution-state.json`，并在默认情况下要求 `validity_state = valid` 且 blocker 为空
- `refresh_status_view.py` 必须只读取 `states/*.json`，并将三份状态快照汇总写入 `status.md`
- `refresh_status_view.py` 的输出必须包含 `task_id`、`changed_files` 和 `result.summary`
- `replay_events.py` 必须只重放显式支持的事件类型；不支持的事件必须失败而不是静默跳过
- `replay_events.py --include-ownership` 必须支持从 ownership 审计事件重建 `ownership.json`
- `validate_state.py` 的输出必须包含 `task_id`、`changed_files` 和 `result.status`
- `validate_state.py` 的 `result.status` 至少应支持 `ok`、`warning`、`recovery_needed`、`invalid`

## Phase 1 边界 (Phase 1 Boundary)

- 已覆盖任务创建、事件追加、状态更新、阶段交接、blocker 生命周期、再验证、完成态、ownership、事件重放、状态视图刷新、状态校验
- memory 系统与更复杂的历史经验能力仍留在后续切片
- 脚本默认语言是 Python 3.11+
- shell 只允许作为薄包装，不承载核心状态逻辑
