# 变更日志 (Changelog)

## 2026-04-03

- 收敛 `task-brief` 的职责边界，只保留任务归一化（task normalization）、澄清问题（Clarifying Question）与是否需要设计阶段（Needs Design）判断
- 删除 `Execution Mode`、`structured-handoff`、`decompose`、`Core Questions`、`Sub-Tasks` 与 DAG 约定
- 新增 `Needs Design` 字段，并把问题收敛为单个 `Clarifying Question`
- 将输出字段顺序调整为更适合快速扫读的版本
- 明确展示规则：英文 canonical 模板保持英文标题，中文响应可使用双语标题
- 移除“默认先搜索代码库再写 brief”的规则
- 同步更新示例、评测（evals）与相关引用

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
