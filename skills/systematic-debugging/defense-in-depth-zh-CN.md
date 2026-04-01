# 纵深防御式验证 (Defense-in-Depth Validation)

## 概览 (Overview)

当一个 bug 是由无效数据引起时，只在一个点上加校验，看起来似乎够了。但那一个检查会被其他代码路径、重构或 mocks 绕开。

**核心原则：** 在数据流经的**每一层**都做验证，让这个 bug 从结构上变得不可能发生。

## 为什么需要多层 (Why Multiple Layers)

单层验证：`We fixed the bug`  
多层验证：`We made the bug impossible`

不同层抓住不同类型的问题：

- Entry validation 抓绝大多数明显坏输入
- Business logic 抓边界情况
- Environment guards 防止特定上下文中的危险操作
- Debug logging 在其他层失效时保留取证线索

## 四层结构 (The Four Layers)

### 第 1 层：入口校验 (Entry Point Validation)

**目的：** 在 API 边界上拒绝明显无效的输入

### 第 2 层：业务逻辑校验 (Business Logic Validation)

**目的：** 确保数据对当前操作而言是有意义的

### 第 3 层：环境守卫 (Environment Guards)

**目的：** 在特定上下文中阻止危险操作

### 第 4 层：调试性埋点 (Debug Instrumentation)

**目的：** 在问题发生时保留上下文，方便取证

## 如何应用 (Applying the Pattern)

当你定位到一个 bug：

1. **Trace the data flow**：坏值从哪来，到哪被使用
2. **Map all checkpoints**：列出所有经过点
3. **Add validation at each layer**：入口、业务、环境、调试
4. **Test each layer**：尝试绕过某一层，确认下一层还能拦住

## 会话中的例子 (Example from Session)

Bug：空的 `projectDir` 导致 `git init` 跑到源码目录

**数据流：**

1. Test setup → 空字符串
2. `Project.create(name, '')`
3. `WorkspaceManager.createWorkspace('')`
4. `git init` 在 `process.cwd()` 里执行

**新增的四层：**

- 第 1 层：`Project.create()` 校验非空 / 存在 / 可写
- 第 2 层：`WorkspaceManager` 校验 `projectDir` 非空
- 第 3 层：`WorktreeManager` 在测试环境拒绝在 `tmpdir` 外做 `git init`
- 第 4 层：`git init` 前记录 stack trace

**结果：** 1847 个测试全部通过，bug 无法再复现

## 关键洞察 (Key Insight)

四层都需要。实际调试里，每一层都抓到了其他层抓不到的问题：

- 不同代码路径会绕过入口校验
- Mocks 会绕过业务校验
- 跨平台边界情况需要环境守卫
- Debug logging 揭示了结构性误用

**不要只在一个点上加校验。** 把检查铺满整个数据路径。
