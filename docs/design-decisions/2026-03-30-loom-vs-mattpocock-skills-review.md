---
title: Loom vs mattpocock/skills Technical Comparison
status: Active
area: skills/design
description: 技术评审 loom task-brief + design 系列技能与 mattpocock/skills 开源项目，对比双方优劣点，指导 loom 优化方向。
supersedes: ""
superseded_by: ""
authors: blackvoid
model: gpt-5
---

# 技术对比评审：loom design 系列技能 vs mattpocock/skills (Technical Comparison)

## 背景与动机 (Background)

loom 的 task-brief + design 系列技能（7 个技能组成的设计工作流）是一个面向 AI 编程助手的结构化设计系统。mattpocock/skills 是 TypeScript 教育者 Matt Pocock 发布的开源技能集合（18+ 技能），在社区中有较高知名度。本次评审通过对比分析，识别双方优劣点并为 loom 提供可操作的优化建议。

---

## 一、项目概览对比 (Project Overview)

| 维度 | loom (本项目) | mattpocock/skills |
|------|---------------|-------------------|
| **技能数量** | ~30+ (design 系列 7 个) | 18+ |
| **核心定位** | 结构化设计工作流系统 | 个人开发工作流工具集 |
| **技能关系** | 紧密耦合、有状态编排 | 独立松散、无状态组合 |
| **工作流深度** | 深度链式（task-brief → orchestrator → structure → refinement → readiness → plans） | 浅层链式（write-a-prd → prd-to-plan → prd-to-issues） |
| **分发方式** | skills.sh registry + `mise run pull` | npm (`npx skills add`) + skills.sh |
| **技能格式** | 纯 Markdown（无 frontmatter） | YAML frontmatter + Markdown |
| **语言** | 中英双语 | 英文 |

---

## 二、逐维度对比分析 (Dimension-by-Dimension Analysis)

### 2.1 技能格式与结构 (Skill Format & Structure)

**loom 优势：**
- 每个技能职责极其明确，Entry/Exit criteria 清晰
- 共享 `design_state` 概念模型贯穿整个工作流
- 统一的字元图表规范（tree / sequence / state machine / DAG）
- 内置状态标记系统（`[OPEN]`, `[DECISION]`, `[DRAFT]`, `[RESEARCH]`, `✓`, `✗`）

**loom 不足：**
- **无 frontmatter**：缺少 YAML 元数据（name, description, trigger hints）。AI agent 在选择加载哪个技能时只能靠文件路径猜测，无法做高效的 trigger matching
- **技能体积过大**：单文件 SKILL.md 动辄 200-500 行，缺乏分层拆分（loom 没有 REFERENCE.md / EXAMPLES.md 的概念）
- **无 script bundling**：所有操作依赖 AI 即时生成，对于确定性操作（如文件验证、格式检查）没有复用机制

**mattpocock 优势：**
- **YAML frontmatter** 中的 `description` 字段是 trigger matching 的关键（max 1024 chars），明确告诉 agent 何时触发
- **100 行限制原则**：SKILL.md 保持精简，详细内容拆到 REFERENCE.md / EXAMPLES.md
- **Script bundling**：确定性操作打包为脚本（如包管理器检测），节省 token 并提高可靠性
- **Progressive disclosure**：quick start → workflows → advanced 的分层结构

**mattpocock 不足：**
- frontmatter description 的 trigger 描述有时过于宽泛，可能误触发

### 2.2 工作流设计 (Workflow Design)

**loom 优势：**
- **有状态编排**：design-orchestrator 维护 `design_state` 并在技能间路由，这是架构上的重大创新——mattpocock 没有等价物
- **质量门控**：design-readiness-check 是一个完整的多维质量检查关卡（4 个并行 subagent），这在 mattpocock 中完全缺失
- **并行 agent 模式**：design-readiness-check 和 design-decision-audit 都使用并行 subagent 执行检查，效率更高
- **增量文件写入**：design-structure 在确认阶段即时写入文件，防止数据丢失
- **外部依赖管理**：`[RESEARCH]` 标记 + 可行性验证是一个务实且有价值的创新

**loom 不足：**
- **工作流启动成本高**：从 raw request 到 implementation-ready design 需要经过 5-6 个技能接力，对简单任务来说过重
- **缺少快速路径**：没有 "just give me a quick design" 的选项，所有任务都走完整流程
- **交互轮次多**：design-structure 的三阶段确认（problem → scope → assumptions）对经验丰富的用户可能感觉冗长

**mattpocock 优势：**
- **Tracer bullet 哲学**：每个阶段产出可验证的 thin vertical slice，PRD → Plan → Issues 的管线清晰
- **HITL/AFK 标记**：明确区分哪些工作需要人参与，哪些可以自动完成——loom 没有这个区分
- **Relentless interview**：write-a-prd 和 grill-me 的提问策略极其深入，确保在编码前充分理解需求
- **"Design it twice" 原则**：design-an-interface 强制生成 3+ 个 radical different 的方案并对比，避免 first-idea bias

**mattpocock 不足：**
- **无中间状态管理**：技能之间无共享状态，每次都是无状态的——不像 loom 的 design_state
- **无质量门控**：缺少 readiness check，PRD 写完直接进 plan，没有验证设计是否 "够完整"
- **无审计能力**：没有 design-decision-audit 的等价物

### 2.3 决策分析 (Decision Analysis)

**loom 优势：**
- decision-evaluation 是专门的决策分析技能，有明确的比较维度（复杂度、兼容性、风险、性能、可维护性、未来灵活性、可调试性）
- star rating 系统提供直观的量化对比
- 架构拓扑图帮助可视化方案差异

**mattpocock 优势：**
- design-an-interface 的并行 agent 方案更激进——每个 agent 有不同的设计约束（minimize interface / maximize flexibility / optimize common case / specific paradigm），强制产出真正不同的方案
- "Design it Twice" 来自 John Ousterhout 的《A Philosophy of Software Design》，理论基础扎实

**对比结论：**
- loom 的 decision-evaluation 更结构化、更适合有明确选项的决策
- mattpocock 的 design-an-interface 更适合开放式探索、缺少明确选项时的方案发现

### 2.4 并行 Agent 模式 (Parallel Agent Patterns)

**loom：分析型并行** — design-readiness-check 启动 4 个并行 subagent（branch-checker / assumption-checker / failure-checker / risk-checker），每个读取同一个 design tree 并应用独立的分析维度。design-decision-audit 启动 N 个条件模块 auditor。两者都有 fallback 到 inline 执行的机制。模板存储在独立的 `agents/*.md` 文件中。

**mattpocock：生成型并行** — design-an-interface 启动 3+ 个 subagent，每个附加不同的设计约束（minimize / maximize / optimize / inspiration），目的是创造性发散而非验证。subagent 的 prompt 内联在 SKILL.md 中，不使用外部模板文件。

**结论：** loom 的并行模式擅长验证和审计，mattpocock 的并行模式擅长探索和发散。两者互补，loom 应补充生成型并行能力。

### 2.5 状态管理 (State Management)

**loom：** 共享 `design_state`（10 个字段：problem, scope, design_tree, open_branches, decision_nodes, external_dependencies, decisions, risks, validation, status），每个技能拥有特定的读/写权限。支持多 session 设计工作。

**mattpocock：** 隐式状态（通过 conversation history），无共享结构。`prd-to-plan` 依赖用户手动提供 PRD 输出，无程序化 handoff。状态仅在对话上下文中存在。

**结论：** loom 的显式状态合约是重大架构优势，但增加了新用户理解成本。

### 2.6 文档与可发现性 (Documentation & Discoverability)

**loom 不足：**
- 无 frontmatter = 无 trigger hints = agent 难以自动选择正确的技能
- 缺少 EXAMPLES.md = 新用户（或新 agent）的学习曲线陡峭
- CHANGELOG.md 存在但似乎不是强制的

**mattpocock 优势：**
- frontmatter description 是 discoverability 的核心
- write-a-skill 是 meta-skill，教 agent 如何创建新技能，降低了贡献门槛
- 每个 skill 的 description 都包含 trigger 条件（"Use when user wants to..."）

### 2.7 图表规范去重 (Diagram Convention Deduplication)

loom 的图表规范（约 250 行）既存在于 `docs/standards/terminal-diagram-style-guide.md`，又被内联重复到 design-structure、design-readiness-check、design-refinement、decision-evaluation 等多个技能文件中。mattpocock 通过外部引用（如 `[tests.md](tests.md)`）避免了这个问题。

**建议：** 每个 SKILL.md 应引用 conventions 文档而非内联重复规则。

### 2.8 生态与工具链 (Ecosystem & Tooling)

**loom 优势：**
- `mise run release` 自动化发布流程（commit + push + pull）成熟
- pre-push hook 验证 install path 一致性
- `scripts/gen-design-index.sh` 从 frontmatter 生成索引并检查一致性
- `skills-lock.json` 跟踪 16 个技能的哈希值
- 完整的 skill-development.md 工作流文档
- tests/ 目录下的 eval workspace 模式（with_skill / without_skill 对比）

**mattpocock 优势：**
- npm 分发更标准化（`npx skills add`）
- 与 GitHub Issues 深度集成（PRD 直接提交为 Issue）
- 社区知名度更高，有 agent-skills.so registry

---

## 三、双方核心优劣总结 (Strengths & Weaknesses Summary)

### loom 优势（mattpocock 缺失的）

1. **有状态编排器** (design-orchestrator) — mattpocock 没有等价物
2. **质量门控** (design-readiness-check) — 多维并行检查，mattpocock 完全缺失
3. **设计审计** (design-decision-audit) — 条件模块 + 并行 subagent 的审计框架
4. **外部依赖追踪** (`[RESEARCH]` 标记 + 可行性验证) — 务实的创新
5. **统一图表规范** — 跨技能一致的 diagram convention
6. **成熟的工具链** — release pipeline、lock file、eval workspace、consistency check

### loom 劣势（需要改进的）

1. **无 frontmatter / trigger hints** — 影响 skill discoverability
2. **技能体积过大** — 缺乏文件拆分策略
3. **无快速路径** — 简单任务被迫走完整流程
4. **无 HITL/AFK 区分** — 不清楚哪些步骤需要人参与
5. **无 "Design it Twice" 模式** — 缺少强制多方案对比的机制
6. **无 script bundling** — 确定性操作依赖 AI 即时生成
7. **图表规范内联重复** — 多个 SKILL.md 重复约 250 行的 diagram 规则

---

## 四、loom 优化建议 (Optimization Recommendations)

### P0 — 高优先级（直接影响可用性）

#### 1. 添加 YAML frontmatter
为每个 SKILL.md 添加标准化 frontmatter，包含 trigger hints：

```yaml
---
name: design-structure
description: Build the initial design structure from a vague or partially formed idea. Use when the task lacks a clear design tree, scope boundaries, core objects, key flows, or explicit decision points. Trigger when the user has an idea, feature request, or system goal that needs to be turned into a structured design skeleton before deeper refinement.
---
```

**涉及文件：** 所有 `skills/*/SKILL.md`
**参考：** mattpocock 的 frontmatter 格式

#### 2. 文件拆分策略
将超过 100 行的 SKILL.md 拆分为：
- `SKILL.md` — 核心 workflow + quick start（≤ 100 行）
- `REFERENCE.md` — 详细参数、边缘情况、高级用法
- `EXAMPLES.md` — 具体示例

**优先拆分：** design-decision-audit（521 行，当前最长）、task-brief（393 行）、design-readiness-check（152 行）

#### 3. 添加快速路径
在 design-orchestrator 中增加 "express" 模式：
- 对简单任务跳过 interactive confirmation，直接生成设计骨架
- 对已有设计文档的任务跳过 structure，直接进入 refinement 或 readiness-check

**涉及文件：** `skills/design-orchestrator/SKILL.md`

### P1 — 中优先级（提升质量和效率）

#### 4. 引入 HITL/AFK 标记
在每个技能的 workflow steps 中标记：
- **HITL** (Human-in-the-loop)：需要用户输入的步骤
- **AFK** (Away from keyboard)：可以自动完成的步骤

**参考：** mattpocock 的 prd-to-issues

#### 5. 添加 "Design it Twice" 生成型并行模式
在 decision-evaluation 中加入强制多方案对比：
- 对关键决策节点，启动并行 subagent，每个附加不同约束（minimize / maximize / optimize）
- 当前 loom 的并行模式全是分析型的，缺少这种生成型并行

**涉及文件：** `skills/decision-evaluation/SKILL.md`

#### 6. 技能独立使用模式
为每个 design skill 添加 "standalone mode" 入口，不依赖 orchestrator 即可使用。例如 design-refinement 可以直接用于任何包含 design tree 的 markdown 文件。

**涉及文件：** 各 design skill 的 SKILL.md

#### 7. 图表规范去重
将内联在多个 SKILL.md 中的 diagram 规则替换为对 `docs/standards/terminal-diagram-style-guide.md` 的引用，减少维护成本和 token 消耗。

**涉及文件：** design-structure, design-refinement, decision-evaluation, design-readiness-check 的 SKILL.md

### P2 — 低优先级（锦上添花）

#### 8. 统一 skill-creator meta-skill
确保 skill-creator 能指导创建符合上述所有规范的新技能（frontmatter + 拆分 + HITL/AFK + examples）。

**涉及文件：** `skills/skill-creator/SKILL.md`

#### 9. Script bundling 机制
对确定性操作（如 design-readiness-check 中的 checklist 验证）提供可选的脚本模板。

#### 10. GitHub Issues 集成
类似 mattpocock 的 write-a-prd，支持将设计文档直接提交为 GitHub Issue。

---

## 五、执行计划 (Execution Plan)

### Phase 1: frontmatter 规范化
1. 定义 frontmatter schema（name, description, version, triggers）
2. 为所有 7 个 design 技能添加 frontmatter
3. 更新 skill-creator 以自动生成 frontmatter

### Phase 2: 文件拆分
1. 识别超过 100 行的 SKILL.md 文件
2. 将详细内容提取到 REFERENCE.md
3. 添加 EXAMPLES.md（每技能 2-3 个典型用例）

### Phase 3: 快速路径 + HITL/AFK
1. 在 design-orchestrator 中添加 express 模式
2. 在所有 design 技能中标记 HITL/AFK steps

### Phase 4: Design it Twice 增强
1. 在 decision-evaluation 中添加多方案生成模板
2. 或创建独立的 design-an-interface 子技能

### Phase 5: 独立使用模式 + 去重
1. 为每个 design skill 添加 standalone mode 入口
2. 将内联 diagram 规则替换为 conventions 文档引用

---

## 六、验证方法 (Verification)

1. **frontmatter**：确认 agent 能根据 description 正确触发技能
2. **文件拆分**：确认 SKILL.md 行数 ≤ 100，且 wikilink 到 REFERENCE.md 可用
3. **快速路径**：用简单任务测试 express 模式是否能跳过不必要的交互
4. **整体**：运行 `mise run check` 确认 install path 一致
5. **skill-creator eval**：用 skill-creator 的 eval 流程验证新技能质量
