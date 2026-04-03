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

## 可稳定引用门槛 (Stable-to-Reference Threshold)

只有在以下条件全部成立时，初始设计树才首次达到“可稳定引用（stable-to-reference）”门槛：

- `design_target_type` 已显式确认
- `problem` 与 `scope` 已足够清楚，能界定这棵树负责什么、排除什么
- 设计树已经形成与目标类型骨架匹配的稳定一级分支
- 每个一级分支都有足够内容，不是只有标题的空壳
- `open_branches` 已被显式列出
- 仍有真实选择时，`decision_nodes` 已被显式列出
- 该目标类型所需的基础分支没有缺口
- 下游设计技能仅凭持久化文件就不会误解当前设计边界

如果这些条件还不满足，就继续做结构化，不要落盘。

## 持久化 (Persistence)

`design-structure` 的首要产物是 `design_state`。
这套保存位置与时机契约是当前仓库的 repo-local 规则，不是 design-tree family 的共享默认规则。

当设计树首次达到“可稳定引用（stable-to-reference）”门槛时，持久化到 `docs/design-tree/<feature-slug>.md`，并且这一步必须早于任何下游设计交接（handoff）。

落盘后：

- 把该文件视为权威持久化设计工件
- 把文档状态标记为 `draft`
- 保持 `design_state` 与文件内容一致
- 除非明确的决策节点或 readiness gate 才是真正阻塞点，否则默认下一步推荐 `design-refinement`

## repo-local 文件命名规则 (Repo-Local File Naming)

所有持久化设计树文件都使用小写 kebab-case slug。
文件名本身也是 repo-local 交接契约的一部分，不属于 design-tree family 的共享命名默认规则。

### 主树 (Main Trees)

根设计树使用：

- `docs/design-tree/<feature-slug>.md`

`<feature-slug>` 应基于该设计树负责的问题域或功能边界来命名，而不是实现手段、会议名或模糊占位词。

正例：

- `docs/design-tree/api-gateway.md`
- `docs/design-tree/push-delivery-system.md`

反例：

- `docs/design-tree/design-v2.md`
- `docs/design-tree/new-thing.md`
- `docs/design-tree/refinement.md`

### 派生树 (Derived Trees)

从父树派生出的子树使用：

- `docs/design-tree/<parent-slug>--<derived-slug>.md`

`<derived-slug>` 应命名子树自己负责的子问题，而不是使用泛化的续写标记。

正例：

- `docs/design-tree/api-gateway--rate-limiting.md`
- `docs/design-tree/push-delivery-system--retry-policy.md`

反例：

- `docs/design-tree/api-gateway--part-2.md`
- `docs/design-tree/api-gateway--refinement.md`
- `docs/design-tree/api-gateway--v2.md`

### 同主题迭代 (Same-Topic Iterations)

如果只是同一条权威设计谱系上的普通细化，就复用原文件路径并在原文件上继续更新。
不要为普通后续细化创建 `-v2`、`-final`、`-new` 之类的后缀文件名。

如果必须让一个实质不同的替代谱系与原谱系并存，则创建新的根文件：

- `docs/design-tree/<feature-slug>--alt-<qualifier>.md`

采用这种并行文件时，必须在文档正文里写清关系，例如 `Alternative To` 或 `Supersedes`，避免下游把两份文件误读成同一设计的连续版本。

## 文档状态 (Document Status)

本仓库的文档状态使用以下两个值：

- `draft`：设计树首次达到“可稳定引用（stable-to-reference）”门槛后已经落盘，但细化、决策收敛或 readiness gate 仍在进行中
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

## File Lineage
- Parent Tree: [optional]
- Alternative To: [optional]
- Supersedes: [optional]

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
