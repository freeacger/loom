---
name: design-structure
description: "把一个模糊或部分成形的想法整理成初始设计结构（initial design structure）。当任务缺少清晰的设计树（design tree）、scope 边界、核心对象、关键流程或显式决策点时使用。只要用户给出的是一个想法、功能请求或系统目标，而你需要先把它变成结构化设计骨架，供后续深入细化，就应触发。本技能不用于处理已经有设计树、且主要需求是深化或验证的任务。"
---

# 设计结构化 (Design Structure)

## 概览 (Overview)

这个技能通过一个两阶段工作流，把模糊想法转换成初始设计树：

1. **交互式确认（Interactive confirmation）**：逐步与用户确认 `design_target_type`、problem、scope 与 assumptions
2. **设计树生成（Design tree generation）**：基于已确认输入产出设计树

它的首要产物是 `design_state`。
保存文件是可选的，只有当任务明确要求持久化（persistence）时才进行。

## 何时使用 (When to Use)

在以下情况下使用：

- 用户有一个想法，但还没有设计
- 任务缺少 scope、边界、核心对象或关键流程
- 还没有清晰的设计树
- 当前设计对话还停留在“我们到底在设计什么？”这个阶段
- 现有树缺少 `design_target_type`，需要把它显式补出来

以下情况不要使用：

- 已经存在可工作的设计树
- 主要需求是深化已有分支
- 主要需求是比较某个明确决策节点的选项
- 主要需求是判断设计是否已准备好进入规划
- 当前树只需要更深 refinement，而不是创建真正的 derived tree
- 任务是报告、笔记、摘要或文档改写
- 任务只是简单线性 SOP，没有真实的 design-state 边界

## 语言策略 (Language Strategy)

让设计文件语言与用户指令语言保持一致。

优先级如下：

1. 用户显式要求的输出语言
2. 当前用户指令的主导自然语言
3. 同一任务里最近几条用户指令的主导自然语言
4. 如果信号弱或含糊，则使用 English

规则：

- 聊天回复、交互式问答与设计文件都使用同一种语言
- 小节标题翻译成选定语言
- 文件路径、代码标识符、模板占位符（例如 `{{...}}`）和字面量配置键保持不变
- 除非用户明确要求双语输出，否则不要混用语言
- 第一阶段的交互式问答也必须匹配选定语言

如果输出语言是 English，默认标题示例如下：

- `Problem`
- `Scope`
- `Included` / `Excluded`
- `Assumptions`
- `Design Tree`
- `Open Branches`
- `Decision Nodes`
- `Decisions`
- `External Dependencies`

## 工作流 (Workflow)

### 阶段 1：交互式确认 (Phase 1: Interactive Confirmation)

在生成设计树前，先确认基础信息。顺序如下：

1. **Design target type**：确认 `system`、`workflow`、`methodology`、`framework` 之一
2. **Problem**：确认核心问题与成功指标（success metrics）
3. **Scope**：确认包含内容与排除内容
4. **Assumptions**：确认当前正在依赖的隐含假设

每确认一项，就更新共享 `design_state`。在后续对话中不要重复已经确认的内容。

只有当用户一开始就明确提供了某一部分时，才可以跳过该小节，例如“problem 是 X、scope 是 Y”，此时可以一轮同时确认两者。

### 阶段 2：设计树生成 (Phase 2: Design Tree Generation)

基于已确认输入，按照 `design_target_type` 对应的分支骨架生成设计树。

共享类型定义看 `../design-tree-core/REFERENCE.md`，本地优先分支骨架看 `REFERENCE.md`。

如果某个分支不相关，要显式说出来，而不是静默省略。

在对话中只展示：

- 树图（tree diagram）
- 需要用户动作的决策节点
- 开放分支名称
- 对下一步的建议

## 派生树创建 (Derived Tree Creation)

当父树已经识别出一个新的稳定问题域时，也可以用这个技能创建 derived tree。

以 `../design-tree-core/REFERENCE.md` 中的共享派生与交接规则为准。

创建 derived tree 时，必须完成以下事项：

1. 显式命名 parent tree 与 derived tree
2. 说明为什么要派生
3. 定义 derived tree 负责什么
4. 定义 derived tree 不负责什么
5. 记录最小 parent/child handoff：
   - 被抽出的分支
   - 继承的约束
   - 未解决问题
   - 预期输出
   - 返回条件

不要把父树原样复制进子树。
不要把派生当成倾倒溢出细节的手段。

## 交互式问答 (Interactive Q&A)

### 以意图驱动的提问策略 (Intent-Driven Strategy)

使用当前环境里可用的交互式提问工具。不要硬编码工具名，而是描述交互意图与约束，让模型根据环境选工具。

**跨 CLI 的约束：**

- 每次提问 1 到 3 个问题
- 每个问题最多 4 个选项
- 使用结构化文本（问题 + 可选选项）

**回退方式（Fallback）：** 如果当前环境没有专门的提问工具，就使用自然语言提示，参考下面的格式模板。

### 问题类型与格式 (Question Types and Formats)

#### 确认（Confirmation）——先陈述理解，再请求核对

```
## Problem

Core problem: Build an internal API gateway for unified routing, authentication, and rate limiting.
Success metrics: P99 latency < 50ms, availability > 99.9%

↑ Is this correct? Anything to amend?
```

#### 范围（Scope）——用 include/exclude 标记的清单

```
## Scope

My assessment:

Included ✓
- Request routing
- Authentication and authorization
- Rate limiting
- Request logging

Excluded ✗
- Service discovery
- Load balancing

↑ Any adjustments?
```

#### 决策（Decision）——表格 + 星级评分，最佳选项放前，最多 4 个选项

```
## Pending Decision: Auth Mode

| Option | Rating | Pros | Cons |
|--------|--------|------|------|
| JWT (stateless) | ★★★ | Scales horizontally, no server state | Revocation is complex, token size |
| Session (stateful) | ★★ | Instant revocation, mature pattern | Requires shared storage, limited scaling |
| API Key | ★ | Simple to implement | Low security, not suitable for user-level auth |

↑ Which one? Or a different idea?
```

#### 补充（Supplement）——直接提问，提示更宽松

```
## Supplementary Info

Expected daily request volume?

↑ Please fill in (a rough range is fine if uncertain)
```

**所有类型都遵循以下规则：**

- 一条消息只用一种问题类型
- 每个问题都以 `↑` 结尾，表示“轮到你了”
- 用户确认后，不要重复已确认内容（它已经进文件了）

## 持久化 (Persistence)

持久化是可选的。

本地保存契约看 `REFERENCE.md`。
除非任务明确要求输出文件，否则不要假设一定要落盘。

## 设计树要求 (Design Tree Requirement)

创建的初始设计树必须：

- 显式包含 `design_target_type`
- 使用该目标类型对应的正确分支骨架
- 识别开放分支（open branches）
- 识别显式决策节点（explicit decision nodes）
- 记录 assumptions，而不是静默依赖它们
- 保持“`design_state` 优先，工件其次（artifact second）”的输出顺序

如果某个分支不相关，要显式说明，而不是静默省略。

## 核心职责 (Core Responsibilities)

你的职责是：

1. 通过交互式确认澄清设计的真实目标。
2. 在建树前显式确定 `design_target_type`。
3. 捕获 scope、non-goals 与 constraints。
4. 构建初始设计树，至少包括一级分支，并在有价值时加二级分支。
5. 识别仍需 refinement 的开放分支。
6. 识别应在后续交给 `decision-evaluation` 的显式决策节点。
7. 记录 assumptions，而不是静默依赖它们。
8. 标记依赖未验证外部工具、API、库或服务的节点。在标记时做一次轻量 feasibility check（web search 或 doc lookup）。如果依赖明显不可行，立刻标 `✗`；如果确认大体可行但仍有未决问题，标 `[RESEARCH]` 并记录初步发现；如果已完全确认，则标 `✓`。
9. 只有当任务明确要求时才持久化设计。
10. 如果是在执行父树 handoff，就创建一个边界明确的 derived tree，而不是把父树原样内联重复。

## 预期输出 (Expected Outputs)

### 必需输出 (Required Output)

产出或更新一个 `design_state`，至少包含：

- `design_target_type`
- `problem`
- `scope`
- `design_tree`
- `open_branches`
- `decision_nodes`
- `external_dependencies`
- `status`

如果创建的是 derived tree，还应额外包含：

- parent/child ownership
- derivation reason
- parent/child handoff

### 对话输出（精简）(Conversation Output)

- 阶段 1：一次只问一个问题（见 Question Types）
- 阶段 2：树图 + 决策节点摘要 + 开放分支名称 + 下一步建议

你不需要把每个分支都在当前轮次闭合。

## 图表示意规范 (Diagram Conventions)

在无语言标签的代码块中，以字符树图（character tree diagram）渲染设计树。

**格式：**

```
design_tree
├── 1. Problem definition
│   ├── 1.1 Core problem
│   └── 1.2 Success metrics ✓
├── 2. Core flows [OPEN]
│   ├── 2.1 Happy path
│   └── 2.2 Error path
├── 3. Interfaces and data
│   └── 3.1 API contract [DRAFT]
├── 4. External integrations
│   └── 4.1 Payment SDK [RESEARCH]
└── 5. Decision points
    └── 5.1 Storage choice [DECISION]
```

**字符规则：**

- 分支：`├──`（中间项）、`└──`（最后一项）
- 延续：`│   `（父项后面还有兄弟节点）、`    `（父项已是最后一项，4 个空格）
- 编号：`1.`、`1.1`，前两层必须编号
- 最大宽度：78 字符

**状态标记：**

| 标记 | 含义 |
|--------|---------|
| `[OPEN]` | 未解决，仍需 refinement 或 decision |
| `[DECISION]` | 存在多个真实选项的决策节点 |
| `[DRAFT]` | 暂定，后续可能变 |
| `[RESEARCH]` | 依赖外部工具、API、库或服务；已通过初步可行性检查，但仍需深入验证 |
| `✓` | 已完成 / 已验证 |
| `✗` | 已否决 / 不在范围内 |

**何时渲染：** 只要设计树有 3 个以上分支，就始终展示树图。只有在设计极小（1 到 2 个分支）时才可省略。

## 进入与退出条件 (Entry and Exit Criteria)

进入条件：

- 还没有有意义的设计树
- 请求整体仍然处于未结构化状态

退出条件：

- 设计树已经有足够结构，可以支持后续工作
- 剩余主要工作变成分支细化或显式决策分析

## 交接规则 (Handoff Rules)

- 当树已经存在，但分支仍然过浅时，交给 `design-refinement`
- 当出现一个带真实选项的具体决策节点时，交给 `decision-evaluation`
- 如果 design state 变化足够大，需要重新评估路由，交回 `design-orchestrator`
- 如果 `design_target_type` 仍未解决，不要继续第一阶段之后的工作
- 不要在设计树尚未成形前强行把对话推进到方案比较
- 除非任务明确要求持久化，否则不要默认落盘
