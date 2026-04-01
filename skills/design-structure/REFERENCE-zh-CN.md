# 设计结构参考 (Design Structure Reference)

## 目的 (Purpose)

这个文件存放 `design-structure` 的本地指导（skill-local guidance）。

让 `SKILL.md` 专注于路由、核心行为与输出契约。
把持久化策略与本地模板放在这里。

## 目标类型骨架 (Target-Type Skeletons)

### `system`

推荐一级分支：

- Problem definition
- Scope and boundaries
- Core objects
- Core flows
- Interfaces and data
- Decision points
- Non-functional requirements
- Validation

### `workflow`

推荐一级分支：

- Problem definition
- Scope and boundaries
- Stages
- Inputs and outputs
- Handoffs and responsibilities
- Failure rollback
- Quality gates
- Validation

### `methodology`

推荐一级分支：

- Problem definition
- Scope and boundaries
- Applicability
- Decision rules
- Steps or phases
- Handoff form
- Exit conditions
- Validation

### `framework`

推荐一级分支：

- Problem definition
- Scope and boundaries
- Dimensions
- Modules
- Routing rules
- Handoff forms
- Exit conditions
- Validation

## 主体完成门槛 (Main Body Completion Threshold)

只有在以下条件全部成立时，初始设计树的主体才算完成：

- `design_target_type` 已显式确认
- `problem` 与 `scope` 已足够清楚，能界定这棵树负责什么、排除什么
- 设计树已经形成与目标类型骨架匹配的稳定一级分支
- 每个一级分支都有足够内容，不是只有标题的空壳
- `open_branches` 已被显式列出
- 仍有真实选择时，`decision_nodes` 已被显式列出
- 该目标类型所需的基础分支没有缺口

如果这些条件还不满足，就继续做结构化，不要落盘。

## 持久化 (Persistence)

`design-structure` 的首要产物是 `design_state`。

一旦达到主体完成门槛，立即持久化到 `docs/design-tree/<feature-name>.md`。

落盘后：

- 把该文件视为权威持久化设计工件
- 把文档状态标记为 `draft`
- 保持 `design_state` 与文件内容一致
- 除非明确的决策节点或 readiness gate 才是真正阻塞点，否则默认下一步推荐 `design-refinement`

## 文档状态 (Document Status)

本仓库的文档状态使用以下两个值：

- `draft`：设计树主体已经落盘，但细化、决策收敛或 readiness gate 仍在进行中
- `ready-for-planning`：`design-readiness-check` 已通过，不再存在阻止进入实现规划的阻塞缺口

状态切换规则：

- 首次落盘的版本必须是 `draft`
- 只要仍存在有意义的 `open_branches`、未解决的决策阻塞点或 readiness 失败项，就保持 `draft`
- 只有在 `design-readiness-check` 明确返回 READY 后，才能升级为 `ready-for-planning`

## 文件模板 (File Template)

执行持久化时，推荐使用以下文件结构：

```markdown
# <Feature Name> Design Tree

## Status
`draft | ready-for-planning`

## Design Target Type
`system | workflow | methodology | framework`

## Problem
[confirmed content]

## Scope
### Included
- ...
### Excluded
- ...

## Assumptions
- ...

## Design Tree
[tree diagram]

## Open Branches
- ...

## Decision Nodes
- ...

## Decisions
[filled later by decision-evaluation]
```
