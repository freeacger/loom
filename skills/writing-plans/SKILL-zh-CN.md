---
name: writing-plans
description: "当你已经拿到规格说明（spec）或需求（requirements），并且在动手改代码前需要先写出多步骤执行计划时使用。"
---

# 编写执行计划 (Writing Plans)

## 概览 (Overview)

假设接手执行的人对当前代码库几乎没有上下文，而且审美与判断都不太可靠，你要为他写出一份完整的实现计划（implementation plan）。把他真正需要知道的内容都写出来：每个任务要动哪些文件、可能需要查看哪些代码、测试与文档、如何验证结果。把整件事拆成细小、可执行的任务。遵循 DRY、YAGNI、TDD、频繁提交（frequent commits）。

假设执行者是熟练工程师，但几乎不了解我们的工具链或问题域。也假设他对测试设计并不擅长。

**开始时必须声明：** “I'm using the writing-plans skill to create the implementation plan.”

**上下文：** 这个技能应在设计阶段通过 `design-readiness-check` 之后使用；理想情况下，在通过 `using-git-worktrees` 准备好的独立 worktree 中执行。

**保存位置：** `docs/exec-plans/active/YYYY-MM-DD-<feature-name>.md`

## 细粒度任务拆分 (Bite-Sized Task Granularity)

**每一步只做一个动作，耗时控制在 2 到 5 分钟：**

- “写出失败测试（failing test）” 是一步
- “运行测试并确认它失败” 是一步
- “写出让测试通过的最小实现（minimal implementation）” 是一步
- “再次运行测试并确认通过” 是一步
- “提交（commit）” 是一步

## 计划文档头部 (Plan Document Header)

**每一份计划都必须以如下头部开始：**

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use loom:executing-plans to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## 任务结构 (Task Structure)

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## 记住这些要求 (Remember)

- 始终写出精确文件路径（exact file paths）
- 在计划里给出完整代码，不要只写“加校验逻辑”这种模糊描述
- 命令必须精确，且要写清预期输出（expected output）
- 用 `@` 语法引用相关技能（skills）
- 遵循 DRY、YAGNI、TDD、频繁提交

## 执行交接 (Execution Handoff)

保存计划后，向用户提供执行方式选择：

**“Plan complete and saved to `docs/exec-plans/active/<filename>.md`. Two execution options:”**

**1. Subagent-Driven (this session)** - 我在当前会话里按任务分发全新的 subagent，并在任务之间做 review，适合快速迭代

**2. Parallel Session (separate)** - 在另一个会话里使用 `executing-plans` 批量执行，并带有检查点

**“Which approach?”**

如果用户选择 **Subagent-Driven**：

- **必需子技能（REQUIRED SUB-SKILL）：** 使用 `loom:subagent-driven-development`
- 留在当前会话
- 每个任务使用新的 subagent，并在任务间做 code review

如果用户选择 **Parallel Session**：

- 指导用户在 worktree 中开启一个新会话
- **必需子技能（REQUIRED SUB-SKILL）：** 新会话使用 `loom:executing-plans`
