---
name: executing-plans
description: "当你已经有一份成文的实现计划（implementation plan），并要在独立会话中按批执行、且在批次之间做 review checkpoint 时使用。"
---

# 执行计划 (Executing Plans)

## 概览 (Overview)

加载计划，批判性审阅，按批执行任务，并在批次之间汇报供审查。

**核心原则：** 批量执行（batch execution）+ 架构师检查点（checkpoints for architect review）。

**开始时必须声明：** “I'm using the executing-plans skill to implement this plan.”

## 过程 (The Process)

### 第 1 步：加载并审阅计划 (Load and Review Plan)

1. 读取计划文件
2. 批判性审阅计划，识别任何疑问或顾虑
3. 如果有顾虑：开始前先向你的人工协作者提出
4. 如果没有顾虑：创建 TodoWrite，然后继续

### 第 2 步：执行一个批次 (Execute Batch)

**默认：先执行前 3 个任务**

对每个任务：

1. 标记为 `in_progress`
2. 严格按步骤执行（计划已经拆成 bite-sized steps）
3. 按计划要求运行验证
4. 标记为 `completed`

### 第 3 步：汇报 (Report)

当一个批次完成后：

- 展示已实现内容
- 展示验证输出
- 说：“Ready for feedback.”

### 第 4 步：继续 (Continue)

根据反馈：

- 如有需要，先应用修改
- 再执行下一个批次
- 直到完成为止

### 第 5 步：完成开发工作 (Complete Development)

当所有任务都完成并通过验证后：

- 声明：“I'm using the finishing-a-development-branch skill to complete this work.”
- **必需子技能（REQUIRED SUB-SKILL）：** 使用 `loom:finishing-a-development-branch`
- 按该技能流程验证测试、展示选项并执行用户选择

**开发成功完成后，将已执行计划归档：**

```bash
mkdir -p docs/exec-plans/completed
mv docs/exec-plans/active/<filename>.md docs/exec-plans/completed/<filename>.md
```

然后汇报被移动的是哪份计划文件，方便 reviewer 核对归档状态。

## 什么时候停下并求助 (When to Stop and Ask for Help)

**遇到以下情况立即停止执行：**

- 批次中途遇到 blocker（缺依赖、测试失败、指令不清）
- 计划存在致命缺口，导致无法开始
- 你无法理解某条指令
- 验证反复失败

**宁可请求澄清，也不要靠猜。**

## 什么时候回到前面的步骤 (When to Revisit Earlier Steps)

**出现以下情况时，回到 Review（第 1 步）：**

- 协作方根据你的反馈更新了计划
- 基本方案需要重想

**不要硬顶着 blocker 往前冲。**

## 记住 (Remember)

- 先批判性审阅计划
- 严格按计划步骤执行
- 不要跳过验证
- 计划要求引用技能时，要照做
- 批次之间只汇报并等待
- 被阻塞就停下，不要猜
- 未经用户明确同意，绝不要在 `main/master` 上直接开始实现

## 集成关系 (Integration)

**必需工作流技能：**

- **`loom:using-git-worktrees`**：必需，在开始前建立隔离工作区
- **`loom:writing-plans`**：负责生成本技能执行的计划
- **`loom:finishing-a-development-branch`**：在所有批次完成后收尾
