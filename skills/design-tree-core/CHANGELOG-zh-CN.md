# 变更日志 (Changelog)

## v0.1.0 — 初始版本 (Initial version)

- 引入 `design-tree-core`，作为 design-tree 技能家族的共享治理核心
- 定义共享 design-tree 行为所需的 admission、eviction、derivation 与 anti-bloat 规则
- 新增一个运行时发布的 `REFERENCE.md`，让共享规则能通过 GitHub 与 skills.sh 分发

## v0.2.0 — 破坏性契约升级 (Breaking contract rollout)

- 将 `design_target_type` 设为必需的共享 `design_state` 字段
- 定义共享目标类型词汇表：`system`、`workflow`、`methodology`、`framework`
- 将整个家族收敛到纯 `design_state` 输出契约
- 明确默认文件持久化不是共享 design-tree 行为
- 为 design refinement 与 readiness 增加目标类型特定的完成标准
