# 脚本清单 (Script Catalog)

## Phase 1 脚本 (Phase 1 Scripts)

- `common.py`：仓库根目录、任务目录、JSON 读写与原子写入辅助
- `create_task.py`：创建任务目录、初始状态文件、首条任务事件与初始 ownership 审计事件
- `append_event.py`：追加事件到 `events.jsonl`
- `update_state.py`：更新阶段状态快照
- `handoff_state.py`：记录阶段交接并写入下游版本锚点
- `add_blocker.py`：向阶段状态写入 blocker 并追加阻塞事件
- `clear_blocker.py`：清除 blocker 并在无剩余阻塞时恢复阶段推进
- `revalidate_state.py`：将 `stale` 状态重新标记为 `valid`
- `complete_task.py`：在满足前提时把执行态标记为 `completed`
- `acquire_ownership.py`：获取或续租任务 ownership
- `transfer_ownership.py`：显式转移任务 ownership
- `replay_events.py`：将支持的事件类型重放回状态快照，并在需要时重建 `ownership.json`
- `refresh_status_view.py`：只根据 `states/*.json` 刷新 `status.md`
- `validate_state.py`：校验事件、快照与视图的一致性

## 约束 (Constraints)

- 这些脚本由 `task-state-management` 拥有
- 其他 skill 只能调用，不得复制维护
- Phase 1 已覆盖任务创建、事件追加、快照更新、阶段交接、blocker 生命周期、再验证、完成态、ownership、事件重放、状态视图刷新与状态校验
- 所有写脚本默认都要通过 ownership 校验
- `validate_state.py` 的结果状态至少包括 `ok`、`warning`、`recovery_needed`、`invalid`
