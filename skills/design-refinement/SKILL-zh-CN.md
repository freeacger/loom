---
name: design-refinement
description: "深化一个已经存在的设计树（design tree），直到关键分支达到可实现程度（implementation-ready）。当高层结构已存在，但重要分支仍然模糊、过浅或未解决时使用。只要用户需要对部分成形的系统做更深拆解、覆盖边界情况、澄清失败路径、补充接口细节或验证标准，就应触发。本技能不用于从零搭建设计骨架，也不用于对单个明确决策节点做方案比较。"
---

# 设计细化 (Design Refinement)

## 概览 (Overview)

这个技能用于深化一棵已经存在的设计树。

它的任务是把仍然模糊的主要分支推进到可以实现的叶子节点（implementable leaf nodes）。它应让设计变得更具体、边界更清晰，也更不容易在实现阶段被误读。

## 何时使用 (When to Use)

在以下情况下使用：

- 设计树已经存在
- 设计仍然过于高层，无法指导实现规划
- 重要分支缺少接口、边界、失败行为或验证细节
- 用户要求把设计变得更具体、更详细或更完整

以下情况不要使用：

- 还没有设计树
- 主要问题是一个边界明确、且有多个方案的单一决策
- 主要问题是判断当前设计是否可以进入规划
- 当前设计状态（design state）缺少 `design_target_type`
- 任务本质上是报告、笔记或 SOP 草稿

## 必需输入 (Required Input)

没有明确的 `design_target_type` 时，不要继续细化。

如果设计状态缺少这个字段：

- 停止细化
- 不要静默假设成 `system`
- 交回 `design-orchestrator` 或 `design-structure`，让类型被显式设置

## 叶子节点标准 (Leaf Node Standard)

使用 `../design-tree-core/REFERENCE.md` 中按目标类型区分的完成标准（completion standard）。

简要总结如下：

- `system`：职责（responsibility）、非职责范围（non-responsibility）、相邻交互（adjacent interaction）、失败处理（failure）、验证（validation）
- `workflow`：阶段目标（stage goal）、输入/输出（input/output）、负责人（owner）、回滚（rollback）、质量门（quality gate）
- `methodology`：适用范围（applicability）、不适用范围（non-applicability）、决策规则（decision rules）、交接形式（handoff form）、退出条件（exit condition）
- `framework`：维度或模块（dimension or module）、非负责范围（non-ownership）、路由规则（routing rule）、交接形式（handoff form）、完成规则（completion rule）

如果针对当前目标类型，这些问题仍未回答完，该分支就还没完成。

## 细化与派生的边界 (Refinement vs Derivation Boundary)

只有当一个分支仍属于当前树原始核心问题的一部分时，才应继续细化。

以 `../design-tree-core/REFERENCE.md` 中的共享派生规则（shared derivation rules）为准。

当某个分支开始同时呈现以下全部特征时，应停止内联细化：

- 它正在回答第二个独立的核心问题
- 它需要反复做本地路由决策
- 它需要自己的范围边界（scope boundary）
- 它需要自己的完成检查（completion check）
- 继续在当前树内细化会让父树更难路由

出现这些条件后：

- 不要继续在当前树里内联展开该分支
- 将它显式标记为派生候选（candidate for derivation）
- 交回 `design-orchestrator` 或 `design-structure` 进行显式派生树创建

## 核心职责 (Core Responsibilities)

你的职责是：

1. 一次处理一个未解决分支。
2. 优先处理高风险、高依赖或高歧义分支。
3. 结合当前 `design_target_type`，把分支展开成具体子分支与叶子节点。
4. 暴露隐藏假设与边界情况。
5. 在缺失处补上失败路径与验证细节。
6. 如果发现新的决策节点，要显式标记出来，而不是假装它已经定了。
7. 通过对外部依赖做深入验证，解决 `[RESEARCH]` 节点，包括 API 兼容性（API compatibility）、版本约束（version constraints）、集成模式（integration patterns）、错误处理（error handling）和速率限制（rate limits）。验证通过后把 `[RESEARCH]` 替换为 `✓`；如果被否定，替换为 `✗`；如果需要比较替代方案，改为 `[DECISION]`。如果当前上下文无法完成验证，记录已知信息并保留 `[RESEARCH]`。

## 预期输出 (Expected Outputs)

产出或更新一个 `design_state`，至少包含：

- `design_target_type`
- 已细化的 `design_tree` 分支
- 更新后的 `open_branches`
- `confirmed_assumptions`
- `risks`
- `validation`
- 如果解决了 `[RESEARCH]` 节点，还应更新 `external_dependencies`
- 如果发现新决策，也要更新 `decision_nodes`

## 图表示意规范 (Diagram Conventions)

在无语言标签的代码块中使用字符图，表示组件交互、失败路径与状态转换。

### 时序图 (Sequence Diagrams)

当一个叶子节点描述“它如何与相邻部分交互”，且涉及 3 个以上组件时使用。

```
Client          API Server      Auth Service     DB
  │                │                │             │
  │── request ────→│                │             │
  │                │── verify ────→│             │
  │                │←── ok ────────│             │
  │                │── insert ─────────────────→│
  │←── response ───│                │             │
```

**规则：**

- 最多三列；如果参与方更多，就拆成两张图
- 生命周期线使用 `│`；消息使用 `──→`（向右）或 `←──`（向左）
- 标签写在箭头线上：`── label ──→`
- 参与方名称最长 20 个字符，顶部左对齐
- 除非 ACK 返回承载重要数据，否则省略

### 数据流图 (Data Flow Diagrams)

当需要展示数据管线或转换链时使用。

```
Source
    │
    ▼
Transform ──── enrich ────→ Enrichment
    │                            │
    ▼                            ▼
Sink A                     Cache Store
```

- 组件写纯文本，不加 brackets
- 纵向使用 `│` 和 `▼`；横向使用 `──→`；回流使用 `◄────`

### 状态机图 (State Machine Diagrams)

当某个组件存在 3 个以上状态与转换时使用。

```
┌──────────┐     approve     ┌───────────┐
│ Pending  │───────────────→│ Approved  │
└──────────┘                 └───────────┘
     │                            │
     │ timeout               │ start
     ▼                            ▼
┌──────────┐             ┌──────────┐     ok     ┌───────────┐
│ Expired  │             │ Running  │───────────→│ Succeeded │
└──────────┘             └──────────┘             └───────────┘
```

- 状态框使用 `┌ ┐ └ ┘ ─ │`
- 转换使用 `──→`，标签放在上下方
- 终态可带 `✓` 或 `✗`

### 何时添加图 (When to Add Diagrams)

- 时序图：3 个以上组件发生消息交互
- 数据流图：存在 3 个以上阶段或分叉路径的管线
- 状态机图：组件存在 3 个以上状态与转换
- 对于 2 个节点的线性流程，不要画图，直接用编号列表
- 最大宽度：78 字符

## 进入与退出条件 (Entry and Exit Criteria)

进入条件：

- 已存在设计树
- 重要分支仍然模糊或不完整

退出条件：

- 关键分支已经细化到可实现叶子节点
- 剩余工作主要变成决策评估或就绪性检查

## 交接规则 (Handoff Rules)

- 当暴露出一个有多个真实备选项的明确决策节点时，交给 `decision-evaluation`
- 当关键分支都已闭合，主要问题变成就绪性检查（readiness）时，交给 `design-readiness-check`
- 如果设计树本身缺少一个基础分支，交回 `design-structure`
- 如果 `design_target_type` 缺失，立即交回 `design-orchestrator` 或 `design-structure`
- 不要为了推进任务而虚构选项比较
- 不要用细化（refinement）去吞掉一个本应派生的新树分支
- 不要把 `workflow`、`methodology` 或 `framework` 分支强行压成 `system` 风格的叶子
