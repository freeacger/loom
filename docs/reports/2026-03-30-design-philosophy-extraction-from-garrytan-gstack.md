# gstack 技能设计思路提炼 (Design Philosophy Extraction from garrytan/gstack)

## 背景 (Context)

gstack 是 Garry Tan（YC CEO）发布的开源项目，定位为"虚拟工程团队"——通过 31 个 SKILL.md 文件将 Claude Code 变成一条完整的软件工厂流水线。本文档提炼其核心设计思路，识别可供 loom 借鉴的模式。

---

## 一、核心设计理念 (Core Design Philosophy)

### 1.1 "Boil the Lake" 哲学

gstack 的首要原则：**AI 让完整性几乎零成本，因此永远做完整的事**。

- "Lake"（可完成的范围）应该被彻底解决
- "Ocean"（跨季度的迁移）应该标记为 out-of-scope
- 这是一条判断边界的原则：不是"能做多少做多少"，而是"如果完整做只多花几分钟，就必须完整做"

**对 loom 的启示：** loom 的 design-readiness-check 已有这个倾向（4 个并行 subagent 做全面检查），但缺少一条显式的"完整性优先"原则来指导其他技能。

### 1.2 "Search Before Building" 三层知识模型

gstack 将知识分三层：
- **Layer 1**: 经过验证的成熟模式——直接使用
- **Layer 2**: 新兴热门方案——需要审视是否是 hype
- **Layer 3**: 第一性原理推理——最有价值，尤其当它推翻了传统智慧时

**对 loom 的启示：** loom 的 `[RESEARCH]` 标记和外部依赖验证已覆盖了 Layer 2 的审视需求，但缺少将这三层知识分级应用到决策过程中的框架。

### 1.3 用户主权 (User Sovereignty)

**AI 推荐，用户决定。** 即使两个模型（Claude + Codex）达成一致，也只是"强信号"而非"命令"。用户始终拥有模型缺乏的上下文。

这体现为一个核心循环：`AI 生成 → 用户验证 → AI 不得跳过验证`。

---

## 二、架构模式 (Architecture Patterns)

### 2.1 模板生成系统 (Template Generation System)

**这是 gstack 与 loom 最大的架构差异。**

```
SKILL.md.tmpl (人写的 prose + 占位符)
       │
       ▼
gen-skill-docs.ts (读取源码元数据)
       │
       ▼
SKILL.md (生成的完整文档，提交到 git)
```

关键占位符：
- `{{PREAMBLE}}` — 所有技能共享的初始化块（更新检查、session 追踪、贡献者模式）
- `{{BROWSE_SETUP}}` / `{{COMMAND_REFERENCE}}` — 浏览器能力注入
- `{{BASE_BRANCH_DETECT}}` — PR 目标分支自动检测
- `{{LEARNINGS_SEARCH}}` / `{{LEARNINGS_LOG}}` — 跨 session 学习注入

**设计决策：** 生成产物提交到 git（而非运行时生成），原因：
1. 技能加载时无需构建步骤
2. CI 可验证产物是否最新
3. git blame 仍然有效

**对 loom 的启示：** loom 当前的图表规范（~250 行）在多个 SKILL.md 中内联重复。gstack 的模板系统是解决此问题的成熟方案。但 loom 的技能规模（19 个）可能还不值得引入完整的模板引擎——**先用文档引用（`@conventions/...`）做轻量去重，规模扩大后再考虑模板化**。

### 2.2 Preamble 分层系统

每个技能在 frontmatter 中声明 `preamble-tier`（1-4），控制注入的 preamble 内容量：

| Tier | 内容 |
|------|------|
| 1 | 最小化：仅版本检查 |
| 2 | + session 追踪 |
| 3 | + 贡献者模式 + AskUserQuestion 格式化 |
| 4 | 完整：+ Search Before Building 哲学注入 |

**设计意图：** 轻量技能（如 `/freeze`、`/unfreeze`）不需要哲学注入和 session 追踪，避免 token 浪费。

**对 loom 的启示：** loom 可以借鉴这个"按需注入"的思路，但不必照搬 4 级分层。当前更实际的做法是区分两类：操作型技能（无 preamble）和设计型技能（注入共享上下文）。

### 2.3 浏览器守护进程 (Browser Daemon)

gstack 的核心技术壁垒：一个长驻的 Chromium 进程通过本地 HTTP 服务器暴露 API。

- 首次调用 ~3s 启动，后续 ~100-200ms
- 元素通过 `@e1`、`@e2` 的 ref 系统寻址（而非 CSS selector）
- 安全模型：仅绑定 localhost + UUID bearer token

**对 loom 的启示：** 这是 gstack 独有的技术投资，loom 不需要复刻。但 gstack 围绕浏览器构建的 `/qa`、`/benchmark`、`/canary` 系列技能的**工作流设计**值得参考——它们展示了如何围绕一个核心能力构建技能生态。

---

## 三、技能设计模式 (Skill Design Patterns)

### 3.1 完整的开发生命周期流水线

gstack 的 31 个技能覆盖了从想法到运维的完整生命周期：

```
Think ──→ Plan ──→ Build ──→ Review ──→ Test ──→ Ship ──→ Reflect
  │         │                    │         │        │         │
  ▼         ▼                    ▼         ▼        ▼         ▼
office    ceo/eng/             review     qa      ship     retro
hours     design                                  land
          review                                  deploy
```

**关键特征：**
- 每个阶段都有专属技能，职责不重叠
- 技能之间通过文件传递状态（design doc → review → qa）
- `/autoplan` 自动串联 CEO → Design → Eng 三轮评审

**对比 loom：** loom 的 design 系列技能覆盖了 Think → Plan 阶段（task-brief → orchestrator → structure → refinement → readiness → plans），但 Review → Test → Ship → Reflect 阶段依赖外部技能或手动流程。

### 3.2 Fix-First 评审模式

`/review` 技能的核心创新：

| 分类 | 行为 |
|------|------|
| **AUTO-FIX** | 直接修复，不问用户 |
| **ASK** | 收集所有需要判断的问题，一次性提交给用户 |

**设计意图：** 最小化打断次数。不是"发现一个问题问一次"，而是"能修的全修了，不能修的攒一批问"。

**对 loom 的启示：** loom 的 design-readiness-check 输出一个"readiness report"，但没有区分"可自动修复"和"需要人判断"的问题。引入 AUTO-FIX / ASK 分类可以提升效率。

### 3.3 Review Readiness Dashboard

`/ship` 技能在执行前检查哪些评审已完成：

```
Review Status
├── CEO Review: ✓ (ran on commit abc123)
├── Eng Review: ✓ (ran on commit abc123)
├── Design Review: SKIPPED (backend-only change)
└── QA: ✗ (not run)
```

并有智能路由：基础设施变更不需要 CEO review，后端变更不需要 design review。

**对 loom 的启示：** loom 的 design-orchestrator 有类似的路由能力（跳过不需要的设计阶段），但缺少一个"全局状态仪表板"来展示当前分支的完成度。

### 3.4 跨模型评审 (Cross-Model Review)

`/codex` 技能获取 OpenAI Codex CLI 的独立评审，然后生成跨模型分析报告。**两个模型达成一致 = 强信号。**

**对 loom 的启示：** 这是一个有趣的"第二意见"模式。当前 loom 没有等价物。可以考虑在高风险决策时引入第二模型的评审，但优先级不高。

### 3.5 自学习机制 (Self-Learning)

`/learn` 技能管理跨 session 记忆。学习内容在两个时机被调用：
- **Review 前**：`{{LEARNINGS_SEARCH}}` 搜索相关的过往经验
- **Review 后**：`{{LEARNINGS_LOG}}` 记录本次发现

**对 loom 的启示：** loom 的 auto memory 系统（`~/.claude/projects/.../memory/`）已覆盖了这个需求，但没有将其系统性地注入到技能工作流中。可以考虑在 design-readiness-check 执行前自动搜索相关的 memory。

---

## 四、与 loom 的关键差异总结 (Key Differences from loom)

| 维度 | gstack | loom |
|------|--------|------|
| **定位** | 全生命周期工厂（Think→Ship→Reflect） | 设计阶段专精（Task→Design→Plan） |
| **技能数量** | 31 个 | 19 个 |
| **技术壁垒** | 浏览器守护进程（Playwright + Bun） | 无（纯 Markdown） |
| **状态管理** | 文件传递（隐式） | 显式 design_state 合约 |
| **模板系统** | 完整的 .tmpl → .md 生成管线 | 无（手写） |
| **共享上下文** | Preamble 分层注入 | 无统一注入机制 |
| **评审模式** | Fix-First（AUTO-FIX / ASK） | Report 式（列出问题） |
| **多模型** | Claude + Codex 交叉评审 | 单模型 |
| **学习机制** | /learn + 模板注入 | auto memory（未注入技能流） |
| **CI 集成** | GitHub Actions 验证 SKILL.md 新鲜度 | pre-push hook 验证一致性 |

---

## 五、可执行的借鉴清单 (Actionable Takeaways for loom)

### 立即可用 (Quick Wins)

1. **在 design-readiness-check 中引入 AUTO-FIX / ASK 分类** — 可自动修复的小问题（如 missing status marker）直接修，需要判断的攒批问
2. **为 design-orchestrator 添加 Review Status Dashboard** — 在路由决策前展示当前设计状态的完成度
3. **在技能中注入 memory 搜索** — 在 design-readiness-check 和 decision-evaluation 执行前搜索相关的 project/feedback memory

### 中期改进 (Medium-term)

4. **引入轻量共享上下文块** — 类似 gstack 的 preamble，但更简单：为 design 系列技能定义一个共享的"设计原则"块（完整性优先、三层知识模型），通过文件引用注入
5. **图表规范去重** — 将内联的 ~250 行 diagram 规则替换为 `@docs/standards/terminal-diagram-style-guide.md` 引用

### 长期考虑 (Long-term)

6. **模板生成系统** — 当技能数量超过 30 且共享内容（preamble + conventions + examples）的维护成本显著时，考虑引入 `.tmpl → .md` 的生成管线
7. **全生命周期扩展** — 逐步补充 Review → Test → Ship → Reflect 阶段的原生技能，形成闭环

---

## 六、验证方法 (Verification)

- 查阅 gstack 仓库源码确认分析准确性：`https://github.com/garrytan/gstack`
- 与 loom 现有的 mattpocock/skills 对比文档交叉验证：`docs/design-decisions/2026-03-30-loom-vs-mattpocock-skills-review.md`
- 实际应用借鉴清单时，用 skill-creator eval 验证改进效果
