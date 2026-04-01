# 设计结构参考 (Design Structure Reference)

## 目的 (Purpose)

这个文件存放 `design-structure` 的本地指导（skill-local guidance）。

让 `SKILL.md` 专注于路由、核心行为与输出契约。
把可选持久化与本地模板放在这里。

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

## 可选持久化 (Optional Persistence)

`design-structure` 的首要产物是 `design_state`。

只有在以下情况之一成立时，才持久化到 `docs/design-tree/<feature-name>.md`：

- 用户显式要求保存设计
- 当前任务明确要求产出设计工件
- parent-tree handoff 明确要求保存 derived tree

如果不需要持久化，就把结果保留在聊天里和 `design_state` 中。

## 可选文件模板 (Optional File Template)

当需要持久化时，推荐使用以下文件结构：

```markdown
# <Feature Name> Design Tree

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
