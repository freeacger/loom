# 根因追踪 (Root Cause Tracing)

## 概览 (Overview)

很多 bug 会在调用栈深处才表现出来，例如：`git init` 跑在错误目录、文件创建在错误位置、数据库用错路径打开。你的本能会想在报错点修，但那只是修症状。

**核心原则：** 沿调用链向后追，直到找到原始触发点（original trigger），再在源头修复。

## 何时使用 (When to Use)

**适用场景：**

- 错误出现在执行链深处，而不是入口点
- stack trace 很长
- 不清楚坏数据最早从哪里来
- 需要找出究竟是哪段代码或哪条测试触发了问题

## 追踪过程 (The Tracing Process)

### 1. 观察症状 (Observe the Symptom)

```
Error: git init failed in /Users/jesse/project/packages/core
```

### 2. 找到直接原因 (Find Immediate Cause)

问：**是哪段代码直接导致了它？**

### 3. 继续追：是谁调用了它？ (Ask: What Called This?)

沿调用链一级一级往上找：

`WorktreeManager.createSessionWorktree(projectDir, sessionId)`  
→ `Session.initializeWorkspace()`  
→ `Session.create()`  
→ 测试里的 `Project.create()`

### 4. 继续往上追值的来源 (Keep Tracing Up)

例如：

- `projectDir = ''`（空字符串）
- 空字符串作为 `cwd` 会解析到 `process.cwd()`
- 于是命中了源码目录

### 5. 找到原始触发点 (Find Original Trigger)

真正的问题不在 `git init`，而在更上游：

```typescript
const context = setupCoreTest(); // Returns { tempDir: '' }
Project.create('name', context.tempDir); // Accessed before beforeEach!
```

## 当人工追踪不够时：加 Stack Trace (Adding Stack Traces)

如果你靠读代码追不出来，就加 instrumentation：

```typescript
async function gitInit(directory: string) {
  const stack = new Error().stack;
  console.error('DEBUG git init:', {
    directory,
    cwd: process.cwd(),
    nodeEnv: process.env.NODE_ENV,
    stack,
  });

  await execFileAsync('git', ['init'], { cwd: directory });
}
```

**关键点：**

- 在测试里用 `console.error()`，不要用可能被吞掉的 logger
- 在危险操作**之前**记录，不要等失败之后

然后：

```bash
npm test 2>&1 | grep 'DEBUG git init'
```

分析 stack trace：

- 看测试文件名
- 看具体触发行号
- 找出是否是同一类模式反复出现

## 如何找出“哪条测试污染了环境” (Finding Which Test Causes Pollution)

如果污染只在测试里发生，但你不知道是哪条测试触发的：

使用本目录下的二分脚本 `find-polluter.sh`：

```bash
./find-polluter.sh '.git' 'src/**/*.test.ts'
```

它会逐条运行测试，并在找到第一个 polluter 时停下。

## 真实示例：空 projectDir (Real Example: Empty projectDir)

**症状：** `.git` 被创建在 `packages/core/` 源码目录中

**追踪链：**

1. `git init` 在 `process.cwd()` 中运行 ← `cwd` 为空
2. `WorktreeManager` 收到空 `projectDir`
3. `Session.create()` 把空字符串继续传下去
4. 测试在 `beforeEach` 前访问了 `context.tempDir`
5. `setupCoreTest()` 初始返回 `{ tempDir: '' }`

**根因：** 顶层变量初始化过早读取了空值

**修复：** 把 `tempDir` 改成 getter；如果在 `beforeEach` 之前访问就直接抛错

**同时补上纵深防御：**

- 第 1 层：`Project.create()` 校验目录
- 第 2 层：`WorkspaceManager` 校验非空
- 第 3 层：`NODE_ENV` guard 拒绝在 `tmpdir` 外执行 `git init`
- 第 4 层：`git init` 前记录 stack trace

## 关键原则 (Key Principle)

**绝不要只修报错点。**  
沿调用链一直往回追，找到原始触发点，再在源头修。

## Stack Trace 提示 (Stack Trace Tips)

- 在测试里用 `console.error()`，不要用 logger
- 在危险操作前记录，而不是失败后
- 日志要包含上下文：目录、cwd、环境变量、时间
- 用 `new Error().stack` 保留完整调用链

## 实际效果 (Real-World Impact)

来自 2025-10-03 的一次调试会话：

- 通过 5 层追踪找到根因
- 在源头修复（getter validation）
- 再加上 4 层防御
- 1847 个测试全部通过，零污染
