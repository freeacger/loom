---
name: finishing-a-development-branch
description: "当实现已经完成、所有测试都通过，并且你需要决定如何集成这份工作时使用。本技能通过结构化选项引导开发收尾，例如本地合并、创建 PR 或清理分支。"
---

# 完成开发分支 (Finishing a Development Branch)

## 概览 (Overview)

通过展示清晰选项并处理用户选择，引导开发工作收尾。

**核心原则：** 先验证测试 → 再展示选项 → 再执行选择 → 最后清理。

**开始时必须声明：** “I'm using the finishing-a-development-branch skill to complete this work.”

## 过程 (The Process)

### 第 1 步：验证测试 (Verify Tests)

**在展示选项之前，先确认测试通过：**

```bash
# Run project's test suite
npm test / cargo test / pytest / go test ./...
```

**如果测试失败：**

```
Tests failing (<N> failures). Must fix before completing:

[Show failures]

Cannot proceed with merge/PR until tests pass.
```

到此停止。不要进入第 2 步。

**如果测试通过：** 继续第 2 步。

### 第 2 步：确定基线分支 (Determine Base Branch)

```bash
# Try common base branches
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

或者直接询问：`This branch split from main - is that correct?`

### 第 3 步：展示选项 (Present Options)

**只展示以下 4 个选项，不能多也不能少：**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

**不要额外解释。** 选项必须简洁。

### 第 4 步：执行选择 (Execute Choice)

#### 选项 1：本地合并 (Merge Locally)

```bash
# Switch to base branch
git checkout <base-branch>

# Pull latest
git pull

# Merge feature branch
git merge <feature-branch>

# Verify tests on merged result
<test command>

# If tests pass
git branch -d <feature-branch>
```

然后进入：Cleanup worktree（第 5 步）

#### 选项 2：推送并创建 PR (Push and Create PR)

```bash
# Push branch
git push -u origin <feature-branch>

# Create PR
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets of what changed>

## Test Plan
- [ ] <verification steps>
EOF
)"
```

然后进入：Cleanup worktree（第 5 步）

#### 选项 3：保持现状 (Keep As-Is)

汇报：`Keeping branch <name>. Worktree preserved at <path>.`

**不要清理 worktree。**

#### 选项 4：丢弃工作 (Discard)

**必须先确认：**

```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

等待用户给出精确确认。

如果确认：

```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

然后进入：Cleanup worktree（第 5 步）

### 第 5 步：清理 Worktree (Cleanup Worktree)

**适用于选项 1、2、4：**

先检查当前是否在 worktree 中：

```bash
git worktree list | grep $(git branch --show-current)
```

如果是：

```bash
git worktree remove <worktree-path>
```

**对于选项 3：** 保留 worktree。

## 快速参考 (Quick Reference)

| 选项（Option） | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | ✓ | - | - | ✓ |
| 2. Create PR | - | ✓ | ✓ | - |
| 3. Keep as-is | - | - | ✓ | - |
| 4. Discard | - | - | - | ✓ (force) |

## 常见错误 (Common Mistakes)

**跳过测试验证**
- **问题：** 把坏代码合并进来，或者创建一个失败的 PR
- **修正：** 在展示选项前始终先验证测试

**开放式提问**
- **问题：** “What should I do next?” → 太模糊
- **修正：** 严格给出 4 个结构化选项

**自动清理 worktree**
- **问题：** 在用户可能还需要它时删掉 worktree（例如选项 2、3）
- **修正：** 只在需要的选项里清理

**丢弃前不确认**
- **问题：** 误删工作
- **修正：** 强制要求键入 `discard`

## 红旗信号 (Red Flags)

**绝不要：**

- 在测试失败时继续
- 不验证合并结果就 merge
- 未经确认删除工作
- 未经明确请求就 force-push

**必须始终：**

- 在展示选项前先验证测试
- 严格展示 4 个选项
- 对选项 4 取得键入式确认
- 按规则清理 worktree

## 集成关系 (Integration)

**被谁调用：**

- **`subagent-driven-development`**（第 7 步）- 所有任务完成后
- **`executing-plans`**（第 5 步）- 所有批次执行结束后

**配套技能：**

- **`using-git-worktrees`** - 清理由该技能创建的 worktree
