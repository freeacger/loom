---
name: design-readiness-check
description: "检查一个设计是否已经完整到足以进入实现规划（implementation planning）。当设计看起来基本完成，并且需要做最终就绪性评审（readiness review），检查是否缺分支、假设薄弱、风险未解、失败处理不全、验证缺口或非功能性遗漏时使用。在调用 `writing-plans` 之前，或当用户询问当前设计是否可以开始实现时触发。本技能不用于审计外部设计文档，也不替代初始设计工作。"
---

# 设计就绪性检查 (Design Readiness Check)

## 概览 (Overview)

这个技能是设计工作与实现规划之间的质量门（quality gate）。

它只回答一个问题，而且必须回答得清楚：当前设计是否已经完整到可以进入 `writing-plans`？

它不是 `design-decision-audit` 的替代品。后者审计独立存在的设计或计划文档；本技能检查的是一个进行中的设计工作流，在进入规划前是否已就绪。

## 何时使用 (When to Use)

在以下情况下使用：

- 设计看起来已经基本完成
- 下一步可能就是 `writing-plans`
- 用户问当前设计是否已经可以开始实现
- 剩余担忧是完整性，而不是发现阶段问题

以下情况不要使用：

- 设计树还不存在
- 主要分支仍然模糊
- 核心决策仍未解决
- 用户要的是对外部设计文档做通用审计
- 设计状态（design state）中缺少 `design_target_type`

## 工作流 (Workflow)

### 阶段 A：上下文准备 (Phase A: Context Preparation)

目标：加载设计状态（design state），并为并行检查组装上下文。

1. 从对话上下文加载当前 `design_state`。
2. 读取设计树内容及所有相关上下文，包括 `open_branches`、`decision_nodes`、`risks` 和 `validation` 状态。
3. 如果 `design_state` 不存在，或设计树（design tree）为空，立刻返回 `NOT READY`，并交接给 `design-structure`。
4. 如果缺少 `design_target_type`，立刻返回 `NOT READY`，并把它列为阻塞性的缺失必需状态。
5. 组装上下文包（context package），包含：设计树文本、开放分支、决策节点、现有风险、验证项以及 `design_target_type`。
6. 使用 `../design-tree-core/REFERENCE.md` 中的共享规则做一次轻量级结构完整性检查（structural integrity check），关注：
   - 一棵树里职责混杂
   - 父子所有权混乱
   - 同一分支上出现重复的父子逻辑
   - 明显本应派生、却仍被内联保留的分支

### 阶段 B：并行就绪性检查 (Phase B: Parallel Readiness Checks)

目标：使用专用子智能体（subagent）并行执行四项独立检查。

7. 启动四个并行 Sonnet 子智能体（subagent），每个子智能体使用一个检查智能体模板（checker agent template）：
   - **branch-checker**：读取 `skills/design-readiness-check/agents/branch-checker.md`，填充 `{{DESIGN_TREE}}` 与 `{{CONTEXT}}`
   - **assumption-checker**：读取 `skills/design-readiness-check/agents/assumption-checker.md`，填充 `{{DESIGN_TREE}}` 与 `{{CONTEXT}}`
   - **failure-checker**：读取 `skills/design-readiness-check/agents/failure-checker.md`，填充 `{{DESIGN_TREE}}` 与 `{{CONTEXT}}`
   - **risk-checker**：读取 `skills/design-readiness-check/agents/risk-checker.md`，填充 `{{DESIGN_TREE}}` 与 `{{CONTEXT}}`

8. 收集四个子智能体的结果。

**回退方案（Fallback）：** 如果任何子智能体失败或超时，由主智能体（main agent）按对应智能体模板（agent template）的 rubric 内联完成该项检查。

### 阶段 C：结论综合 (Phase C: Verdict Synthesis)

目标：把各项检查结果合成为明确的就绪性结论（readiness judgment）。

9. 把各个子智能体的 `status` 映射到就绪性检查清单（readiness checklist）：
   - required-state check → “Design target type present”
   - branch-checker → “Design tree present” 与 “Key branches refined”
   - assumption-checker → “Decisions resolved”（如果假设（assumptions）仍未解决）
   - failure-checker → “Failure paths documented” 与 “Validation strategy defined”
   - risk-checker → “Blocking risks mitigated”
   - structural integrity check → “Structural integrity preserved”

10. 按 Diagram Conventions 构建一个带 `✓/✗` 的检查清单图（checklist diagram）。

11. 判定结论：
   - **READY**：required state 存在，四项检查全部返回 `pass`，且没有阻塞性的结构完整性问题
   - **NOT READY**：required state 缺失、任意检查返回 `fail`，或存在阻塞性的结构完整性问题

12. 如果是 `NOT READY`，根据失败项决定交接目标：
   - required-state 失败 → 交给 `design-structure`
   - branch-checker 失败 → 交给 `design-structure`（缺分支）或 `design-refinement`（分支太弱）
   - assumption-checker 失败 → 交给 `design-refinement`（需要补充假设）
   - failure-checker 失败 → 交给 `design-refinement`（需要补失败路径）
   - risk-checker 失败 → 交给 `decision-evaluation`（风险相关决策未解）或 `design-refinement`（风险说明太弱）
   - 结构完整性检查失败 → 交给 `design-orchestrator`（重新路由所有权）、`design-structure`（派生子树）或 `design-refinement`（收缩重复内联逻辑）

13. 用新信息更新 `design_state`：
   - `status.ready_for_planning`：true 或 false
   - `status.blocking_issues`：失败检查生成的列表
   - 如果有新信息，也更新 `open_branches`、`risks`、`validation`
   - 如果当前工作流包含已落盘的设计文件，还要让文档状态与结论保持一致：NOT READY 时保持 `draft`，READY 时升级为 `ready-for-planning`

14. 返回明确结论与检查清单图（checklist diagram）。绝不要说 “probably ready”。

## 就绪标准 (Readiness Standard)

只有满足以下条件，设计才算准备好进入规划（ready for planning）：

- 存在 `design_target_type`
- 主设计树存在
- 关键分支对于当前目标类型而言，已经细化到足以指导实现
- 重要决策节点已经解决，或带着可接受理由被显式延期
- 失败路径与验证策略没有缺失
- 阻塞性风险要么已被缓解，要么已被清楚承认
- 树的职责没有混到足以破坏路由清晰度

## 预期输出 (Expected Outputs)

产出或更新一个 `design_state`，至少包含：

- `design_target_type`
- `open_branches`
- `risks`
- `validation`
- `status.ready_for_planning`
- `status.blocking_issues`

并且始终返回一个明确结果：

- ready for planning
- not ready for planning

如果当前工作流包含已落盘的设计文件，文档状态也必须明确：

- 设计未就绪时保持 `draft`
- readiness gate 通过后升级为 `ready-for-planning`

## 图表示意规范 (Diagram Conventions)

用无语言标签的代码块，以状态清单（status checklist）的形式呈现就绪性结论：

```
Readiness Check
├── Design target type present   ✓
├── Design tree present          ✓
├── Key branches refined         ✓
├── Decisions resolved           ✗ (storage choice pending)
├── Failure paths documented     ✓
├── Validation strategy defined  ✓
├── Blocking risks mitigated     ✗ (migration cutover risk)
└── Structural integrity preserved ✓

Verdict: NOT READY — 2 blocking issues
```

**规则：**

- 使用 `✓`（通过）和 `✗`（失败），失败项要带内联原因
- 最大宽度：78 字符
- 就绪性结论（readiness verdict）中始终包含这份检查清单

## 进入与退出条件 (Entry and Exit Criteria)

进入条件：

- 设计接近完成
- 下一步很可能是实现规划

退出条件：

- 你已经给出清晰的就绪性结论
- 如果设计未就绪，你已经识别出下一步该路由到哪里

## 交接规则 (Handoff Rules)

- 只有在设计明确 ready 时，才交给 `writing-plans`
- 当基础分支仍缺失时，交给 `design-structure`
- 当重要分支已存在但仍然很弱时，交给 `design-refinement`
- 当真正阻塞点是未解决的决策节点时，交给 `decision-evaluation`
- 当真正阻塞点是树的所有权或路由漂移，而不是分支薄弱时，交给 `design-orchestrator`
- 缺少 `design_target_type` 是立即阻塞，不是软警告
- 永远不要给出 “probably ready” 这种模糊回答，结论必须明确
