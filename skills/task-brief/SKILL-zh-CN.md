---
name: task-brief
description: "在执行前，把原始自然语言请求整理成结构化、与模型无关的任务简报（Task Brief）。当请求复杂、多步骤、跨领域、含糊，或将被交给其他模型或 agent 时触发；当用户明确表示“帮我理清我到底需要什么”“我不知道该怎么提这个需求”“我想做 X 但不知道从哪开始”“帮我把这个说清楚”时也应触发。对于意图明确的简单单行请求，例如“修掉第 42 行的拼写错误”或“重命名这个变量”，不要触发。"
---

# 任务简报 (Task Brief)

## 概览 (Overview)

把一条原始自然语言请求整理成一份结构化任务简报（task brief），让另一个执行者在**不阅读原始消息**的前提下也能理解任务。

**这个技能本质上是一个任务规格归一化器（task specification normalizer）。** 它的职责是提炼真实目标、补齐完成标准，并显式写出关键约束。它不负责设计阶段路由（design-stage routing）、任务拆解（decomposition）、实现规划（implementation planning）或任务执行（execution）。

价值很直接：好的 brief 可以减少误解，避免在错误的问题上浪费时间，并让交接（handoff）更干净。

## 核心职责 (Core Responsibilities)

`task-brief` 只做下面这些事：

1. 重写真实的用户目标（User Goal），而不是照抄表面措辞。
2. 提炼成功标准（Success Criteria），明确什么结果算完成。
3. 写出交付物（Deliverables），让执行者知道最终要产出什么。
4. 提炼会改变执行路径的约束（Constraints）。
5. 用简短假设（Assumptions）标出推断边界。
6. 当只剩一个关键未知量时，提出一个澄清问题（Clarifying Question）。
7. 做一个轻量判断：这个任务是否需要进入设计阶段（Needs Design）。

`task-brief` 不做下面这些事：

- 在设计技能之间做路由
- 把任务拆成子任务
- 画依赖关系图（DAG, Directed Acyclic Graph）
- 写实现步骤
- 给迁移顺序或实施顺序
- 为了“问得更尖锐”而默认先搜索代码库

如果真实任务已经是根因调查（root-cause investigation），应改用 `systematic-debugging`，不要把 `task-brief` 变成调试流程。

## 何时使用 (When to Use)

**以下场景应触发：**

- 请求包含多个子目标，或优先级顺序不清楚
- 请求跨越多个领域，例如 data + UI + API
- 用户描述的问题未必是真正问题
- 任务大概率会被交给另一个执行者
- 缺少上下文时，执行者会被迫做高风险假设
- 用户明确要求你帮他先把任务说清楚

**以下场景不要触发：**

- 单一、明确、无歧义的动作，例如“delete this function”“run the tests”
- 意图已经清晰、执行路径显而易见的请求
- 对当前进行中任务的补充说明
- 明确要求产出设计树（design tree）或做设计阶段拆解的请求

如果你拿不准，就问自己一句：执行者只看这份 brief，能不能正确开工？如果能，brief 就足够了。

## 复杂度分层 (Complexity Tiers)

写 brief 前，先把请求分到下面三档之一。

| 层级（Tier） | 信号（Signal） | 响应方式（Response） |
|------|--------|----------|
| **Direct** | 单一目标、范围清晰、没有关键缺失信息 | 写简短 brief。通常 `Needs Design` 为 `no`。 |
| **Clarify** | 还剩一个关键未知量，或用户写出的目标本身可能不准确 | 先写 brief，再只问一个澄清问题。 |
| **Structured** | 多目标、跨领域，或需要一份适合交接的完整 brief | 写完整 brief，但停在 brief。不要在本技能里拆任务或做路由。 |

**Clarify** 常见有三种子类型：

- *Missing parameter*：目标已知，但缺一个关键细节。
- *Ambiguous intent*：目标可能指向两件差异很大的事。
- *Inaccurate goal*：用户说出的是方案、症状，或范围异常的目标，而不是真正意图。

对不准确目标，需要识别三类信号：

1. **Solution-as-goal**：用户点名了某个技术方案，例如 “add Redis caching”，而不是它要解决的问题。
2. **Symptom-as-goal**：用户描述的是错误现象，例如 “fix timeout errors”，而不是想达成的结果。
3. **Scope anomaly**：用户给出的范围过窄或过宽，看起来不符合问题的自然边界。

出现这些信号时：

- 在 `User Goal` 中重写你对底层目标的最佳猜测
- 把这层猜测写进 `Assumptions`
- 只问一个用来确认真实目标的澄清问题

不要为了把问题问得更尖锐，就默认先搜索代码库。如果真实任务已经是调试，请转到 `systematic-debugging`。

## 输出格式 (Output: Task Brief)

始终按下面的字段语义输出 brief。中文响应可以用双语标题；如果没有澄清问题，就省略 `Clarifying Question`。

````
## 任务简报 (Task Brief)

**任务类型 (Task Type):** [分析 (analysis) | 变更 (transformation) | 生成 (generation) | 调研 (investigation) | 其他 (other)]

**用户目标 (User Goal):**
[1-2 句。写真实意图，不写表面说法。句子尽量以动词开头。]

**成功标准 (Success Criteria):**
- [可观察的完成信号 1]
- [可观察的完成信号 2]

**交付物 (Deliverables):**
- [具体工件 1]
- [具体工件 2]

**澄清问题 (Clarifying Question):**
[只在还剩一个关键未知量时填写；否则省略整个字段。]

**约束 (Constraints):**
- 范围 (Scope): [数据源、文件范围、系统边界等]
- 格式 (Format): [输出语言、文件类型、响应长度等]
- 风险 (Risk): [哪些东西不能被破坏、修改或泄露]
- 其他 (Other): [时间范围、地区、性能预算等]

**假设 (Assumptions):**
- [因为用户未说明而做出的简短推断]

**是否需要设计阶段 (Needs Design):** [yes | no]
````

说明：

- 中文响应可以使用“中文标题 + 英文原文”的双语展示
- 英文字段名与枚举值仍然是协议锚点（protocol anchors）
- 英文响应应使用纯英文标题，不应把双语标题硬编码到 canonical 英文模板里

## 压缩规则 (Compression Rules)

这些规则用于把原始消息压缩成 brief。

**保留：**

- 底层目标，也就是用户真正想实现的变化
- 能排除整类方案的约束
- 会改变执行路径的领域上下文

**去掉：**

- 填充语气
- 对同一目标的重复表述
- 执行者不需要的长段推理

**将模糊表达改写成可执行表达（vague -> actionable）：**

- “make it better” -> 明确是哪一维更好：performance、readability、UX、security
- “something's wrong” -> 说明观察到的行为与预期行为
- “soon” / “quickly” -> 只有在会影响方案时才追问具体时间
- “the usual format” -> 根据上下文推断，或标成 assumption
- “add Redis to the API” -> 先问这到底要解决什么问题

**当意图含糊时：**

- 如果两种差异很大的解释都成立，就显式写出来
- 只问一个迫使用户做选择的问题
- 依赖该选择的交付物先 defer，不要硬猜

**不要过度修正（Don't over-correct）：**

- 如果用户原始 framing 本身承载了重要意图，就保留它
- 不要引入用户没有暗示的目标或约束
- 如果拿不准某个细节是否关键，就保留并标记为 assumption

## 示例 (Examples)

### 示例 1：Direct

**用户输入：**
> "Extract all TODO comments from the codebase and output them as a markdown list grouped by file."

**Task Brief：**

````
## 任务简报 (Task Brief)

**任务类型 (Task Type):** 变更 (transformation)

**用户目标 (User Goal):**
收集整个代码库中的 TODO 注释，并按文件分组整理成易读的 markdown 列表。

**成功标准 (Success Criteria):**
- 输出按文件分组列出 TODO 注释。
- 每条 TODO 都带有行号。

**交付物 (Deliverables):**
- TODO markdown 列表

**约束 (Constraints):**
- 范围 (Scope): 整个仓库
- 格式 (Format): markdown 输出

**假设 (Assumptions):**
- “TODO” 指字面量 `TODO` 或 `TODO:`。

**是否需要设计阶段 (Needs Design):** no
````

### 示例 2：Clarify

**用户输入：**
> "I need to migrate our auth system to JWT. Can you help me figure out what needs to change?"

**Task Brief：**

````
## 任务简报 (Task Brief)

**任务类型 (Task Type):** 调研 (investigation)

**用户目标 (User Goal):**
识别把当前认证系统迁移到 JWT-based auth 需要变更的范围，同时避免在未确认现状的情况下误判迁移目标。

**成功标准 (Success Criteria):**
- 需要调整的认证组件被识别出来。
- 迁移目标足够清楚，可以进入设计或影响分析。

**交付物 (Deliverables):**
- 认证迁移变更简报

**澄清问题 (Clarifying Question):**
当前认证系统现在用的是什么：session cookies、第三方 identity provider、API keys，还是别的东西？

**约束 (Constraints):**
- 范围 (Scope): 仅限认证相关行为
- 风险 (Risk): 在未确认当前实现之前，不要预设 stateless-token 迁移路径

**假设 (Assumptions):**
- JWT 指的是标准 stateless tokens，而不是 JWE。

**是否需要设计阶段 (Needs Design):** yes
````

### 示例 3：Structured

**用户输入：**
> "Build me a dashboard that shows real-time sales data pulled from our Postgres DB, with a chart for daily revenue and a table for top 10 products. It should update every 30 seconds and be shareable via a link."

**Task Brief：**

````
## 任务简报 (Task Brief)

**任务类型 (Task Type):** 生成 (generation)

**用户目标 (User Goal):**
构建一个可分享的实时销售看板，从 Postgres 展示每日收入图表和热销商品表，并每 30 秒刷新一次。

**成功标准 (Success Criteria):**
- 看板能显示实时收入和热销商品数据。
- 看板每 30 秒刷新一次。
- 看板可通过稳定链接访问。

**交付物 (Deliverables):**
- 实时销售看板

**澄清问题 (Clarifying Question):**
“shareable via a link” 是指无需登录即可公开访问，还是仅对已认证用户开放？

**约束 (Constraints):**
- 范围 (Scope): 仅限看板行为
- 格式 (Format): 浏览器中的 UI
- 风险 (Risk): 不允许写数据库，也不能在前端暴露凭据

**假设 (Assumptions):**
- 已存在包含收入和商品聚合所需字段的 Postgres 数据源。

**是否需要设计阶段 (Needs Design):** yes
````

### 示例 4：Ambiguous Intent

**用户输入：**
> "Our API docs are a mess - can you help fix them?"

**Task Brief：**

````
## 任务简报 (Task Brief)

**任务类型 (Task Type):** 分析 (analysis)

**用户目标 (User Goal):**
改进 API 文档，但目标在两个方向之间存在实质性歧义：

- Interpretation A：审查并重写文档内容本身
- Interpretation B：调整文档工具链或站点呈现方式

**成功标准 (Success Criteria):**
- 在开始执行前确认真正目标是哪一个方向。

**交付物 (Deliverables):**
- 在方向确认前暂缓

**澄清问题 (Clarifying Question):**
你真正想解决的是文档内容问题，还是文档工具与呈现层问题？

**约束 (Constraints):**
- 范围 (Scope): 仅限公共 API 文档
- 风险 (Risk): 对公共文档的修改会影响外部开发者体验

**假设 (Assumptions):**
- “API docs” 指的是面向开发者的 HTTP API 文档，而不是内部笔记。

**是否需要设计阶段 (Needs Design):** yes
````

### 示例 5：Inaccurate Goal

**用户输入：**
> "Add Redis caching to our API endpoints."

**Task Brief：**

````
## 任务简报 (Task Brief)

**任务类型 (Task Type):** 调研 (investigation)

**用户目标 (User Goal):**
降低 API 延迟或后端负载，并把 Redis 当作一个候选技术手段，而不是已经确认的目标。

**成功标准 (Success Criteria):**
- 真实的性能问题被识别出来。
- 任务目标围绕实际瓶颈而不是预设技术方案重写完成。

**交付物 (Deliverables):**
- 性能问题简报

**澄清问题 (Clarifying Question):**
你现在看到的性能问题到底是什么：接口变慢、数据库负载高，还是别的现象？

**约束 (Constraints):**
- 范围 (Scope): 仅限 API 行为
- 风险 (Risk): 在瓶颈未确认前，不要默认缓存就是合适方案

**假设 (Assumptions):**
- 用户想提升性能，但尚未确认瓶颈位置。

**是否需要设计阶段 (Needs Design):** no
````

## 验收标准 (Acceptance Criteria)

一份好的 task brief 应满足这些条件：

1. **Standalone**：执行者只看 brief，也能正确开始；或者至少知道唯一该问的问题。
2. **Intent-preserving**：`User Goal` 抓住的是用户真正想要的结果，而不是表面说法。
3. **Constraint-complete**：缺掉任何一个被保留的约束，都会明显增加走错路的风险。
4. **Non-padded**：简单任务保持简短，不为了“看起来完整”而硬凑字段。
5. **Actionable deliverables**：每个 deliverable 都是具体工件或结果。
6. **Goal-honest**：面对 solution-as-goal 和 symptom-as-goal 时，brief 会诚实地重写底层目标。
7. **Scope-clean**：brief 不会滑向设计路由、任务拆解或实现规划。
8. **Single-question discipline**：需要澄清时，只问一个聚焦问题，而不是发问卷。

以下 brief **不算有用**：

- 只是把用户原话换个说法复述一遍
- 引入了用户没有暗示过的目标或约束
- 把简单请求扩展成冗长澄清会话
- 滑向设计树、子任务拆解或实现计划
