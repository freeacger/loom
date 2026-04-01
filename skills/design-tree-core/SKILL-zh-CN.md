---
name: design-tree-core
description: "设计树（design tree）技能家族的内部共享核心规则。只有在维护设计树系统本身，或者其他设计技能需要共享的派生（derivation）、交接（handoff）、边界或防膨胀（anti-bloat）治理规则时才使用。不要把它用于普通用户设计请求，也不要拿它替代 `design-orchestrator`、`design-structure` 或 `design-refinement`。"
---

# 设计树核心 (Design Tree Core)

## 概览 (Overview)

这个技能是设计树（design tree）技能家族的共享治理核心（shared governance core）。

它不是通用设计技能。
它不是面向普通设计工作的用户入口。
它存在的目的，是定义所有设计树技能都必须遵守的**最小共享契约（minimum shared contract）**。

它只保护那些跨整个家族稳定存在的规则：

- 必需的 `design_state` 字段
- `design_target_type` 词汇表
- 派生标准（derivation criteria）
- 父子交接契约（parent/child handoff contract）
- 防膨胀治理（anti-bloat governance）

## 何时使用 (When to Use)

只有在以下场景使用本技能：

- 维护或修订设计树技能系统本身
- 变更共享的 `design_state` 契约
- 让多个设计技能在 `design_target_type` 行为上保持一致
- 判断是否应从现有设计树派生出一棵新树
- 判断某条共享规则是否应进入公共核心
- 让多个设计技能在边界或交接（handoff）规则上保持一致
- 防止设计树漂移、重复或膨胀

以下情况不要使用：

- 用户需要普通设计路由
- 任务是创建初始设计树
- 任务是细化现有设计树
- 任务是评估一个边界明确的设计决策
- 任务是检查设计是否准备进入规划
- 任务是写设计文档、报告、笔记或计划
- 任务是存放项目特定结论、示例或临时指导

## 核心职责 (Core Responsibility)

这个技能只负责那些同时满足以下条件的规则：

1. 至少被两个设计树技能共享
2. 能稳定存在于时间中
3. 与设计状态（design state）边界、路由、派生、交接或防膨胀治理直接相关
4. 重要到不能默会
5. 共享到不应只属于单个技能

任意一条不满足，都不应放在这里。

## 禁止内容 (Forbidden Content)

以下内容不应加入本技能或其参考文件：

- 项目特定结论
- 一次性讨论结果
- 长篇示例或案例研究
- 详细模板
- 持久化适配器（persistence adapter）或仓库特定的保存流程
- 发布流程细节
- 单技能专属规则
- 面向报告、笔记或计划的内容生产规则
- FAQ 式补丁堆积
- 不改变共享行为的解释性扩写

如果内容有用但不属于核心，就放到别处。

## 准入规则 (Admission Rule)

新内容只有在满足下列所有条件时，才允许进入这个技能：

1. 它影响超过一个设计树技能
2. 它是一条稳定规则，而不是局部权宜修补（workaround）
3. 它会改变或保护共享边界、路由、派生、交接或防膨胀行为
4. 如果省略它，会导致共享漂移或决策不一致
5. 它不能更自然地放到以下任一位置：
   - 某个具体设计技能
   - 某个单技能参考文件
   - eval
   - 示例（example）
   - 设计文档
   - 报告
   - 检查清单（checklist）
   - script

只要有任意一项不满足，就拒绝加入。

## 驱逐规则 (Eviction Rule)

当下列任一情况成立时，内容应从这里迁出：

- 它实际上只被一个技能使用
- 它变成了项目特定内容
- 它主要是解释性的，而不是行为性的
- 它更适合表达为示例（example）、模板（template）、检查清单（checklist）或脚本（script）
- 它让文件变大，但没有增加共享治理价值

不要因为“历史上已经加进来了”就继续保留。

## 派生范围 (Derivation Scope)

本技能可以定义“什么时候一棵设计树应派生成新树”的共享规则。

它**不能**定义任何派生树的完整运行逻辑。
一旦某棵派生树拥有了自己的稳定职责，这部分逻辑就应留在派生树里，而不是这里。

## 共享输出契约 (Shared Output Contract)

设计树技能共享一个主要输出契约：它们产出或更新 `design_state`。

它们**不**共享默认的文件写入契约。
如果某个技能或仓库希望持久化设计文件，这种行为应写在该技能自己的本地参考文件（reference）或适配规则（adapter rules）中，而不是共享核心。

## 输出契约 (Output Contract)

使用本技能时，输出应严格限制在以下一项或多项：

- 共享 `design_state` 澄清
- `design_target_type` 澄清
- 共享规则澄清
- 派生决策标准（derivation decision criteria）
- 交接契约（handoff contract）澄清
- 防膨胀治理指导
- 针对设计树内容的保留 / 迁移 / 派生建议

它不应输出普通设计树。

## 维护规则 (Maintenance Rule)

让这个技能保持小而硬（small and rigid）。

- 优先选择能保住共享行为的最短规则
- 优先把细节迁出，而不是扩写本文件
- 优先用参考文件（reference file），而不是内联堆积
- 优先删除，而不是保留历史杂物

只有当它比依赖它的技能更小、更稳定时，它才是健康的。

## 与其他技能的关系 (Relationship to Other Skills)

- `design-orchestrator` 可在判断是否派生新树时使用本技能
- `design-orchestrator` 可在拒绝缺少 `design_target_type` 的设计流时使用本技能
- `design-structure` 可在创建派生树（derived tree）时使用本技能
- `design-structure` 可在选择正确的目标类型骨架（target-type skeleton）时使用本技能
- `design-refinement` 可在某个分支看起来正演变成独立稳定决策系统时使用本技能
- `design-readiness-check` 只可用它来检测缺失必需状态、树结构漂移或职责混杂

本技能绝不能接管它们的日常职责。

## 参考文件 (Reference Files)

详细共享规则应放在配套参考文件（reference files）中，例如：

- `REFERENCE.md`
- `CHANGELOG.md`

让 `SKILL.md` 保持为严格的入口契约，而不是完整知识库。
