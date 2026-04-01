---
name: requesting-code-review
description: "当任务完成、重大功能实现结束，或在合并前需要确认工作是否满足要求时使用。"
---

# 请求代码评审 (Requesting Code Review)

在问题扩散之前，分发 `loom:code-reviewer` subagent 来尽早发现问题。

**核心原则：** 早 review，常 review。

## 什么时候请求评审 (When to Request Review)

**强制场景：**

- 在 subagent-driven development 中，每个任务结束后
- 完成重大功能后
- 合并到 `main` 之前

**可选但很有价值：**

- 卡住时（引入新视角）
- 重构前（做一次基线检查）
- 修完复杂 bug 后

## 如何请求 (How to Request)

**1. 获取 git SHA：**

```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. 分发 code-reviewer subagent：**

使用 Task 工具，类型为 `loom:code-reviewer`，模板见 `code-reviewer.md`

**占位符：**

- `{WHAT_WAS_IMPLEMENTED}` - 你刚刚实现了什么
- `{PLAN_OR_REQUIREMENTS}` - 它本应做什么
- `{BASE_SHA}` - 起始提交
- `{HEAD_SHA}` - 结束提交
- `{DESCRIPTION}` - 简要摘要

**3. 处理反馈：**

- 立刻修 Critical 问题
- Important 问题必须在继续前修掉
- Minor 问题可以记下来之后处理
- 如果 reviewer 错了，要带着理由反驳

## 示例 (Example)

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch loom:code-reviewer subagent]
  WHAT_WAS_IMPLEMENTED: Verification and repair functions for conversation index
  PLAN_OR_REQUIREMENTS: Task 2 from docs/plans/deployment-plan.md
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types

[Subagent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators]
[Continue to Task 3]
```

## 与工作流的集成 (Integration with Workflows)

**Subagent-Driven Development：**

- 每个任务后都 review
- 在问题叠加前尽早发现
- 修完再进入下一个任务

**Executing Plans：**

- 每个批次（3 个任务）后 review
- 接收反馈，应用，再继续

**Ad-Hoc Development：**

- 合并前 review
- 卡住时 review

## 红旗信号 (Red Flags)

**绝不要：**

- 因为“很简单”而跳过 review
- 忽略 Critical 问题
- 带着未修复的 Important 问题继续
- 和有效的技术反馈硬吵

**如果 reviewer 错了：**

- 用技术理由反驳
- 展示能证明代码正确的代码或测试
- 请求澄清

模板见：[code-reviewer.md](/Users/youjunxin/workspace/tools/loom/skills/requesting-code-review/code-reviewer.md)
