---
name: using-git-worktrees
description: "当开始需要与当前工作区隔离的功能开发，或在执行实现计划之前使用。它会通过合理目录选择与安全验证来创建隔离的 git worktree。"
---

# 使用 Git Worktree (Using Git Worktrees)

## 概览 (Overview)

Git worktree 能在共享同一仓库的前提下创建隔离工作区，使你可以在多个分支上同时工作，而无需来回切换。

**核心原则：** 系统化目录选择 + 安全验证 = 可靠隔离。

**开始时必须声明：** “I'm using the using-git-worktrees skill to set up an isolated workspace.”

## 目录选择流程 (Directory Selection Process)

按以下优先级执行：

### 1. 检查现有目录 (Check Existing Directories)

```bash
# Check in priority order
ls -d .worktrees 2>/dev/null     # Preferred (hidden)
ls -d worktrees 2>/dev/null      # Alternative
```

**如果找到了：** 就用该目录。如果两个都存在，`.worktrees` 优先。

### 2. 检查 CLAUDE.md

```bash
grep -i "worktree.*director" CLAUDE.md 2>/dev/null
```

**如果其中指定了偏好：** 直接使用，不用再问。

### 3. 询问用户 (Ask User)

如果既没有现有目录，也没有 CLAUDE.md 偏好：

```
No worktree directory found. Where should I create worktrees?

1. .worktrees/ (project-local, hidden)
2. ~/.config/loom/worktrees/<project-name>/ (global location)

Which would you prefer?
```

## 安全验证 (Safety Verification)

### 对项目内目录（.worktrees 或 worktrees）

**在创建 worktree 之前，必须确认该目录被忽略：**

```bash
# Check if directory is ignored (respects local, global, and system gitignore)
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**如果没有被忽略：**

按 Jesse 的规则 “Fix broken things immediately”：

1. 在 `.gitignore` 中加入合适规则
2. 提交该修改
3. 再继续创建 worktree

**为什么关键：** 防止 worktree 内容被意外提交进仓库。

### 对全局目录（~/.config/loom/worktrees）

不需要做 `.gitignore` 验证，因为它完全在项目外部。

## 创建步骤 (Creation Steps)

### 1. 检测项目名 (Detect Project Name)

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
```

### 2. 创建 Worktree

```bash
# Determine full path
case $LOCATION in
  .worktrees|worktrees)
    path="$LOCATION/$BRANCH_NAME"
    ;;
  ~/.config/loom/worktrees/*)
    path="~/.config/loom/worktrees/$project/$BRANCH_NAME"
    ;;
esac

# Create worktree with new branch
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

### 3. 运行项目初始化 (Run Project Setup)

自动检测并执行合适的 setup：

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

### 4. 验证干净基线 (Verify Clean Baseline)

运行测试，确认新 worktree 起点是干净的：

```bash
# Examples - use project-appropriate command
npm test
cargo test
pytest
go test ./...
```

**如果测试失败：** 报告失败，并询问是继续还是先调查。  
**如果测试通过：** 报告 worktree 已就绪。

### 5. 汇报位置 (Report Location)

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## 快速参考 (Quick Reference)

| 情况（Situation） | 动作（Action） |
|-----------|--------|
| `.worktrees/` exists | Use it (verify ignored) |
| `worktrees/` exists | Use it (verify ignored) |
| Both exist | Use `.worktrees/` |
| Neither exists | Check CLAUDE.md → Ask user |
| Directory not ignored | Add to .gitignore + commit |
| Tests fail during baseline | Report failures + ask |
| No package.json/Cargo.toml | Skip dependency install |

## 常见错误 (Common Mistakes)

### 跳过 ignore 验证 (Skipping ignore verification)

- **问题：** worktree 内容被跟踪，污染 git status
- **修正：** 对项目内 worktree 一律先跑 `git check-ignore`

### 想当然假设目录位置 (Assuming directory location)

- **问题：** 破坏一致性，违背项目约定
- **修正：** 遵循优先级：existing > CLAUDE.md > ask

### 在测试失败时继续 (Proceeding with failing tests)

- **问题：** 无法区分新 bug 与历史问题
- **修正：** 先报告失败，再取得明确许可

### 硬编码 setup 命令 (Hardcoding setup commands)

- **问题：** 不同工具链项目会直接出错
- **修正：** 根据项目文件自动检测

## 示例工作流 (Example Workflow)

```
You: I'm using the using-git-worktrees skill to set up an isolated workspace.

[Check .worktrees/ - exists]
[Verify ignored - git check-ignore confirms .worktrees/ is ignored]
[Create worktree: git worktree add .worktrees/auth -b feature/auth]
[Run npm install]
[Run npm test - 47 passing]

Worktree ready at /Users/jesse/myproject/.worktrees/auth
Tests passing (47 tests, 0 failures)
Ready to implement auth feature
```

## 红旗信号 (Red Flags)

**绝不要：**

- 在未确认被 ignore 的情况下创建项目内 worktree
- 跳过基线测试验证
- 在测试失败时不问就继续
- 在目录存在歧义时擅自假设
- 跳过 CLAUDE.md 检查

**必须始终：**

- 遵循目录优先级：existing > CLAUDE.md > ask
- 对项目内目录验证 ignore 状态
- 自动检测并运行项目 setup
- 验证测试基线干净

## 集成关系 (Integration)

**被这些技能调用：**

- **`design-readiness-check`** - 当设计通过并进入实现时为必需
- **`writing-plans`** - 在生成或执行会改代码的计划前强烈建议使用
- **`subagent-driven-development`** - 在执行任何任务前为必需
- **`executing-plans`** - 在执行任何任务前为必需
- 任何需要隔离工作区的技能

**配套技能：**

- **`finishing-a-development-branch`** - 工作完成后的清理为必需
