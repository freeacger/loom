# 提炼 mattpocock/skills 的技能设计思路 (Design Philosophy Extraction from mattpocock/skills)

## 上下文 (Context)

分析 [mattpocock/skills](https://github.com/mattpocock/skills) 仓库的设计理念，与本项目 loom 的技能体系进行对比，提炼可借鉴的设计思路。mattpocock/skills 包含 18 个技能，涵盖规划设计、开发、工具设置和写作知识四大类。

---

## 核心设计理念 (Core Design Philosophy)

### 1. 深模块思想 (Deep Module Philosophy)
- 源自 John Ousterhout《A Philosophy of Software Design》
- 贯穿多个技能：TDD、improve-codebase-architecture、design-an-interface
- **核心原则**：小接口、大实现——技能的触发条件简洁，但内部工作流程丰富
- **loom 对比**：loom 也遵循类似思路，但未显式引用这一哲学框架

### 2. 垂直切片优于水平分层 (Vertical Slices over Horizontal Layers)
- 最核心的设计模式，几乎渗透到所有技能
- TDD: "一个测试 → 一个实现 → 重复"
- prd-to-plan: "每个阶段交付一条完整的全层路径"
- request-refactor-plan: "每个重构步骤尽可能小"
- **反模式被显式标注**：水平切片（先做完一整层再做下一层）被明确否定
- **loom 对比**：loom 的 `writing-plans` 和 `executing-plans` 也有类似思路，但未将其上升为跨技能的统一原则

### 3. 持久性优于精确性 (Durability over Precision)
- 输出物（GitHub Issue、计划文档）**不引用**文件路径、行号、函数名等会因重构而失效的实现细节
- 改用行为（behavior）和契约（contract）来描述
- triage-issue: "只建议能经受住彻底重构的修复方案"
- **loom 对比**：loom 未显式采用此原则，部分技能产出中仍包含具体文件路径

### 4. 最少打扰用户 (Minimal User Interruption)
- 先调查后提问，而非先提问
- triage-issue: "最多问一个问题"，然后立即调查
- qa: "最多 2-3 个简短澄清问题"
- **loom 对比**：loom 的 `task-brief` 也有分层策略（Direct/Clarify/Structured），但部分技能仍倾向于先问再做

### 5. 给出明确立场 (Opinionated Recommendations)
- 不呈现中性菜单，而是在探索后给出强烈推荐
- improve-codebase-architecture: "要有主见——用户想要的是你的专业判断，而非选项列表"
- **loom 对比**：loom 的 `design-orchestrator` 更偏向路由分发，较少表达"推荐"立场

---

## 架构模式 (Architectural Patterns)

### 1. 扁平自包含目录 (Flat Self-Contained Directories)
- 无全局配置、无构建步骤、技能目录之间无硬依赖
- 每个技能目录独立可寻址：`mattpocock/skills/<name>`
- **loom 相同**：也采用扁平结构，但 loom 额外有 `skills-lock.json` 和 mise 任务链

### 2. 渐进披露 (Progressive Disclosure)
- SKILL.md 包含核心工作流和决策逻辑
- 详细参考材料拆分到 REFERENCE.md、专题 .md、scripts/ 等
- 100 行阈值规则：SKILL.md 超过约 100 行时拆分
- TDD 技能是典范：6 个文件（deep-modules.md, mocking.md, tests.md, refactoring.md, interface-design.md）
- **loom 对比**：loom 采用 agents/ 子目录存放子代理提示模板，这是 mattpocock 未采用的独有模式

### 3. 并行子代理探索 (Parallel Sub-Agent Divergent Exploration)
- design-an-interface: 派生多个子代理，各带不同设计约束（最少方法、最大灵活性、常见场景优化、Ports & Adapters）
- improve-codebase-architecture: "并行派生 3+ 个子代理，每个必须产出截然不同的接口"
- 各子代理收到独立技术简报，结果按序呈现后综合比较
- **loom 对比**：loom 的 `subagent-driven-development` 和 agents/ 模板提供了更结构化的子代理机制（含 tools、model 字段），mattpocock 的方式更轻量

### 4. GitHub Issue 作为主要产出 (GitHub Issue as Primary Output)
- 多个技能的终态产出是自动创建的 GitHub Issue（`gh issue create`），不需用户先行审阅
- write-a-prd、triage-issue、improve-codebase-architecture、request-refactor-plan、qa、prd-to-issues
- 每个技能内嵌结构化 issue 模板
- **loom 对比**：loom 更偏向文档/计划输出，较少直接创建 issue

### 5. 确定性脚本捆绑 (Bundled Deterministic Scripts)
- 对可重复的确定性操作，捆绑 shell 脚本而非让 agent 每次生成
- git-guardrails: `block-dangerous-git.sh` 读取工具输入 JSON，匹配危险 git 模式
- 接入 Claude Code 的 PreToolUse hook 系统
- **loom 对比**：loom 也有 scripts/ 和 mise tasks，但更偏向生命周期管理（publish/pull/check），而非运行时行为防护

---

## 技能组合方式 (Skill Composition)

### mattpocock：隐式语义链接
- 无正式依赖声明，通过共享词汇和工作流衔接组合
- 流水线：`write-a-prd` → `prd-to-plan` / `prd-to-issues`
- 嵌套调用：`grill-me` 被 `write-a-prd` 的"深度访谈"步骤内联调用
- 共享方法论：`triage-issue` 的修复计划遵循 `tdd` 的 RED-GREEN 方法

### loom：显式引用 + 编排器
- `loom:<skill-name>` 显式跨引用语法
- `design-orchestrator` 作为纯路由/协调器分发到专门技能
- 形成有向管线：`task-brief` → `design-orchestrator` → `design-*` → `design-readiness-check` → `writing-plans` → `executing-plans`
- 有 `Related skills` 章节

**差异总结**：mattpocock 靠约定和自然语言隐式组合；loom 靠显式引用和编排器显式组合。各有优劣——隐式更灵活但难追踪，显式更清晰但更刚性。

---

## 值得借鉴的设计要点 (Actionable Takeaways for Loom)

| # | 要点 | 说明 | 优先级 |
|---|------|------|--------|
| 1 | **垂直切片作为跨技能统一原则** | 在 loom 的规划和实现类技能中显式声明此原则，而非各技能零散体现 | 高 |
| 2 | **持久性输出规则** | 技能产出的文档/issue 中避免硬编码文件路径和行号，改用行为和契约描述 | 高 |
| 3 | **100 行拆分阈值** | 为 SKILL.md 设置明确的体量阈值，超过则拆分到补充文件 | 中 |
| 4 | **"先做后问"模式** | 调查型技能应先探索代码库，再向用户提问——基于代码事实提出更精准的问题 | 中 |
| 5 | **自动创建 Issue 的产出模式** | 部分技能（如 triage、QA）可将结果直接创建为 GitHub Issue，降低人工转录成本 | 低 |
| 6 | **运行时行为防护脚本** | 借鉴 git-guardrails 模式，将防护性脚本捆绑进技能并接入 hook 系统 | 低 |

---

## 交付物 (Deliverables)

1. 本分析文档（plan file）
2. 可选后续：将分析结果归档到 `docs/design-decisions/` 目录

## 验证方式 (Verification)

- 与 mattpocock/skills 仓库的实际内容进行交叉验证
- 与 loom 现有技能结构进行对比确认
