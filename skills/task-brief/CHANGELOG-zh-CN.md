# 变更日志 (Changelog)

## 2026-03-30

- 初始版本，新增 `task-brief` 技能
- 将触发条件（trigger conditions）从“用户显式提到 ‘task brief’”扩展为“任何复杂、模糊、多步骤、跨领域或适合交接的请求”
- 建立与模型无关的 Task Brief 输出协议（8 个字段）
- 明确区分三类复杂度分层：`Direct`、`Clarify`、`Structured`
- 新增针对 “solution-as-goal” 的检测逻辑，用于处理用户把技术方案误当成目标的问题
- 新增针对 “symptom-as-goal” 的检测逻辑，用于处理用户把症状误当成目标的问题
- 新增针对 “scope anomaly” 的检测逻辑，用于识别范围边界明显异常的请求
- 为含糊意图（ambiguous intent）加入明确协议：要求写出 `Interpretation A` 与 `Interpretation B`
- 新增 “Compression Rules” 章节，规范如何从原始请求压缩为可执行简报
- 扩展 execution modes：加入 `structured-handoff` 与 `decompose`
- 增加用于复杂任务拆解的 “Sub-Tasks” 与依赖 DAG 约定
- 加入 5 个完整示例，覆盖：
  - Direct request
  - Missing parameter
  - Multi-component decomposition
  - Ambiguous intent
  - Inaccurate goal
- 增加 Acceptance Criteria，用于判断 task brief 是否足够好
