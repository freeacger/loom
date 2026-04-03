# 设计树核心参考 (Design Tree Core Reference)

## 目的 (Purpose)

本文件定义 design-tree 技能家族的**最小共享参考规则（minimum shared reference rules）**。

它用于支持以下技能之间的一致行为：

- `design-orchestrator`
- `design-structure`
- `design-refinement`
- `design-readiness-check`
- `decision-evaluation`

它**不是**：

- 模板库
- 项目知识库
- 设计文档仓库

---

## 1. 共享设计状态 (Shared Design State)

### 1.1 必需字段 (Required Fields)

所有 design-tree 技能都围绕一个共享 `design_state` 推理，至少要求这些逻辑字段：

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

这个家族不要求严格 schema validator，但要求这些字段被稳定地视为设计阶段的必需状态。

### 1.2 必需目标类型 (Required Target Type)

`design_target_type` 是 `design_state` 的**强制字段**：

- 不是可选字段
- 不是可以默认补上的字段
- 不是事后注解

允许值只有：

- `system`
- `workflow`
- `methodology`
- `framework`

如果输入的 design-state 缺少 `design_target_type`，所有 design-tree 技能都必须把它视为**无效状态**。
任何 design-tree 技能都**不得**根据上下文、问题描述或其他字段，静默推断、假设、默认或派生出一个 `design_target_type`。

缺失该字段时的修复路径只有两条：

1. **停止并拒绝继续**：明确把状态视为不完整
2. **路由回能显式设置该字段的步骤**：交回给用户、orchestrator，或负责建立初始 design state 的入口技能

技能可以要求用户显式提供类型；但不能替用户做这个决定。

### 1.3 共享输出契约 (Shared Output Contract)

design-tree 技能的主要输出契约是：**产出或更新 `design_state`**。

整个家族不共享默认 persistence contract。
如果某个技能或仓库希望落盘设计文件，那是 skill-local 或 repo-local adapter 行为，不属于共享设计树规则。

### 1.4 设计树 (Design Tree)

设计树是对一个稳定设计问题空间（stable design problem space）的结构化表达。

它应捕获：

- scope
- major branches
- decision nodes
- open branches
- handoff points
- readiness state

它不应被当成：

- task board
- report
- writing outline
- examples 集合
- project log

### 1.5 父树 (Parent Tree)

父树是当前某个设计问题域中最权威的树。

它负责：

- 问题的主框架
- 原始且稳定的 scope
- 在需要时把问题路由进 derived trees

### 1.6 派生树 (Derived Tree)

派生树是在某个分支演化为独立稳定决策系统时创建的新树。

派生树必须：

- 回答与父树不同的核心问题
- 拥有自己的边界
- 拥有自己的完成标准
- 消费来自父树的已定义 handoff

派生树绝不能：

- 重复整棵父树
- 成为承接溢出细节的垃圾桶
- 静默重定义父树 scope

### 1.7 开放分支 (Open Branch)

开放分支是树内尚未解决、但仍然属于当前问题域的区域。

并不是每个开放分支都值得派生为新树。

### 1.8 稳定决策系统 (Stable Decision System)

当某个分支具备以下特征时，它开始变成一个稳定决策系统：

- 在工作中反复出现
- 需要自己的路由逻辑
- 有自己的 inputs 和 outputs
- 有自己的 completion check
- 已经不像普通分支 refinement

### 1.9 交接 (Handoff)

handoff 是一棵树向另一棵树传递的最小结构化转移。

它存在的目的，是防止：

- 静默 scope drift
- 重复推理
- 父子边界含糊
- 树间隐藏假设

---

## 2. 目标类型分类 (Target Type Classification)

### 2.1 `system`

当设计主要关注 built system 中的组件、接口、数据流、运行边界或部件间的失败行为时，使用 `system`。

典型问题：

- 核心对象或服务是什么？
- 相邻部分如何交互？
- 什么会失败？在哪里失败？如何验证？

### 2.2 `workflow`

当设计主要关注有序阶段、stage handoff、操作角色、rollback 路径或 quality gate 时，使用 `workflow`。

典型问题：

- 阶段有哪些？
- 每个阶段输入什么、输出什么？
- 每个 handoff 由谁或什么负责？

### 2.3 `methodology`

当设计主要关注一个可复用的方法、决策流程、停机条件或工作判断框架时，使用 `methodology`。

典型问题：

- 这个方法何时适用？
- 哪些规则决定工作如何推进？
- 用户何时应停止或升级？

### 2.4 `framework`

当设计主要关注维度、路由规则、分类规则或其他工作赖以运作的协调契约时，使用 `framework`。

典型问题：

- 哪些维度组织这个问题？
- 工作如何被路由？
- handoff form 和 exit rule 是什么？

### 2.5 分类规则 (Classification Rule)

如果多个解释都说得通，应选择最匹配设计**主核心问题**的类型。
不要仅仅因为能用组件来描述，就把 workflow 或 methodology 硬塞成 `system`。

---

## 3. 类型特定完成标准 (Type-Specific Completion Standards)

### 3.1 `system`

只有当一个叶子节点能回答以下问题时，它才算 implementation-ready：

1. 它负责什么
2. 它不负责什么
3. 它如何与相邻部分交互
4. 失败会长什么样
5. 如何验证它

### 3.2 `workflow`

只有当一个叶子节点能回答以下问题时，它才算 implementation-ready：

1. 阶段目标是什么
2. 输入什么、输出什么
3. 谁或什么负责该阶段
4. rollback 或 retry 路径是什么
5. 什么 quality gate 关闭该阶段

### 3.3 `methodology`

只有当一个叶子节点能回答以下问题时，它才算 implementation-ready：

1. 该方法何时适用
2. 何时不适用
3. 哪些决策规则指导推进
4. 它输出什么 handoff form
5. 什么 exit / stop condition 结束该方法

### 3.4 `framework`

只有当一个叶子节点能回答以下问题时，它才算 implementation-ready：

1. 它定义了哪个 dimension 或 module
2. 它明确不拥有的内容是什么
3. 它应用什么 routing 或 classification rule
4. 它期望什么 handoff form
5. 什么 exit condition 或 completion rule 会关闭它

---

## 4. 派生规则 (Derivation Rules)

### 4.1 什么时候派生新树 (When to Derive a New Tree)

只有当以下**硬门槛（hard gates）**全部满足时，才派生新树：

1. 这个分支已经在回答一个不同于父树原始核心问题的独立核心问题，而不是“同一个问题更深”
2. 候选派生树能够定义自己明确的 scope 与 non-scope
3. 候选派生树能够定义自己的 done criteria 或 completion check
4. 父 / 子 handoff 能被表达为一个显式转移契约，包含清楚的输入与预期返回形式

任意一个硬门槛不满足，都不要派生。

### 4.2 辅助信号 (Supporting Signals)

在硬门槛全部满足后，再看以下辅助信号：

1. 这个新问题是反复出现的，而不是一次性例外
2. 该分支已经表现得像一个稳定决策系统，拥有自己的 inputs、outputs、routing logic 或 decision cadence
3. 派生它会让父树明显更小、更清晰

只有在 3 条辅助信号中至少满足 2 条时，才建议派生。

### 4.3 决策标准 (Decision Standard)

派生判断应采用门槛式（gate-based）决策，而不是加权打分（weighted score）。

- 只要任意一个硬门槛失败，就继续在父树内 refine
- 如果硬门槛全部通过，且辅助信号至少通过 2 条，就派生新树
- 如果硬门槛全部通过，但辅助信号少于 2 条，就继续留在父树内细化，并在后续重新评估

不要用总分或加权分数去覆盖未满足的硬门槛。

### 4.4 什么时候不要派生 (When Not to Derive)

出现以下情况时，不要派生新树：

- 分支只需要更深 refinement
- 内容主要是示例或解释
- 问题是 project-specific 的
- 分支只是暂时变大
- 内容更适合放进 checklist、report、template 或 script
- 问题仍明显属于父树原始核心问题

### 4.5 派生测试问题 (Derivation Test)

在派生前先问自己：

- 这还是同一个问题，只是更深了吗？
- 还是它已经成了另一个拥有稳定决策的新问题？

如果还是同一个问题，就 refine。  
如果已经是另一个稳定问题，就 derive。

---

## 5. 父 / 子交接契约 (Parent / Child Handoff Contract)

### 5.1 最小交接字段 (Minimum Handoff Fields)

父树在向派生树 handoff 时，至少应提供：

- `parent_tree_name`
- `derived_tree_name`
- `reason_for_derivation`
- `branch_being_extracted`
- `inherited_constraints`
- `unresolved_questions`
- `expected_output`
- `return_conditions`

### 5.2 派生后父树职责 (Parent Responsibilities After Derivation)

派生树创建后，父树必须：

- 只保留该分支摘要
- 显式链接到派生树
- 停止在父树中继续内联扩展该分支
- 记录 handoff 状态
- 说明子树何时应返回结果

父树绝不能继续维护一份子逻辑的重复副本。

### 5.3 子树职责 (Child Responsibilities)

派生树必须：

- 显式声明自己的 scope
- 声明自己不拥有什么
- 把父树 handoff 当作输入
- 避免重定义父问题
- 以父树能消费的形式返回结果

### 5.4 返回路径 (Return Paths)

派生树可以返回以下结果之一：

- resolved result
- unresolved result，并带显式 open questions
- recommendation to refine parent assumptions
- recommendation to derive another tree，但前提是再次满足 derivation rules

---

## 6. 反膨胀治理 (Anti-Bloat Governance)

### 6.1 核心规则 (Core Rule)

让树保持足够小，从而维持路由清晰度。

树应存放稳定结构，而不是累积历史。

### 6.2 什么应放在树里 (What Belongs in a Tree)

允许：

- 稳定边界
- 主要分支
- 决策点
- handoff rules
- completion criteria
- 仍然属于这棵树的 open branches

不允许：

- 长篇示例
- 重复表述
- 项目特定结论
- 临时执行笔记
- 发布说明
- 模板正文
- FAQ 累积
- 应该放在别处的重复 caveat
- 只对单个仓库有意义的 persistence adapter

### 6.3 增长控制 (Growth Controls)

当树开始变大时，优先按这个顺序处理：

1. 压缩措辞
2. 去重
3. 把 examples 移出去
4. 把 project-specific 内容移出去
5. 只有在满足 derivation rules 时才派生新树

不要仅仅因为当前树很长就派生新树。

### 6.4 驱逐规则 (Eviction Rules)

出现以下情况时，应把内容移出树：

- 它只是解释性内容
- 它只对一个项目相关
- 它只服务一个下游工作流
- 它在多个位置重复出现
- 它已经不再改变路由或设计决策

### 6.5 压缩触发器 (Compaction Trigger)

出现以下任意情况时，应做一次 compaction pass：

- 重复 caveat
- 重复的 branch definition
- mixed responsibilities
- 树中包含大段 examples
- 父树与子树都在扩展同一分支
- 这棵树已经变得“比起阅读更难路由”

### 6.6 Anti-Bloat 优先级 (Anti-Bloat Priority)

当“保留细节”和“保留结构”冲突时，优先保留结构。

---

## 7. 其他技能如何使用本参考 (Use by Other Skills)

### `design-orchestrator`

用本参考判断：

- 某个 design-state 输入是否完整到足以路由
- 是否继续在当前树内路由
- 是否应派生新树

### `design-structure`

在以下情况下使用本参考：

- 确认 `design_target_type`
- 选择初始 branch skeleton
- 创建新的 derived tree
- 定义 parent/child 边界

### `design-refinement`

在以下情况下使用本参考：

- 判断某个分支是否应继续留在 refinement 中
- 判断 refinement 是否已经跨入 derivation territory
- 对当前目标类型应用正确 completion standard

### `design-readiness-check`

只用本参考来检测：

- 缺失的 required state
- mixed responsibilities
- tree drift
- 未解决的 branch ownership
- 与 target type 对应的 readiness gaps

### `decision-evaluation`

在以下情况下使用本参考：

- 确认某个 bounded decision 是否属于当前 target type
- 把选定方案回填到正确的 design-state 形状中
