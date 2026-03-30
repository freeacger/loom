---
name: design-structure
description: Build the initial design structure from a vague or partially formed idea. Use when the task lacks a clear design tree, scope boundaries, core objects, key flows, or explicit decision points. Trigger when the user has an idea, feature request, or system goal that needs to be turned into a structured design skeleton before deeper refinement. Do not use when the design tree already exists and the main need is to deepen or validate it.
---

# Design Structure

## Overview

This skill turns a vague idea into an initial design tree through a two-phase workflow:

1. **Interactive confirmation** — progressively confirm problem, scope, and assumptions with the user
2. **Design tree generation** — produce the design tree based on confirmed inputs

All output is written to a file. The conversation stays concise: questions during confirmation, tree diagram and action items during generation.

## When to Use

Use this skill when:

- the user has an idea but not a design
- the task lacks scope, boundaries, core objects, or key flows
- there is no clear design tree yet
- the current design conversation is still at the "what are we even designing?" stage

Do not use this skill when:

- a workable design tree already exists
- the main need is deeper decomposition of existing branches
- the main need is to compare options for one explicit decision node
- the main need is to decide whether the design is ready for planning

## Workflow

### Phase 1: Interactive Confirmation

Confirm the foundation before generating the design tree. Proceed in order:

1. **问题(problem)** — confirm the core problem and success metrics
2. **范围(scope)** — confirm what is included and excluded
3. **假设(assumptions)** — confirm implicit assumptions being made

After each confirmation, immediately write the confirmed section to the design file. Do not repeat confirmed content in subsequent conversation.

Skip a section only if the user explicitly provides it upfront (e.g., "the problem is X and the scope is Y" — confirm both in one round).

### Phase 2: Design Tree Generation

Based on confirmed inputs, generate the design tree covering (when relevant):

1. 问题定义(problem definition)
2. 范围与边界(scope and boundaries)
3. 核心对象(core objects)
4. 核心流程(core flows)
5. 接口与数据(interfaces and data)
6. 决策点(decision points)
7. 非功能需求(non-functional requirements)
8. 验证与交付(validation and delivery)

If a branch is not relevant, say so explicitly instead of silently omitting it.

Write the complete design tree to the file. In conversation, show only:
- the tree diagram
- decision nodes that need user action
- open branch names (point user to file for details)
- next step recommendation

## Interactive Q&A

### Intent-Driven Strategy

Use whatever interactive question tool is available in the current environment. Do not hardcode tool names — describe the interaction intent and constraints; the model selects the right tool based on its environment.

**Constraints (cross-CLI compatible):**
- 1–3 questions per prompt
- ≤ 4 options per question
- Structured text (question + optional choices)

**Fallback:** If no dedicated question tool is available, use natural language prompts (see format templates below).

### Question Types and Formats

#### Confirmation — state understanding, ask to verify

```
## 问题(problem)
核心问题：构建内部 API 网关，统一路由、认证、限流。
成功指标：P99 延迟 < 50ms，可用性 > 99.9%

↑ 理解正确吗？需要修正哪里？
```

#### Scope — checklist with include/exclude markers

```
## 范围(scope)
我的判断：

包含 ✓
- 路由转发
- 认证鉴权
- 限流
- 请求日志

不包含 ✗
- 服务发现
- 负载均衡

↑ 需要调整吗？
```

#### Decision — table with star ratings, best option first, max 4 options

```
## 待决策: 认证模式

| 方案 | 推荐 | 优势 | 劣势 |
|------|------|------|------|
| JWT 无状态 | ★★★ | 水平扩展好，无服务端状态 | 撤销麻烦，token 体积 |
| Session 有状态 | ★★ | 撤销即时，成熟方案 | 需共享存储，扩展受限 |
| API Key | ★ | 实现简单 | 安全性低，不适合用户级 |

↑ 选哪个？或者有其他想法？
```

#### Supplement — direct question with relaxed prompt

```
## 补充信息
预期的日均请求量级？

↑ 请补充（不确定可以给个大概范围）
```

**Rules for all types:**
- One question type per message
- End every question with `↑` marker to signal "your turn"
- After user confirms, do not repeat the confirmed content (it is already in the file)

## File Output

### Path

Write the design file to `docs/design-tree/<feature-name>.md`.

Derive `<feature-name>` from the user's request (e.g., "API 网关" → `api-gateway`). Create the directory if it does not exist.

### Template

```markdown
# <功能名> 设计树

## 问题(problem)
[confirmed content]

## 范围(scope)
### 包含
- ...
### 不包含
- ...

## 假设(assumptions)
- ...

## 设计树(design_tree)
[tree diagram]

## 开放分支(open_branches)
- ...

## 决策节点(decision_nodes)
- ...

## 决策记录(decisions)
[filled later by decision-evaluation]
```

### Incremental Write

Write each section to the file as soon as it is confirmed or generated. Do not wait until the end. This prevents data loss if the process is interrupted.

## Design Tree Requirement

Create an initial design tree that covers, at minimum, these branches when relevant:

1. 问题定义(problem definition)
2. 范围与边界(scope and boundaries)
3. 核心对象(core objects)
4. 核心流程(core flows)
5. 接口与数据(interfaces and data)
6. 决策点(decision points)
7. 非功能需求(non-functional requirements)
8. 验证与交付(validation and delivery)

If a branch is not relevant, say so explicitly instead of silently omitting it.

## Core Responsibilities

Your responsibilities are:

1. Clarify the real goal of the design through interactive confirmation.
2. Capture scope, non-goals, and constraints.
3. Build an initial design tree with first-level and, where useful, second-level branches.
4. Identify open branches that still need refinement.
5. Identify explicit decision nodes that should later go to `decision-evaluation`.
6. Record assumptions instead of silently relying on them.
7. Write all output to the design file incrementally.
8. Flag nodes that depend on unverified external tools, APIs, libraries, or services. Perform a lightweight feasibility check (web search or doc lookup) at the time of flagging. If the dependency is clearly infeasible, mark `✗` immediately; if confirmed feasible with open questions, mark `[RESEARCH]` with initial findings; if fully confirmed, mark `✓`.

## Expected Outputs

### File Output (complete)

The design file at `docs/design-tree/<name>.md` must contain:
- 问题(problem) — confirmed
- 范围(scope) — confirmed, with explicit non-goals
- 假设(assumptions) — confirmed
- 设计树(design_tree) — tree diagram
- 开放分支(open_branches) — list
- 决策节点(decision_nodes) — list
- 外部依赖(external_dependencies) — list, each entry contains: node, dependency, validation_needed, status (unverified | verified | blocked)

### Conversation Output (concise)

- Phase 1: one question at a time (see Question Types)
- Phase 2: tree diagram + decision node summaries + open branch names + next step

You are not expected to fully close every branch.

## Diagram Conventions

Render the design tree as a character tree diagram inside a code block (no language tag).

**Format:**

```
design_tree
├── 1. 问题定义(problem definition)
│   ├── 1.1 核心问题
│   └── 1.2 成功指标 ✓
├── 2. 核心流程(core flows) [OPEN]
│   ├── 2.1 正常路径
│   └── 2.2 异常路径
├── 3. 接口与数据(interfaces)
│   └── 3.1 API 合约 [DRAFT]
├── 4. 外部集成(integrations)
│   └── 4.1 支付 SDK [RESEARCH]
└── 5. 决策点(decisions)
    └── 5.1 存储选择 [DECISION]
```

**Character rules:**

- Branches: `├──` (middle), `└──` (last)
- Continuation: `│   ` (non-last parent), `    ` (last parent, 4 spaces)
- Numbering: `1.`, `1.1` — required at first two levels
- Max width: 78 characters

**Status markers:**

| Marker | Meaning |
|--------|---------|
| `[OPEN]` | Unresolved, needs refinement or decision |
| `[DECISION]` | Decision node with multiple real options |
| `[DRAFT]` | Tentative, may change |
| `[RESEARCH]` | Depends on an external tool, API, library, or service that has passed initial feasibility check but needs deeper validation |
| `✓` | Complete / verified |
| `✗` | Rejected / out of scope |

**When to render:** Always include a tree diagram when the design tree has 3+ branches. Omit only if the design is trivially small (1-2 branches).

## Entry and Exit Criteria

Enter when:

- there is no meaningful design tree yet
- the request is still mostly unstructured

Exit when:

- the design tree exists with enough structure for follow-on work
- the main remaining work is branch refinement or explicit decision analysis

## Handoff Rules

- Hand off to `design-refinement` when the tree exists but branches are still too shallow.
- Hand off to `decision-evaluation` when there is a concrete decision node with real options.
- Hand back to `design-orchestrator` if the design state changed enough that routing should be re-evaluated.
- Do not force the conversation into option comparison before the design tree is formed.
