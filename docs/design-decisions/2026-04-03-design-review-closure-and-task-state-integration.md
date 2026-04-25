# 设计审查闭环与任务状态集成设计决策草案 (Design Review Closure and Task State Integration Decision Draft)

> **状态 (Status):** 已被取代 (superseded)，2026-04-26。
>
> **Superseded by:** [`2026-04-26-task-journal-replaces-task-state-management.md`](./2026-04-26-task-journal-replaces-task-state-management.md)
>
> 本文围绕的"`task-state-management` 作为状态真相"前提已废弃；任务状态改用 `skills/task-journal` 提供的 append-only 约定承载。文中提到的 `docs/tasks/<task-id>/`、`design-state.json`、`status.md` 等工件不再适用。
>
> 本文保留作为历史记录（historical record），便于追溯当时的设计动机与被否决路径。

## 背景与问题 (Background and Problem)

当前仓库已经开始形成两类收敛：

- `task-brief` 向任务归一化（task normalization）收敛
- `design-orchestrator` 向设计阶段内部路由（design-stage routing）收敛
- `design-structure` 已要求设计树（design tree）达到可稳定引用门槛（stable-to-reference threshold）后自动落盘
- `design-readiness-check` 已开始输出显式 readiness（就绪性）结论
- `task-state-management` 已把 `docs/tasks/<task-id>/` 定义为任务状态真相（task state source of truth）

但设计审查（design review）闭环仍然主要依赖自然语言对话推进，典型问题包括：

- 审查结果通常是一段 prose（自然语言段落），不是结构化对象（structured artifact）
- 是否采纳某条审查意见（review finding），缺少稳定记录
- 修订设计树（design revision）往往需要额外口头指令，而不是由状态驱动动作触发
- 设计树已保存、正在审查、需要修订、修订已回写、可进入规划（planning）之间缺少统一状态迁移
- 同一轮任务里，设计正文（authoritative design artifact）、审查结果、修订记录和任务状态分散存在，难以重放（replay）和校验

这会带来三个后果：

- 设计阶段的多轮沟通成本持续偏高
- 审查与修订之间容易出现遗漏、漂移与重复确认
- 即使已有状态脚本，关键推进动作仍可能退化成口头约定

本草案的目的，是把“设计审查闭环（design review closure）”和“任务状态集成（task state integration）”一起定成显式协议，而不是继续依赖技能之间的隐含默契。

## 本次决策 (Decision)

本草案选择把设计审查建模为任务状态机（task state machine）中的显式子流程（explicit subflow），并要求所有高风险状态迁移通过 `task-state-management` 记录为事件（event）。

本草案引入四类一等工件（first-class artifacts）：

1. 设计树（design tree）
2. 审查包（review bundle）
3. 审查项（review finding）
4. 设计修订（design revision）

本草案同时定义三层状态：

1. 任务级状态（task-level state）
2. 工件级状态（artifact-level state）
3. 审查项级状态（finding-level state）

这个决策的核心不是新增更多字段，而是把“设计正文（design content）”“审查结论（review conclusion）”“修订动作（revision action）”“状态推进（state progression）”拆成可追踪的对象与事件。

## 目标 (Goals)

- 让设计进入审查后自动进入可追踪闭环，而不是继续靠聊天推动
- 让每条审查意见具备稳定标识（stable identifier）、处理状态（resolution status）和处理结果（resolution result）
- 让修订动作回写同一个权威设计工件（authoritative design artifact），而不是默认生成漂移副本
- 让 readiness gate（就绪性关口）基于显式状态与事件判断，而不是对对话上下文做隐式推断
- 让后续脚本具备状态重放（state replay）、一致性校验（consistency validation）和审计追踪（auditability）的基础

## 非目标 (Non-Goals)

- 不在本文中定义通用代码审查（code review）协议
- 不在本文中覆盖执行阶段（execution stage）的全部状态细节
- 不替代 `design-decision-audit` 对审查内容本身的判断逻辑
- 不在本文中决定 UI 仪表盘（dashboard）或可视化呈现方式
- 不要求 Phase 1 一次性实现全部脚本与全部状态迁移

## 一等工件 (First-Class Artifacts)

### 1. 设计树 (Design Tree)

设计树是当前任务的权威设计工件（authoritative design artifact），落在 `docs/design-tree/` 下。

建议最小字段：

- `design_id`
- `task_id`
- `path`
- `design_version`
- `design_status`
- `design_doc_status`
- `last_review_bundle_id`
- `last_revision_id`

### 2. 审查包 (Review Bundle)

审查包是一轮设计审查的容器工件（container artifact），用于把同一次审查产生的 finding（审查项）组织在一起。

建议最小字段：

- `review_bundle_id`
- `task_id`
- `design_id`
- `review_target_version`
- `review_status`
- `source`
- `created_at`

### 3. 审查项 (Review Finding)

审查项是一条可以单独处理、单独追踪的设计审查意见。

建议最小字段：

- `finding_id`
- `review_bundle_id`
- `task_id`
- `design_id`
- `target_version`
- `severity`
- `blocking`
- `finding_status`
- `summary`
- `recommended_action`
- `resolution_note`

### 4. 设计修订 (Design Revision)

设计修订表示基于一组审查项对设计树做出的单次修订。

建议最小字段：

- `revision_id`
- `task_id`
- `design_id`
- `base_design_version`
- `result_design_version`
- `revision_status`
- `applied_findings`
- `rejected_findings`
- `deferred_findings`
- `summary`

## 状态模型 (State Model)

本草案不使用单一巨型 `status` 字段，而是采用多轴状态（multi-axis state）模型。原因很直接：任务阶段（phase）、阻塞（blocker）、所有权（ownership）、设计生命周期（design lifecycle）、审查生命周期（review lifecycle）与审查项处理结果（finding resolution）不是同一种维度，混在一起会快速导致状态组合爆炸。

### 任务级状态 (Task-Level State)

#### `task_phase`

`task_phase` 只表达主流程所处的大阶段，不表达阻塞或审查细节。

建议枚举值：

- `intake`
- `design`
- `planning`
- `execution`
- `completed`

#### `blocker_status`

`blocker_status` 表达当前任务是否存在阻塞，而不是把 `blocked` 塞进 `task_phase`。

建议枚举值：

- `clear`
- `blocked`

#### `ownership_status`

`ownership_status` 表达当前任务是否已有明确 owner（所有者）以及是否发生交接（handoff）。

建议枚举值：

- `unowned`
- `owned`
- `handed_off`

#### `readiness_status`

`readiness_status` 用于表达当前阶段是否已经通过进入下一主阶段的显式检查。

建议枚举值：

- `unknown`
- `not_ready`
- `ready`

### 设计工件状态 (Design Artifact State)

#### `design_status`

`design_status` 表达权威设计工件（authoritative design artifact）的生命周期。

建议枚举值：

- `absent`
- `draft`
- `stable_to_reference`
- `in_review`
- `changes_requested`
- `revising`
- `revised`
- `ready_for_planning`
- `superseded`

这些状态的意图如下：

- `absent`：尚不存在权威设计工件
- `draft`：已有设计内容，但尚未达到稳定引用门槛
- `stable_to_reference`：已达到稳定引用门槛并落盘
- `in_review`：已发起审查，当前处于审查中
- `changes_requested`：存在待处理阻塞审查项
- `revising`：正在基于已接受审查项修订设计树
- `revised`：设计修订已完成并回写权威设计工件
- `ready_for_planning`：已通过 readiness gate，可进入规划阶段
- `superseded`：被新版本设计替代，仅保留历史引用价值

#### `design_version`

`design_version` 是整数递增字段，每次成功回写权威设计文件后递增。

本草案要求：

- review bundle（审查包）必须显式绑定 `review_target_version`
- revision（修订）必须显式声明 `base_design_version` 和 `result_design_version`
- finding（审查项）必须知道自己针对哪个设计版本提出

#### `design_doc_status`

`design_doc_status` 是文档面对人类读者的可见状态，不必与 `design_status` 一一对应，但应保持稳定映射。

建议枚举值：

- `draft`
- `ready-for-planning`
- `superseded`

### 审查包状态 (Review Bundle State)

#### `review_status`

`review_status` 表达一整轮设计审查的状态，而不是只看单条 finding。

建议枚举值：

- `idle`
- `open`
- `pending_resolution`
- `revising`
- `resolved`
- `verified`
- `closed`
- `superseded`

这些状态的意图如下：

- `idle`：当前还没有正在进行的审查轮次
- `open`：审查轮次已创建，finding 仍在记录中
- `pending_resolution`：审查结论已形成，等待逐条处理
- `revising`：已进入基于本轮 finding 的修订
- `resolved`：本轮审查项都已得到处理结果
- `verified`：本轮修订结果已被复核确认
- `closed`：本轮审查已正式结束
- `superseded`：被新一轮审查替代，不再作为当前活动审查轮次

### 修订状态 (Revision State)

#### `revision_status`

`revision_status` 表达一次设计修订的生命周期。

建议枚举值：

- `idle`
- `in_progress`
- `applied`
- `verified`
- `abandoned`

这些状态的意图如下：

- `idle`：当前没有活动修订
- `in_progress`：正在根据 accepted finding（已采纳审查项）回写设计树
- `applied`：修订已写回权威设计工件
- `verified`：修订结果已通过复核
- `abandoned`：修订计划被放弃或由后续版本替代

### 审查项状态 (Finding-Level State)

#### `finding_status`

`finding_status` 表达单条审查项的处理进度。

建议枚举值：

- `open`
- `accepted`
- `rejected`
- `deferred`
- `applied`
- `verified`

这些状态的意图如下：

- `open`：已记录，尚未决定如何处理
- `accepted`：决定采纳，但尚未落实到设计正文
- `rejected`：决定不采纳，必须带理由（rationale）
- `deferred`：暂不处理，但保留到后续阶段或后续版本
- `applied`：修订已回写设计正文
- `verified`：回写结果已被复核确认

#### `severity`

`severity` 建议沿用现有审查级别：

- `P0`
- `P1`
- `P2`
- `P3`

#### `blocking`

`blocking` 是显式布尔字段，不应由 `severity` 隐式推出。原因是：

- 不同阶段对阻塞的定义可能不同
- 同一优先级 finding 在不同上下文下可能不具有同样阻塞性
- readiness gate 需要直接判断阻塞项是否已处理，而不是重新解释 prose

## 事件模型 (Event Model)

本草案要求：所有高风险状态迁移都必须记录为结构化事件（structured event），并由 `task-state-management` 统一写入。

每个事件至少应包含：

- `event_id`
- `event_type`
- `task_id`
- `actor`
- `timestamp`
- `correlation_id`

按需追加以下关联字段：

- `design_id`
- `design_version`
- `review_bundle_id`
- `revision_id`
- `finding_id`

### 任务事件 (Task Events)

- `task_created`
- `task_brief_recorded`
- `task_phase_entered`
- `blocker_added`
- `blocker_cleared`
- `ownership_acquired`
- `ownership_transferred`
- `task_completed`

### 设计事件 (Design Events)

- `design_initialized`
- `design_saved`
- `design_updated`
- `design_superseded`

### 审查事件 (Review Events)

- `review_requested`
- `review_bundle_created`
- `review_finding_recorded`
- `review_reopened`
- `review_closed`

### 审查项事件 (Finding Events)

- `finding_accepted`
- `finding_rejected`
- `finding_deferred`
- `finding_applied`
- `finding_verified`

### 修订事件 (Revision Events)

- `design_revision_started`
- `design_revision_applied`
- `design_revision_verified`
- `design_revision_abandoned`

### Readiness 事件 (Readiness Events)

- `readiness_check_started`
- `readiness_check_passed`
- `readiness_check_failed`

## 关键迁移约束 (Key Transition Constraints)

本草案把下面这些规则定义为硬约束（hard constraints），不是建议性提示：

1. `review_requested` 发生前，`design_status` 必须至少为 `stable_to_reference`。
2. `review_bundle_created` 必须绑定 `review_target_version`，不得对“当前设计”这种模糊对象发起审查。
3. `review_finding_recorded` 产生的 finding 必须显式绑定 `review_bundle_id` 和 `target_version`。
4. 如果存在 `blocking=true` 且 `finding_status=open` 的 finding，则 `design_status` 不得进入 `ready_for_planning`。
5. `design_revision_started` 之前，至少要有一条 `accepted` finding，或者存在显式 revision scope（修订范围）记录。
6. `design_revision_applied` 必须回写同一个权威设计文件，不得默认分叉出新的正文文件。
7. `design_revision_applied` 成功后，`design_version` 必须递增，并写明 `base_design_version` 与 `result_design_version`。
8. `readiness_check_passed` 之前，所有阻塞审查项必须处于 `verified`、`rejected`，或被显式允许进入后续阶段的 `deferred`。
9. `blocked` 只能由 `blocker_status` 表达，不能混入 `task_phase`。
10. 所有高风险状态迁移都必须通过 `task-state-management` 写入事件，不得只靠自然语言说明。

## 默认自动化策略 (Default Automation Policy)

本草案区分“默认自动推进（auto-advance）”和“必须人工确认（explicit confirmation）”。

### 默认自动推进的动作 (Auto-Advance Actions)

- 设计树首次达到 stable-to-reference 门槛后自动落盘
- `design_saved` 后自动将 `design_status` 置为 `stable_to_reference`
- 发起审查后自动创建 `review_bundle`
- 记录 blocking finding 后自动将 `design_status` 置为 `changes_requested`
- 修订成功回写后自动刷新 `design_version`、`design_status` 和相关快照

### 必须人工确认的动作 (Explicit Confirmation Actions)

- 将 blocking finding 标记为 `rejected`
- 将 blocking finding 标记为允许带入后续阶段的 `deferred`
- 在存在未解决阻塞项时尝试通过 readiness gate
- 把 `design_status` 从 `revised` 提升为 `ready_for_planning`

## 职责分工 (Responsibility Boundaries)

### `design-structure`

负责：

- 生成初始设计树
- 达到 stable-to-reference 门槛后落盘
- 触发 `design_saved`

不负责：

- 直接修改 review bundle
- 直接处理 finding resolution
- 直接给出 readiness verdict

### `design-decision-audit`

负责：

- 读取设计工件
- 生成 review bundle
- 生成结构化 review finding

不负责：

- 直接修改设计正文
- 直接推进 readiness 状态

### `design-refinement`

负责：

- 基于已接受的 finding 修订设计树
- 生成 revision 记录
- 回写权威设计工件

不负责：

- 在没有显式 resolution 的情况下自行解释 finding
- 在存在未处理阻塞项时擅自宣告 ready

### `design-readiness-check`

负责：

- 基于显式设计状态、审查状态和审查项状态给出 READY / NOT READY 结论
- 更新 readiness 相关状态

不负责：

- 充当通用审查器
- 代替设计修订

### `task-state-management`

负责：

- 写入事件
- 更新状态快照
- 刷新状态视图
- 执行一致性校验
- 提供重放基础

不负责：

- 审查内容判断
- 业务设计决策

## 存储约定 (Storage Contract)

本草案建议最小存储形态如下：

- `docs/tasks/<task-id>/`
- `docs/design-tree/<feature-slug>.md`
- `docs/tasks/<task-id>/reviews/<review-bundle-id>.md`
- `docs/tasks/<task-id>/revisions/<revision-id>.md`

这里的原则是：

- 设计正文仍以 `docs/design-tree/` 下的文件为单一权威正文（single authoritative design body）
- review 和 revision 工件属于任务态附属工件（task-scoped supporting artifacts）
- 任务状态真相仍在 `docs/tasks/<task-id>/`

## 分期落地建议 (Phased Rollout Recommendation)

本草案定义的是完整协议（full protocol），不要求一次性全部实现。

### Phase 1

优先落地以下内容：

- `task_phase`
- `blocker_status`
- `design_status`
- `design_version`
- `review_status`
- `finding_status`
- 核心事件写入
- 关键迁移校验

### Phase 2

后续再补：

- `ownership_status`
- `revision_status`
- 更强的 replay（重放）能力
- 更强的一致性校验与恢复逻辑

这样做的目的，是先把高风险口头约定替换成显式协议，再逐步提高自动化与恢复能力。

## 反模式与被拒绝方案 (Anti-Patterns and Rejected Alternatives)

本草案明确反对下面几种方向：

- 继续把设计审查闭环寄托在自由对话中
- 让 `design-decision-audit` 直接修改设计正文
- 让 `design-refinement` 在没有显式 resolution 的情况下“自行理解”审查意见
- 让多个 skill 直接写 `docs/tasks/<task-id>/`
- 通过不断增加 prose 字段来替代状态机
- 用单一全能 `status` 字段表达任务阶段、阻塞、审查和修订

这些做法的问题，不是它们一定立刻失效，而是它们会持续侵蚀“状态真相（state truth）”“事件可追踪性（event traceability）”和“脚本可维护性（script maintainability）”。

## 开放问题 (Open Questions)

这份草案仍有几个后续问题没有在本文中彻底定死：

- `review bundle` 和 `revision` 的物理文件格式是否最终应为 Markdown（Markdown）加 frontmatter（frontmatter），还是 JSON（JavaScript Object Notation）主存储
- `deferred` finding 在什么条件下允许越过 readiness gate
- `rejected` blocking finding 是否必须附带固定结构的 rationale
- `review_status=resolved` 与 `review_status=verified` 之间是否需要更明确的界限说明
- `ownership_status` 在多 agent（multi-agent）协作下是否还需要补充 owner identity（所有者标识）约束

## 当前结论 (Current Conclusion)

本草案的结论很集中：

- 设计审查必须成为显式子流程，而不是纯对话约定
- 设计树、审查包、审查项和设计修订应成为一等工件
- 任务状态应采用多轴模型，而不是单一全能状态
- 所有高风险状态迁移都必须通过 `task-state-management` 统一写事件
- readiness gate 必须基于显式状态与显式事件，而不是对上下文做口头推断

如果后续实现要偏离这些结论，最好先更新这份设计决策，而不是在单个 skill 或单个脚本里悄悄改变协议边界。
