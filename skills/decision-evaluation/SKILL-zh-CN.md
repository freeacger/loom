---
name: decision-evaluation
description: "对单个明确的设计决策节点（design decision node）进行评估，比较真实可行的选项，并给出带有清晰权衡的推荐。当设计里已经出现具体选择题，例如架构风格、状态管理、认证模型、存储模式、同步策略、多 agent 协调模式、语言或运行时、UI 框架、数据层库、工具选型时使用。本技能适用于边界明确的决策比较，不适用于广义设计探索、整体系统拆解或最终就绪性审查。"
---

# 决策评估 (Decision Evaluation)

## 概览 (Overview)

这个技能一次只评估一个明确的设计决策（design decision）。

它不负责发现整棵设计树，也不负责验证整体是否准备就绪。它的职责是：在一个边界明确的决策节点上比较真实可行的选项，并给出有根据的推荐。

## 何时使用 (When to Use)

在以下情况下使用本技能：

- 设计中已经出现了一个具体的决策节点
- 用户本质上在问“这些方案里我们该选哪一个？”
- 这个决策会实质性影响架构、实现路径、兼容性、成本或运行风险

典型示例包括：

- 认证模型（auth model）
- 协调模式（coordination pattern）
- 存储策略（storage strategy）
- 同步模型（sync model）
- 状态管理方式（state management approach）
- 重试或执行模型（retry or execution model）
- 工作流回滚策略（workflow rollback policy）
- 工作流审批策略（workflow approval strategy）
- 方法论停机条件（methodology stop condition）
- 方法论证据阈值（methodology evidence threshold）
- 框架路由规则（framework routing rule）
- 框架交接契约（framework handoff contract）
- 语言或运行时选择（language or runtime selection）
- UI 框架选择（UI framework selection）
- 数据层库选择，例如 ORM、query builder、validation
- 工具选型，例如 bundler、linter、test runner、CI 平台

以下情况不要使用本技能：

- 设计树尚未成形
- 任务仍属于广义设计探索
- 主要需求是深化设计，而不是做边界明确的比较
- 任务是最终的 readiness gate

## 约束收集 (Constraint Gathering)

当决策涉及技术选型（语言、框架、库、工具）时，在正式比较前先完成这一步。

要求用户确认：

1. 硬约束（hard constraints）：现有技术栈、许可证要求、预算上限、部署环境限制。
2. 偏好或已排除的选项。
3. 评估维度的优先级，例如 performance > ecosystem > learning curve。
4. 必需能力（must-have requirements），例如 TypeScript 支持、SSR 能力、plugin system。

根据已确认的约束过滤候选项。只有可行选项才能进入正式比较。

输出内容：已确认的约束 + 过滤后的候选列表。

如果决策不是技术选型，但仍然是一个边界明确的选择题，不要强行套用技术选型问题。
此时应确认决策边界、真实备选项，以及这个工作流、方法论或框架选择真正关心的维度。

## 核心职责 (Core Responsibilities)

你的职责是：

1. 准确定义决策问题。若是技术选型，基于“约束收集”阶段确认的约束来定义问题。
2. 将工作严格限制在一个明确的决策节点内。
3. 在确实存在真实选项时，给出 3 到 4 个选项。
4. 清晰且具体地比较各项权衡。
5. 推荐一个方案；必要时也可以推荐一个有充分理由的组合方案。
6. 解释为什么在当前上下文里不优先选择被拒绝的方案。
7. 将结果记录为可复用的决策记录（decision record）。

## 比较标准 (Comparison Standard)

使用对该决策真正重要的维度来比较选项。常见维度包括：

- 实现复杂度（implementation complexity）
- 与当前系统的兼容性（compatibility with the current system）
- 运行风险（operational risk）
- 性能（performance）
- 可维护性（maintainability）
- 未来灵活性（future flexibility）
- 调试与可观测性影响（debugging and observability implications）

不要机械地把所有维度都塞进每一次决策。只使用真正相关的维度。

## 预期输出 (Expected Outputs)

产出或更新一个 `design_state`，至少包含：

- `design_target_type`
- `decision_nodes`
- `decisions`
- `risks`
- 可选的下游影响说明（downstream impact notes）

## 图表示意规范 (Diagram Conventions)

在代码块中使用字符图（character diagrams，无语言标签）来表达权衡或架构拓扑。

### 星级评分 (Star Ratings)

当存在 3 个以上选项，且需要跨 2 个以上定量维度比较时使用。

```
Overall Rating:

Auth0:      ★★★★☆  4/5
Keycloak:   ★★★☆☆  3/5
Self-build: ★☆☆☆☆  1/5

Dimension Breakdown:

Security:       Auth0 ★★★★★  Keycloak ★★★★☆  Self ★★☆☆☆
Speed-to-MVP:   Auth0 ★★★★★  Keycloak ★★★☆☆  Self ★☆☆☆☆
Cost-at-scale:  Auth0 ★★★☆☆  Keycloak ★★★★☆  Self ★★★★★
```

规则：

- 使用 `★`（实心，U+2605）和 `☆`（空心，U+2606），固定为 5 星制
- 格式为 `label ★★★★☆  4/5`
- 永远显示 5 个星号，例如 `★★☆☆☆`，不要写成 `★★`
- 先写 Overall Rating，再写 Dimension Breakdown
- Breakdown 中每一行是一个维度，同一行内并列所有选项
- 必须明确说明量表是 5 分制

### 架构拓扑图 (Architecture Topology)

当决策会改变组件布局或系统拓扑时使用。

```
┌──────────────────┐
│  Load Balancer   │
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
 [API x2] [API x2]
    │         │
    └────┬────┘
         ▼
  ┌────────────┐
  │  Postgres  │
  └────────────┘
```

- 基础设施组件使用 `┌ ┐ └ ┘ ─ │`
- 应用组件使用 `[brackets]`
- 以纵向流为主；横向连接使用 `──→`

### 何时添加图 (When to Add Diagrams)

- 星级评分：3 个以上选项 × 2 个以上定量维度
- 拓扑图：该决策会改变物理或逻辑组件布局
- 对于简单的二选一或纯定性比较，不要画图，直接用 Markdown 表格
- 最大宽度：78 字符

## 进入与退出条件 (Entry and Exit Criteria)

进入条件：

- 决策节点已经明确且边界清晰
- 该决策至少存在两个有意义的备选项

退出条件：

- 已经得到清晰的推荐方案
- 该决策带来的后果足够清楚，可以回馈给设计树的后续工作

## 交接规则 (Handoff Rules)

- 当选定方案影响了仍未解决的设计分支时，交回 `design-refinement`
- 当这是最后一个尚未解决的重要设计问题时，交给 `design-readiness-check`
- 如果这个决策落定后应重新考虑路由，交回 `design-orchestrator`
- 不要为了推进任务而把广义设计探索硬塞成一个边界明确的决策题
- 不要接管通用设计澄清工作
