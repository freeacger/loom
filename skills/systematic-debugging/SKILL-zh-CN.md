---
name: systematic-debugging
description: "当你在调试 bug、测试失败、构建失败、性能回退或其他异常行为，并且在提出修复前需要先做根因调查（root-cause investigation）时使用。用户只要说要 debug、调查为什么坏了，或找出技术问题来源，就应触发。"
---

# 系统化调试 (Systematic Debugging)

## 概览 (Overview)

随机修补既浪费时间，也会制造新 bug。快速补丁只会遮住底层问题。

**核心原则：** 在尝试任何修复之前，**永远**先找到根因（root cause）。只修症状，就是失败。

**只遵守字面、不遵守精神，也同样算违背调试流程。**

## 铁律 (The Iron Law)

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

如果你还没有完成 Phase 1，就没有资格提出修复方案。

## 何时使用 (When to Use)

用于**任何**技术问题：

- 测试失败
- 生产 bug
- 异常行为
- 性能问题
- 构建失败
- 集成问题

**尤其在以下情况下必须使用：**

- 时间压力大时
- 你很想“先来一个 quick fix”
- 你已经试过多个修复
- 上一个修复无效
- 你并没有完全理解问题

**以下情况也不能跳过：**

- 问题看起来很简单
- 你很赶时间
- 管理者要你“立刻修好”

## 四个阶段 (The Four Phases)

你**必须**按顺序完成每一阶段，才能进入下一阶段。

### 阶段 1：根因调查 (Phase 1: Root Cause Investigation)

在尝试**任何**修复前：

1. **认真读错误信息**
   - 不要跳过错误或 warning
   - 错误信息常常已经给出解法
   - 把 stack trace 全部读完
   - 记下行号、文件路径、错误码

2. **稳定复现**
   - 能否可靠触发？
   - 具体步骤是什么？
   - 每次都会发生吗？
   - 如果不能稳定复现，就继续收集数据，不要猜

3. **检查最近变更**
   - 最近什么变更可能导致它？
   - 看 git diff、最近 commits
   - 新依赖、配置变化
   - 环境差异

4. **在多组件系统中收集证据**

   当系统跨多个组件（例如 CI → build → signing，或 API → service → database）时：

   **在提出修复前先加诊断性 instrumentation：**

   ```
   For EACH component boundary:
     - Log what data enters component
     - Log what data exits component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   THEN analyze evidence to identify failing component
   THEN investigate that specific component
   ```

   它的目的，是定位究竟坏在第几层，而不是一上来猜修法。

5. **追踪数据流**

   当错误已经很深地埋在调用栈里时：

   本目录里的 `root-cause-tracing.md` 提供了完整的反向追踪法（backward tracing technique）。

   **简版：**

   - 坏值最早来自哪里？
   - 是谁把坏值传到这里的？
   - 一直往上追，直到找到源头
   - 在源头修，不要在症状处修

### 阶段 2：模式分析 (Phase 2: Pattern Analysis)

先找到模式，再动手修。

1. **找正常工作的例子**
   - 在同一个代码库里找相似且正常工作的代码
   - 对比“坏掉的”和“正常的”

2. **对照参考实现**
   - 如果你在套某个模式，完整读完参考实现
   - 不要扫读
   - 理解完整模式后再应用

3. **识别差异**
   - 正常与异常之间到底哪里不同？
   - 列出所有差异，哪怕很小
   - 不要先入为主地说“这个差异不可能有影响”

4. **理解依赖**
   - 它依赖哪些其他组件？
   - 需要哪些设置、配置、环境？
   - 它默认了哪些前提？

### 阶段 3：假设与测试 (Phase 3: Hypothesis and Testing)

按科学方法来：

1. **提出单一假设**
   - 清楚写出来：“我认为 X 是根因，因为 Y”
   - 要具体，不要模糊

2. **做最小测试**
   - 只做足以验证这个假设的**最小变更**
   - 一次只动一个变量
   - 不要一次修多个问题

3. **验证后再继续**
   - 有效？进入 Phase 4
   - 无效？形成**新的**假设
   - 不要在旧修复上继续叠更多补丁

4. **当你不知道时**
   - 直接说 “I don't understand X”
   - 不要装懂
   - 请求帮助
   - 或继续研究

### 阶段 4：实施修复 (Phase 4: Implementation)

修根因，不修症状。

1. **先创建失败测试**
   - 做出最简单复现
   - 能自动化最好
   - 没框架时也至少写 one-off test script
   - 修之前必须先有
   - 写失败测试时应使用 `loom:test-driven-development`

2. **实现单一修复**
   - 只针对已识别的根因
   - 一次一个改动
   - 不要顺手“顺便优化”
   - 不要捆绑重构

3. **验证修复**
   - 目标测试现在通过了吗？
   - 其他测试有没有被打坏？
   - 问题是否真的解决？

4. **如果修复无效**
   - 停下
   - 统计：你已经试了几次修复？
   - 如果 `< 3`：回到 Phase 1，带着新信息重新分析
   - **如果 `≥ 3`：停止，并开始质疑架构**
   - 不要在没有架构讨论的前提下继续第 4 次尝试

5. **如果连续 3 次以上修复失败：质疑架构**

   这通常说明问题不再是局部假设，而是架构层面不对：

   - 每次修复都会在别的地方暴露新的共享状态/耦合问题
   - 想修好它必须进行“massive refactoring”
   - 每次修好一个点，别处就出现新症状

   这时要问：

   - 这个模式本身是否成立？
   - 我们是不是只因为惯性在坚持它？
   - 是该继续补症状，还是该重构架构？

   在继续尝试前，先和你的人工协作者讨论。

## 红旗信号：立刻停止并回到流程 (Red Flags)

一旦你脑中出现以下念头，就该立刻停下并回到 Phase 1：

- “Quick fix for now, investigate later”
- “Just try changing X and see if it works”
- “Add multiple changes, run tests”
- “Skip the test, I'll manually verify”
- “It's probably X, let me fix that”
- “I don't fully understand but this might work”
- “Pattern says X but I'll adapt it differently”
- “Here are the main problems: ...” 但其实还没调查
- 还没追数据流就开始提方案
- **“One more fix attempt”**（已经试过 2 次以上时）
- **每次修复都在不同地方引出新问题**

**如果已经失败 3 次以上：** 不要继续补，转而质疑架构。

## 你的人工协作者给出的纠偏信号 (Signals You're Doing It Wrong)

以下提示通常意味着你偏离了系统化调试：

- “Is that not happening?” → 你在未验证的情况下做了假设
- “Will it show us...?” → 你应该先加证据收集
- “Stop guessing” → 你在没理解前就提修复
- “Ultrathink this” → 该质疑根本模式，而不是只盯症状
- “We're stuck?” → 当前方法已经失效

看到这些信号，就回到 Phase 1。

## 常见自我合理化 (Common Rationalizations)

| 借口（Excuse） | 现实（Reality） |
|--------|---------|
| “问题很简单，不需要流程” | 简单问题也有根因；流程对简单 bug 一样快。 |
| “很紧急，没时间走流程” | 系统化调试比瞎试更快。 |
| “先试一下，再调查” | 第一次修法就决定了后续模式。 |
| “等确认修好再写测试” | 不先写测试，修复就不可靠。 |
| “一次修多个更省时间” | 你会失去隔离变量的能力。 |
| “参考实现太长，我自己改着用” | 理解不完整几乎必出 bug。 |
| “我已经看出来问题了” | 看到症状 ≠ 理解根因。 |
| “再试一次修复” | 3+ 次失败说明是架构问题。 |

## 快速参考 (Quick Reference)

| 阶段（Phase） | 关键动作（Key Activities） | 成功标准（Success Criteria） |
|-------|---------------|------------------|
| **1. Root Cause** | 读错、复现、查变更、收证据 | 真的知道 WHAT 和 WHY |
| **2. Pattern** | 找正常例子、做对比 | 找到差异 |
| **3. Hypothesis** | 提假设、做最小测试 | 假设被证实，或得到新假设 |
| **4. Implementation** | 先写测试、修复、验证 | bug 解决，测试通过 |

## 当流程得出“没有根因”时 (When Process Reveals "No Root Cause")

如果系统化调查后确认问题真的是环境性、时序依赖或外部因素：

1. 你已经完成了流程
2. 记录你调查过什么
3. 实施适当处理，例如 retry、timeout、error message
4. 加上 monitoring / logging，为未来调查留证据

**但是：** 95% 的“没有根因”其实只是调查还不完整。

## 支撑技术 (Supporting Techniques)

这些文档都位于当前目录，是系统化调试的配套技术：

- **`root-cause-tracing.md`** - 沿调用栈反向追踪 bug，找到原始触发点
- **`defense-in-depth.md`** - 找到根因后，在多层加验证
- **`condition-based-waiting.md`** - 用条件轮询替代任意 timeout

**相关技能：**

- **`loom:test-driven-development`** - 用于创建失败测试（Phase 4, Step 1）
- **`loom:verification-before-completion`** - 在声称修好前验证结果

## 真实效果 (Real-World Impact)

来自多次调试会话的统计：

- 系统化方式：15 到 30 分钟解决
- 随机修补方式：2 到 3 小时乱撞
- 一次修对率：95% vs 40%
- 新 bug 引入率：几乎为零 vs 经常发生
