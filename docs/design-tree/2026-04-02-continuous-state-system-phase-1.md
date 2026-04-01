# 连续状态系统 Phase 1 设计树 (Continuous State System Phase 1 Design Tree)

## 问题 (Problem)

当前设计树系列技能已经在“概念路由（concept routing）”上形成较清楚的能力边界，但对技能使用方而言，仍缺少一套跨 `design -> planning -> execution` 连续推进的显式状态系统。缺口不在单一 `writing-plans` 技能，而在于：

- 缺少可依赖的阶段状态（state）分层
- 缺少稳定的阶段交接（handoff）与版本锚点（version anchors）
- 缺少基于事件流（event stream）的恢复与一致性校验
- 历史经验（historical learnings）虽已识别为独立问题域，但不应进入 Phase 1 实现范围

本设计文档的目标，是把当前对话中已收敛的设计状态正式落盘，作为进入实现规划（implementation planning）前的设计树工件。

## 范围 (Scope)

### 包含 (Included)

- 面向技能使用方的连续状态系统（continuous state system）Phase 1 边界
- 主树、子树 A、子树 B 的问题域划分
- `docs/tasks/<task-id>/` 目录布局
- `design-state.json`、`plan-state.json`、`execution-state.json` 的状态分层
- `events.jsonl`、`status.md` 的职责边界
- 事件优先（event-first）的状态收敛顺序
- stale / recovery / invalid 的状态有效性（validity）规则
- Phase 1 与 Phase 2 的切分

### 不包含 (Excluded)

- `docs/memory/` 下正式历史经验系统的实现
- `memory-curation` 技能的详细输入输出契约
- memory 检索、排序、注入、淘汰的自动化实现
- 跨仓库或跨项目共享 memory
- UI dashboard 或可视化管理界面

## 假设 (Assumptions)

- 本设计面向“采用这些技能的使用方”，不是仅服务本仓库自身维护流程
- Phase 1 的目标是先跑通任务状态系统，不追求一次性覆盖完整历史经验系统
- `status.md` 是人读视图（human-readable view），不是机器真相（machine truth）

## 强制规则 (Mandatory Rules)

### 状态根目录规则 (State Root Rule)

- `docs/` 是唯一合法状态根目录（the only valid state root）
- 所有任务状态、事件流、记忆工件都必须位于 `docs/` 下
- 技能不得将这些工件写入仓库其他目录
- 若运行环境不允许使用 `docs/`，则该环境不在支持范围内

### 支持前提 (Support Preconditions)

- 仓库根目录可写
- `docs/` 可创建或可写
- 使用方接受 `docs/` 下出现状态工件与记忆工件

## 主树 (Primary Design Tree)

```text
design_tree
├── 1. 问题定义 (Problem Definition)
│   ├── 1.1 使用方可见能力边界 ✓
│   └── 1.2 非目标与排除项 ✓
├── 2. 范围与边界 (Scope and Boundaries)
│   ├── 2.1 共享契约 vs 本地适配 ✓
│   └── 2.2 单任务状态 vs 历史经验 ✓
├── 3. 状态层模型 (State Layer Model)
│   ├── 3.1 design_state ✓
│   ├── 3.2 plan_state ✓
│   ├── 3.3 execution_state ✓
│   └── 3.4 historical_learnings ✓
├── 4. 阶段路由规则 (Stage Routing Rules)
│   ├── 4.1 design -> planning ✓
│   ├── 4.2 planning -> execution ✓
│   └── 4.3 execution -> learning capture ✓
├── 5. Handoff 形式 (Handoff Forms)
│   ├── 5.1 摘要 + 引用 + 必要字段 ✓
│   ├── 5.2 版本锚点（version anchors）✓
│   └── 5.3 失效与再验证（stale / revalidation）✓
├── 6. 持久化策略 (Persistence Strategy)
│   ├── 6.1 docs/tasks 与 docs/memory 布局 ✓
│   ├── 6.2 事件优先、状态收敛（event-first）✓
│   └── 6.3 使用方依赖保证 ✓
├── 7. 可观测性与状态视图 (Observability and State Views)
│   ├── 7.1 status.md 作为人读视图 ✓
│   └── 7.2 真相裁定与恢复（truth / recovery）✓
├── 8. 历史经验接口 (Historical Learning Interface)
│   ├── 8.1 intake / learnings 分层 ✓
│   ├── 8.2 记忆分类表（memory taxonomy）✓
│   ├── 8.3 准入标准（admission criteria）✓
│   ├── 8.4 记忆沉淀技能（memory-curation）[OPEN]
│   └── 8.5 注入触发策略（injection trigger policy）✓
└── 9. 验证与退出条件 (Validation and Exit Conditions)
    ├── 9.1 状态一致性校验 ✓
    └── 9.2 子树派生条件 ✓
```

## 核心状态对象 (Core State Objects)

### 设计状态 (Design State)

`design_state` 持有设计阶段的权威信息，包括问题定义、范围、设计树、开放分支、决策节点、风险、验证要求与设计阶段状态。它不承担执行事实与运行期进度。

### 计划状态 (Plan State)

`plan_state` 持有实现计划（implementation plan）的拆分结果、依赖顺序、验证计划与进入执行前的阻塞项。它不复制完整设计树，只引用设计状态及其版本锚点。

### 执行状态 (Execution State)

`execution_state` 持有执行事实（execution facts），包括当前执行单元、已完成单元、活跃发现、阻塞项、最新验证结果与执行阶段状态。它不能反向改写设计或计划的权威内容，只能通过事件反馈推动再验证。

### 历史经验 (Historical Learnings)

`historical_learnings` 已被确认为独立问题域，但不进入 Phase 1 实现范围。Phase 1 只保留其接口与挂点，不实现完整生命周期。

## 目录布局 (Directory Layout)

Phase 1 约定的任务目录如下：

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

目录职责如下：

- `events.jsonl`：历史真相（historical truth）
- `states/*.json`：当前真相（current truth）
- `status.md`：派生视图（derived view）

历史经验相关目录在 Phase 2 中再启用：

```text
docs/
  memory/
    intake/
      learnings.jsonl
    learnings/
      <memory-id>.json
```

## 提交策略 (Commit Policy)

### `docs/tasks/`

- `docs/tasks/<task-id>/status.md`、`events.jsonl`、`states/*.json` 属于任务级状态工件（task-scoped state artifacts）
- 默认视为应提交工件（commit-worthy artifacts），因为它们共同定义了任务的当前真相、历史事件与恢复基础
- 如果某个使用方环境不希望将这些工件提交到版本控制（version control），则该环境不在当前 Phase 1 设计的默认支持范围内

### `docs/memory/`

- `docs/memory/intake/*.jsonl` 与 `docs/memory/learnings/*.json` 在 Phase 2 中默认也视为应提交工件
- `intake` 记录原始候选经验流，`learnings` 记录正式记忆对象，两者都属于系统可追溯性的组成部分
- 当前设计不提供 `.gitignore` 模式、临时目录回退模式或仓库外 memory 存储模式

## 状态契约 (State Contracts)

### 双轴状态模型 (Two-Axis Status Model)

所有阶段状态文件共享统一 `status` 子对象，并拆成两个轴：

- 生命周期状态（lifecycle_state）
  - `draft|in_progress|blocked|ready|completed|abandoned`
- 有效性状态（validity_state）
  - `valid|stale|recovery_needed|invalid`

最小形状如下：

```json
{
  "status": {
    "phase": "design|planning|execution",
    "lifecycle_state": "draft|in_progress|blocked|ready|completed|abandoned",
    "validity_state": "valid|stale|recovery_needed|invalid",
    "blocking_issues": [],
    "updated_at": "",
    "owner": ""
  }
}
```

### 版本锚点 (Version Anchors)

每个状态文件至少包含：

```json
{
  "meta": {
    "state_version": 0,
    "last_applied_event_id": ""
  }
}
```

下游状态必须额外记录上游引用与版本锚点，例如：

```json
{
  "source_design_ref": "",
  "source_design_version": 0,
  "source_design_event_id": ""
}
```

```json
{
  "source_plan_ref": "",
  "source_plan_version": 0,
  "source_plan_event_id": ""
}
```

## 核心流程 (Core Flows)

### 事件优先收敛流程 (Event-First Convergence Flow)

统一写入顺序固定为：

```text
append event -> update state snapshot -> refresh status.md
```

解释如下：

- 先追加事件，确保变化先进入事件流
- 再更新状态快照，形成当前真相
- 最后刷新 `status.md`，提供人读总览

### 阶段交接流程 (Phase Handoff Flow)

Phase 1 只覆盖两段 handoff：

1. `design -> planning`
2. `planning -> execution`

每次合法 handoff 都必须留下：

- 上游状态引用
- 上游版本号
- 上游事件锚点
- `handoff_completed` 事件

## 真相裁定与恢复 (Truth Order and Recovery)

### 真相裁定顺序 (Truth Order)

冲突时按以下顺序裁定：

1. `events.jsonl` 负责解释“发生了什么”
2. `states/*.json` 负责解释“现在是什么”
3. `status.md` 负责解释“现在最值得人看什么”

### 恢复规则 (Recovery Rules)

- 事件已写入但快照未更新：
  - 进入 `recovery_needed`
  - 通过事件重放（replay）修复快照
- 快照已更新但 `status.md` 过期：
  - 只刷新 `status.md`
- 事件链与快照冲突：
  - 进入 `invalid`
  - 禁止静默继续自动推进

## 子树 A：跨阶段推进工作流 (Child Tree A: Cross-Stage Progression Workflow)

```text
design_tree
├── 1. 阶段定义 (Stages) ✓
├── 2. 输入与输出 (Inputs and Outputs) ✓
├── 3. 状态转移规则 (State Transition Rules) ✓
├── 4. Blocker 与阻力处理 (Blocker Handling) ✓
├── 5. Readiness 与质量门禁 (Readiness and Quality Gates) ✓
├── 6. 恢复与重试路径 (Recovery and Retry Paths) ✓
├── 7. 用户状态视图 (User-Facing Status Views) ✓
└── 8. 验证 (Validation) ✓
```

该子树负责：

- 阶段推进
- blocker / recovery
- readiness / progress 视图
- 再验证入口（revalidation entry points）

它不拥有 memory 生命周期与 memory 注入能力。

## 子树 B：历史经验回注系统 (Child Tree B: Historical Learning Injection System)

```text
design_tree
├── 1. 经验来源 (Learning Sources) ✓
├── 2. 经验分类与准入 (Taxonomy and Admission) ✓
├── 3. intake 与正式记忆分层 (Intake vs Curated Memory) ✓
├── 4. 注入触发策略 (Injection Trigger Policy) ✓
├── 5. 注入记录与采纳边界 (Injection vs Apply Boundary) ✓
├── 6. 记忆沉淀技能（memory-curation）[OPEN]
└── 7. 验证与淘汰 (Validation and Deprecation) ✓
```

该子树已完成问题域边界定义，但不进入 Phase 1 实现。`memory-curation` 被明确降级为子树中的待完成能力项（pending capability），而不是新的顶层状态层。

## 使用方依赖保证 (User-Facing Reliability Guarantees)

Phase 1 向使用方承诺以下最小保证：

- 一旦事件成功追加到 `events.jsonl`，该变化最终应可收敛到状态快照
- 每次合法 handoff 都可追溯到上游引用与版本锚点
- 若事件与快照不一致，系统必须显式进入 `recovery_needed` 或 `invalid`
- `status.md` 允许短暂落后，但必须可由快照重建

Phase 1 明确不保证：

- memory 自动沉淀
- memory 自动注入与排序
- 跨任务自动经验共享
- stale 自动恢复为 valid

## 已冻结决策 (Frozen Decisions)

- Phase 1 只实现 `docs/tasks/` 下的连续状态系统
- Phase 2 再引入 `docs/memory/` 与 `memory-curation`
- 当前任务状态采用 3 个独立 JSON，而不是单一 `state.json`
- `status.md` 不是机器真相
- `events.jsonl` 是 append-only 事件流
- stale 只能通过当前阶段 owner 的再验证清除
- `injected` 与 `applied` 必须严格分离

## Phase 切分 (Phase Split)

### Phase 1 (MVP)

Phase 1 只实现任务状态系统最小闭环：

- `docs/tasks/<task-id>/states/*.json`
- `events.jsonl`
- `status.md`
- handoff、版本锚点、stale / recovery / invalid
- 基本一致性校验与 revalidation

### Phase 2

Phase 2 再实现历史经验系统：

- `docs/memory/intake/learnings.jsonl`
- `docs/memory/learnings/<memory-id>.json`
- `memory-curation`
- memory lifecycle
- learning injection / apply

## Readiness 结论 (Readiness Verdict)

本设计在主树与两个子树上已达到“停止继续扩树”的程度。为进入实现规划，关键切分已经完成：

- 主树已基本闭合
- 子树 A 已具备进入实现规划的边界清晰度
- 子树 B 已完成问题域收敛，但整体推迟到 Phase 2

因此，本设计文档的最终结论是：

- **Phase 1 设计已准备进入实现规划（planning-ready）**
- **Phase 2 记忆系统仍保留为后续阶段设计与实现事项**

## 下一步 (Next Step)

下一步应基于本文档进入 `writing-plans`，为 Phase 1 产出实施计划（implementation plan），而不是继续扩展设计树。
