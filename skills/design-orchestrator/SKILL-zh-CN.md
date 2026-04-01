---
name: design-orchestrator
description: "在多个专用设计技能（specialized design skills）之间协调设计阶段工作。当任务在实现前需要结构化设计，例如设计拆解、设计澄清、决策路由或就绪性检查时使用。只要用户想把一个想法变成可落地的设计、深化一个部分成形的设计，或判断下一步设计动作，就应触发。本技能不用于直接执行、实现规划或单步编码任务。"
---

# 设计编排器 (Design Orchestrator)

## 概览 (Overview)

这个技能是设计阶段工作的入口（entrypoint）。

它自己不做深度设计。它的职责是检查当前设计状态（design state），精确选择**一个**下一步设计技能，并持续推动流程前进，直到设计准备好进入 `writing-plans`。

## 何时使用 (When to Use)

在以下情况下使用本技能：

- 任务在实现前需要设计
- 用户想把一个想法变成可落地的实现级设计
- 设计已经存在，但下一步不清楚
- 任务需要在设计拆解、决策分析和就绪性审查之间做路由

以下情况不要使用：

- 用户要的是直接执行
- 任务已经进入实现规划阶段
- 任务只是单步编码或编辑请求
- 任务是报告、笔记或摘要等写作请求
- 任务只是一个简单线性 SOP，没有真实的设计状态（design state）

## 共享设计状态 (Shared Design State)

默认设计流程围绕一个共享 `design_state` 传递，包含这些逻辑字段：

- `problem`
- `scope`
- `design_tree`
- `open_branches`
- `decision_nodes`
- `external_dependencies`
- `decisions`
- `risks`
- `validation`
- `status`
- `design_target_type`

把 `design_target_type` 当成**必填字段**。不要从一个不完整的 `design_state` 输入中静默推断它。

## 核心职责 (Core Responsibilities)

你的职责是：

1. 判断当前任务是否真的处于设计阶段。
2. 检查当前 `design_state`，找出最有价值的**单个**下一步技能。
3. 把任务路由到**恰好一个**下一步设计技能。
4. 每次交接后重新评估，直到设计准备好进入规划，或用户停止。
5. 防止过早进入 `writing-plans`。

## 路由规则 (Routing Rules)

按以下顺序应用路由：

### 1. 缺失必需状态 (Missing Required State)

在以下情况路由到 `design-structure`：

- 任务本应已经处于 `design_state` 形式，但缺少 `design_target_type`
- 设计树已经存在，但目标类型没有被显式设置

这种情况下，不要先继续到其他设计技能。
第一步必须先把目标类型明确下来。

### 2. 还没有真实设计树 (No Real Tree Yet)

在以下情况路由到 `design-structure`：

- 还没有真实设计树
- 任务仍然只是一个模糊想法或功能请求
- 范围（scope）、边界、核心对象或关键流程仍然缺失

### 3. 派生树候选 (Derived Tree Candidate)

在路由到 `design-refinement` 之前，先检查当前树是否开始承载第二个稳定问题域（second stable problem domain）。

这个判断以 `../design-tree-core/REFERENCE.md` 中的共享派生规则（derivation rules）为准。

只有在以下条件都满足时，才应创建派生树（derived tree）：

- 当前树开始回答第二个独立的核心问题
- 这个问题是反复出现的，不是一次性例外
- 这个分支已经像一个稳定的决策系统一样运作
- 子树能够定义自己的范围（scope）和完成标准（done criteria）
- 派生出去后，父树会更小、更清晰

如果这些条件成立：

- 路由到 `design-structure` 来创建派生树
- 要求显式父子交接（parent/child handoff）
- 要求派生完成后，父树收缩被抽出的分支

如果条件不成立：

- 不要派生
- 继续在当前树内做路由

### 4. 明确的决策阻塞点 (Explicit Decision Blocker)

在以下情况路由到 `decision-evaluation`：

- 存在边界明确的决策节点，且确实有真实备选项
- 阻塞点是一个具体选择题，而不是一个尚未细化的分支

### 5. 基本完成 (Mostly Complete)

在以下情况路由到 `design-readiness-check`：

- 设计看起来已经基本完成
- 剩下的问题主要是：能否安全进入实现规划

### 6. 其他情况 (Everything Else)

在以下情况路由到 `design-refinement`：

- 已经有设计树
- 主要分支仍然浅、模糊或未解决
- 主要需要的是更深的拆解、边界情况覆盖或失败路径澄清

当 `design-structure` 刚完成初始设计树主体时：

- 先假定该树已经完成落盘，再继续往下路由
- 除非真正阻塞点更明确地落在有边界的决策节点或 readiness check，否则默认下一步是 `design-refinement`

## 图表示意规范 (Diagram Conventions)

完成路由后，用代码块中的字符有向无环图（DAG，无语言标签）展示当前工作流位置：

```
[task-brief]
     │
     ▼
[design-orchestrator]  ← you are here
     │
     ▼
[design-structure]
```

如果需要展示分叉：

```
          [orchestrator]
          │    │    │
     ┌────┘    │    └────┐
     ▼         ▼         ▼
[structure] [refine] [evaluate]
```

**规则：**

- 组件写在 `[brackets]` 中，纵向流用 `│` 和 `▼`
- 分叉使用 `┌────┘` / `└────┐`；汇合使用 `└────┬────┘`
- 最大宽度：78 字符
- 只在路由发生变化，或用户要求状态总览时显示

## 进入与退出条件 (Entry and Exit Criteria)

进入条件：

- 任务需要设计阶段协调
- 用户没有要求跳过设计

退出条件：

- `design-readiness-check` 明确返回设计已准备好进入规划
- 用户显式停止设计流程
- 事实证明该任务根本不需要设计阶段工作

## 交接规则 (Handoff Rules)

- 如果应该由专用设计技能深入展开某个分支，就不要自己做深挖。
- 如果真正下一步是先做结构化或细化，就不要提前大范围比较选项。
- 如果下游技能实质性改变了设计，要重新检查路由，不要假定下一步。
- `design-structure` 刚完成主树后，默认优先继续到 `design-refinement`。
- 只有在 `design-readiness-check` 明确通过后，才能交给 `writing-plans`。
- 如果当前上下文无法调用下游技能，也必须明确指出它是下一步，然后停止。不要把对方职责内联代做。
- 同一轮里绝不能路由到多个下一步。
- 缺少 `design_target_type` 时，绝不能继续设计流。
- 绝不能因为当前树很长，就机械派生新树。
- 一旦判断某个分支应成为派生树，就不要继续在当前树里内联扩写它。
- 不要把报告撰写、笔记生产或 SOP 草拟混进设计路由中。
