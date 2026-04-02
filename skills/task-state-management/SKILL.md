# 任务状态管理 (Task State Management)

## 职责 (Responsibilities)

`task-state-management` 负责维护 `docs/tasks/<task-id>/` 下的任务状态真相。
它是 Phase 1 状态维护脚本的单一真相（single source of truth），只负责
确定性状态维护，不负责业务决策。

## 适用范围 (Scope)

- 创建任务状态目录与初始状态文件
- 追加事件流（event stream）
- 更新设计、计划、执行三阶段状态快照
- 记录阶段交接（handoff）
- 维护 blocker 的新增与清除
- 执行 `stale -> valid` 的再验证（revalidation）
- 在满足前提时写入完成态（completion）
- 获取与转移任务 ownership
- 在支持的事件类型上执行状态与 ownership 重放（replay）
- 刷新 `status.md`
- 校验状态一致性

## 唯一写入口 (Single Write Path)

- 只有本 skill 目录下的 `scripts/` 可以直接写入 `docs/tasks/<task-id>/`
- 其他 skill 只能调用这些脚本，不得直接改写状态工件
- 所有高风险状态维护动作都应走脚本，不应靠自然语言约定

## Phase 1 脚本范围 (Phase 1 Script Scope)

Phase 1 当前覆盖以下状态维护脚本：

- `create_task.py`
- `append_event.py`
- `update_state.py`
- `handoff_state.py`
- `add_blocker.py`
- `clear_blocker.py`
- `revalidate_state.py`
- `complete_task.py`
- `acquire_ownership.py`
- `transfer_ownership.py`
- `replay_events.py`
- `refresh_status_view.py`
- `validate_state.py`

## 不负责的内容 (Non-Responsibilities)

- `docs/memory/` 的正式历史经验系统
- 业务规划与设计决策
- UI 仪表盘或可视化管理界面
