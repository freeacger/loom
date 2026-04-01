---
name: task-brief
description: "在执行前，把原始自然语言请求整理成结构化、与模型无关的任务简报（Task Brief）。当请求复杂、多步骤、跨领域、含糊，或将被交给其他模型或 agent 时触发；当用户明确表示“帮我理清我到底需要什么”“我不知道该怎么提这个需求”“我想做 X 但不知道从哪开始”“帮我把这个说清楚”时也应触发。对于意图明确的简单单行请求，例如“修掉第 42 行的拼写错误”或“重命名这个变量”，不要触发。"
---

# 任务简报 (Task Brief)

## 概览 (Overview)

把一条原始自然语言请求整理成一份结构化任务简报（task brief），使任何执行模型在**不阅读原始用户消息**的前提下也能开始工作。

**这个技能本质上是一个任务规格归一化器（task specification normalizer）。** 它的职责是提炼真实目标、补齐缺失约束，并决定下一步该如何推进。它不负责做设计阶段路由或设计拆解（那属于 `design-orchestrator` 及相关设计技能），不负责写实现步骤（那属于 `writing-plans`），也不负责亲自执行任务。

价值很直接：好的 brief 可以减少误解，防止在错误的子问题上浪费时间，并让任务具备可移植性（portable）——另一个模型、agent 或人类可以在冷启动状态下直接接手。

## 何时使用 (When to Use)

**以下场景应触发：**

- 请求包含多个子目标，或优先级顺序不清楚
- 请求跨越多个领域，例如 data + UI + API
- 用户描述的问题未必是真正问题
- 任务将被委派给其他模型或 agent
- 缺少关键上下文时，执行者会被迫做大量高风险假设
- 用户明确要求你帮他澄清自己的请求

**以下场景不要触发：**

- 单一、明确、无歧义的动作，例如 “delete this function”“run the tests”
- 意图清晰且执行路径显而易见的请求
- 针对当前进行中任务的补充澄清消息

如果你拿不准，就问自己一句：**如果执行者只能看到这份 brief、看不到原始消息，他能不能立刻开工？** 如果答案是“能”，那 brief 就足够好了，通常无需继续加深。

## 复杂度分层 (Complexity Tiers)

在写 brief 之前，先把请求分到以下三档之一。这会决定要套多少结构，以及是否需要先问一个问题。

| 层级（Tier） | 信号（Signal） | 响应方式（Response） |
|------|--------|----------|
| **Direct** | 单一目标、范围清晰、没有关键缺失信息 | 写出 brief，将 Execution Mode 设为 `direct`，并立即继续 |
| **Clarify** | 存在一个关键未知量：缺少必要参数、意图在 2 个以上解释之间含糊，或者用户陈述的目标可能并不准确（solution-as-goal、symptom-as-goal、scope anomaly） | 写出 brief，明确暴露歧义，只问一个问题，将 mode 设为 `clarify-first` |
| **Structured** | 多个目标、跨领域、高度含糊，或需要交接 | 写出完整 brief，将 mode 设为 `structured-handoff` 或 `decompose` |

对于 Tier 1（Direct），brief 可以很短，3 到 4 个字段就够了。不要硬凑内容。

**Tier 2 有三种不同子类型，处理方式要区分：**

- *Missing parameter*：你知道目标，只缺一个细节。正常写 User Goal，把未知项列入 Core Questions，并询问缺失值。
- *Ambiguous intent*：目标本身可能指向两种截然不同的事情。在 User Goal 中显式写出 **Interpretation A** 和 **Interpretation B**。让用户二选一，不要静默替他选。
- *Inaccurate goal*：用户说出来的是一个方案、一个症状，或者一个范围明显异常的目标，而不是真实意图。需要识别三类信号：
  1. **Solution-as-goal**：用户点名了某种技术手段，例如 “add Redis caching”，而不是它要解决的问题。你要问：“你真正想解决的是什么问题？”
  2. **Symptom-as-goal**：用户描述的是错误状态，例如 “fix timeout errors”，而不是想达到的结果。你要问：“预期行为是什么？”
  3. **Scope anomaly**：问题天然边界与用户给定范围不匹配，可能过窄也可能过宽。你要问：“这个问题只出现在这里，还是其他区域也会出现？”

识别到这些信号时，在 User Goal 中写出你对**真实底层目标**的最佳猜测，并把它标记为 assumption，然后只问一个澄清问题。不要在未确认的情况下按用户字面说法直接执行。

在写 brief 之前，先快速搜索代码库上下文，查看相关文件、已有模式或错误日志。建立在代码事实上的 brief，通常会比纯靠语义猜测得出更锋利的澄清问题。

## 输出格式 (Output: Task Brief)

始终按以下格式输出 brief。对确实不适用的字段可以省略；只有在字段相关但信息未知时，才标为 `N/A`。

````
## Task Brief

**Task Type:** [analysis | transformation | generation | investigation | orchestration | other]

**User Goal:**
[1-2 sentences. State the real intent, not the surface request. Start with a verb. E.g., "Identify which API endpoints are missing authentication middleware and produce a prioritized fix list."]

**Core Questions:**
- [What must be answered to complete this task?]
- [Include only questions whose answer changes execution — not exhaustive sub-tasks]

**Success Criteria:**
- [How will the executor know the task is done?]
- [Prefer observable outcomes: "a working script", "a diff applied", "a ranked list with rationale"]

**Constraints:**
- Scope: [data source, file range, system boundary, etc.]
- Format: [output language, file type, response length, etc.]
- Risk: [what must not be broken, changed, or leaked]
- Other: [time range, locale, performance budget, etc.]

**Assumptions:**
- [State what you're inferring because the user didn't specify. Keep it short.]

**Execution Mode:** [direct | clarify-first | structured-handoff | decompose]

**Deliverables:**
- [Concrete artifact 1]
- [Concrete artifact 2]
````

说明：

- 模板中的字段名与枚举值应保留原样，避免破坏协议
- 解释文字可用中文，但如果该任务依赖固定英文字段，则以协议字面量优先

## 压缩规则 (Compression Rules)

这些规则用于把原始消息压缩成 brief。目标是在保留意图的同时去掉噪音。

**保留：**

- 底层目标，也就是用户真正希望世界发生什么变化
- 能直接排除整类方案的约束
- 会改变任务处理方式的领域上下文

**去掉：**

- 填充语气，例如 “I was thinking maybe...”“not sure if this is the right way but...”
- 对同一目标的重复表述
- 执行者行动时不需要的长段推理

**将模糊表达改写成可执行表达（vague → actionable）：**

- “make it better” → 明确是哪一维更好：performance、readability、UX、security
- “something's wrong” → 说明观察到的行为与预期行为
- “soon” / “quickly” → 如果会影响方案，需要问具体 deadline
- “the usual format” → 结合上下文推断，或把它标记为 assumption
- “add Redis to the API” → 反问这要解决什么性能问题（典型 solution-as-goal）

**当意图含糊时：**

- 如果一个请求存在两种或以上都成立、但差异重大的解释，不要替用户选一个继续做
- 在 User Goal 里明确写出 “Interpretation A: …” 与 “Interpretation B: …”
- 只问一个能迫使用户做出选择的问题，不要问开放式的 “what do you mean?”
- Deliverables 写成 “deferred until intent confirmed”，不要留空，也不要瞎猜

**不要过度修正（Don't over-correct）：**

- 如果用户的 framing 本身承载了意图，就保留它
- 不要引入用户没有暗示的目标或约束
- 如果拿不准某个细节是否关键，就保留并标记为 assumption

## 执行模式 (Execution Modes)

| 模式（Mode） | 何时使用 |
|------|-------------|
| `direct` | 信息齐全、目标单一，执行者可以立刻开始 |
| `clarify-first` | 只缺一个关键未知量：缺参数、目标在 2 个以上解释之间含糊，或目标本身可能不准确（solution/symptom/scope signal）；只问这一个问题 |
| `structured-handoff` | 任务复杂，但边界已清楚；brief 足够完整，可以交给另一个 agent 执行 |
| `decompose` | 请求里包含 2 个以上相互独立、应分开或并行执行的子任务 |

对于 `clarify-first`：先给出基于最佳努力假设写出的 brief，再提出问题。不要因为用户还没回复，就卡住 brief 的生成。

对于 `decompose`：在 **Sub-Tasks** 小节下列出各个子任务，每个子任务至少要有自己的 Goal 与 Deliverable。

如果子任务之间存在依赖，在 Sub-Tasks 后追加一个字符 DAG，放在无语言标签的代码块中：

```
[Data layer] ──→ [API endpoints]
      │
      └───────→ [Frontend]
[Email service] → [Notifications]
```

**规则：**

- 组件写在 `[brackets]` 中，箭头使用 `──→`
- 当顺序很重要时，可以使用 `│` 与 `▼` 表示纵向流
- 最大宽度：78 字符
- 只有在 3 个以上子任务存在非平凡依赖时才加 DAG

## 示例 (Examples)

### 示例 1：Tier 1（Direct）

**用户输入：**
> "Extract all TODO comments from the codebase and output them as a markdown list grouped by file."

**Task Brief：**

````
## Task Brief

**Task Type:** transformation

**User Goal:**
Collect all TODO comments across the codebase and organize them into a readable markdown list, grouped by file.

**Core Questions:**
- None — intent and scope are clear.

**Success Criteria:**
- A markdown file (or inline output) listing TODOs grouped by filename, with line numbers.

**Constraints:**
- Scope: entire codebase (all files in the repo)
- Format: markdown output

**Assumptions:**
- "TODO" means the literal string `TODO` or `TODO:` in comments (case-insensitive).
- No filtering by age, author, or priority.

**Execution Mode:** direct

**Deliverables:**
- Markdown list of TODO comments grouped by file, with line numbers
````

### 示例 2：Tier 2（Clarify）

**用户输入：**
> "I need to migrate our auth system to JWT. Can you help me figure out what needs to change?"

**Task Brief：**

````
## Task Brief

**Task Type:** investigation + generation

**User Goal:**
Identify what changes are required to replace the current authentication system with JWT-based auth, and produce an actionable change list or implementation plan.

**Core Questions:**
- What does the current auth system use? (session cookies, API keys, OAuth tokens?)
- Should the migration maintain backward compatibility with existing sessions?

**Success Criteria:**
- A list of components/files that need to change, with the nature of each change described.
- Enough detail to begin implementation or hand off to another developer.

**Constraints:**
- Scope: authentication-related code only
- Risk: must not break existing authenticated sessions during cutover

**Assumptions:**
- JWT means standard stateless tokens (not JWE).
- The target stack is server-side (not client-only).

**Execution Mode:** clarify-first

**Deliverables:**
- Impact analysis: which files/modules need to change
- Recommended migration sequence
````

**澄清问题：**
> What does the current auth system use — session-based cookies, a third-party provider, or something else? The answer determines how much of the token issuance and validation logic needs to be rewritten.

### 示例 3：Tier 3（Decompose）

**用户输入：**
> "Build me a dashboard that shows real-time sales data pulled from our Postgres DB, with a chart for daily revenue and a table for top 10 products. It should update every 30 seconds and be shareable via a link."

**Task Brief：**

````
## Task Brief

**Task Type:** generation (orchestration)

**User Goal:**
Build a web dashboard that displays live sales data from a Postgres database, refreshing every 30 seconds, with a revenue chart and a top-products table, shareable via URL.

**Core Questions:**
- Is there a preferred frontend framework, or is a lightweight stack (e.g., plain HTML + Chart.js) acceptable?
- Does "shareable via a link" mean public (no auth) or authenticated sharing?

**Success Criteria:**
- A running web app accessible via browser
- Revenue chart and top-10-products table refresh every 30 seconds with live DB data
- A stable URL that can be shared

**Constraints:**
- Data source: existing Postgres DB (read-only queries assumed)
- Refresh interval: 30 seconds
- Risk: no writes to the DB; no exposure of credentials in client-side code

**Assumptions:**
- Deployment environment is local or a simple server (not a managed cloud service)
- The Postgres schema has a table with at least: product name, sale amount, timestamp

**Execution Mode:** decompose

**Sub-Tasks:**
1. **Data layer** — Write the API endpoint(s) that query Postgres for daily revenue aggregates and top-10 products. Deliverable: a working server endpoint returning JSON.
2. **Frontend** — Build the dashboard page with a chart and table that poll the API every 30 seconds. Deliverable: a working HTML/JS page.
3. **Sharing** — Make the dashboard accessible at a stable URL. Deliverable: deployment instructions or a running dev server with a shareable link.

**Deliverables:**
- Backend API endpoint(s)
- Frontend dashboard page
- Working shareable URL
````

### 示例 4：Tier 2（Ambiguous Intent）

**用户输入：**
> "Our API docs are a mess — can you help fix them?"

**Task Brief：**

````
## Task Brief

**Task Type:** unclear — pending intent confirmation

**User Goal:**
Improve the API documentation, but the target outcome is ambiguous between two substantially different directions:

- **Interpretation A — Content**: the docs exist but are inaccurate, incomplete, or hard to follow. Goal: audit and rewrite the documentation content itself (endpoints, parameters, examples, error codes).
- **Interpretation B — Tooling/Presentation**: the docs are technically present but poorly organized or served via an outdated tool. Goal: migrate to a better doc platform (e.g., Swagger UI, Redoc, Mintlify) or restructure the site layout.

These require different executors, different files touched, and different success criteria.

**Core Questions:**
- Which direction: fix the content, or fix the tooling/presentation?

**Success Criteria:**
- Deferred until intent is confirmed.

**Constraints:**
- Scope: API documentation only (not internal wikis, READMEs, or code comments unless specified)
- Risk: changes to public-facing docs may affect external developer experience

**Assumptions:**
- "API docs" means developer-facing HTTP API reference, not internal design docs.
- There is an existing doc artifact to work from (not a greenfield write from scratch).

**Execution Mode:** clarify-first

**Deliverables:**
- Deferred until intent is confirmed.
````

**澄清问题：**
> Is the core problem the **content** (missing endpoint descriptions, inaccurate examples, undocumented error codes) or the **presentation** (outdated tooling, poor structure, hard to navigate)? The answer determines whether we start by auditing existing docs or by evaluating tooling options.

### 示例 5：Tier 2（Inaccurate Goal）

**用户输入：**
> "Add Redis caching to our API endpoints."

**Task Brief：**

````
## Task Brief

**Task Type:** investigation + transformation

**User Goal:**
Reduce API response latency (assumed — user stated a specific caching technique rather than the problem it solves).

**Core Questions:**
- What performance problem is prompting this — high latency on specific endpoints, high DB load, or slow responses under heavy traffic?

**Success Criteria:**
- Identified performance bottleneck and an appropriate mitigation strategy (which may or may not be Redis).

**Constraints:**
- Scope: API layer
- Risk: no data consistency issues introduced by caching

**Assumptions:**
- The user wants faster API responses and believes Redis is the solution. The actual bottleneck has not been confirmed.

**Execution Mode:** clarify-first

**Deliverables:**
- Deferred until the performance problem is confirmed.
````

**澄清问题：**
> What performance problem are you seeing — slow endpoints under load, high database query times, or something else? Redis caching is one option, but the right fix depends on where the bottleneck actually is.

## 验收标准 (Acceptance Criteria)

一份好的 task brief 应满足以下检查项：

1. **Standalone**：执行者只看 brief、不看原始消息，也能开始工作；或者至少知道唯一应该问的那个问题是什么。
2. **Intent-preserving**：User Goal 抓住了用户真正想要的东西，而不只是他表面的措辞。
3. **Constraint-complete**：任何一旦缺失就会导致执行走错路的约束，都已被包含。
4. **Non-padded**：没有为了“看起来完整”而硬凑字段。简单任务写 3 个字段是对的，为同一个简单任务写 8 个字段反而是过度设计。
5. **Actionable deliverables**：每个 deliverable 都是具体工件，例如 “a working script”，而不是空泛结果如 “something that helps with the problem”。
6. **Goal-honest**：User Goal 反映的是底层问题，而不只是用户说出的技术手段或错误现象。如果目标看起来只是某个方案或症状，brief 必须显式指出并要求确认。

以下 brief **不算有用**：

- 只是把用户原话换了个说法复述一遍
- 引入了用户没有暗示过的目标或约束
- 对一个简单请求开启 6 个问题的澄清会话
- 泛化到几乎适用于任何任务，例如 “deliverable: results”
