---
name: verification-before-completion
description: "当你准备声称工作已经完成、问题已修复或结果已通过验证时，在提交（commit）或创建 PR 之前使用。本技能要求先运行验证命令并核对输出，再做任何成功性表述。证据（evidence）必须先于结论（claims）。"
---

# 完成前验证 (Verification Before Completion)

## 概览 (Overview)

没有经过验证就声称工作完成，不是高效，而是不诚实。

**核心原则：** 先有证据，再有结论（Evidence before claims, always）。

**只遵守字面、不遵守精神，也仍然算违规。**

## 铁律 (The Iron Law)

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

如果你没有在当前这条消息对应的工作中运行验证命令，就不能声称它已经通过。

## 闸门函数 (The Gate Function)

```
在声称任何状态或表达满意之前：

1. IDENTIFY：什么命令能证明这个结论？
2. RUN：完整、重新运行该命令
3. READ：阅读完整输出，检查退出码，统计失败数
4. VERIFY：输出是否真的支持这个结论？
   - 如果不支持：基于证据说明真实状态
   - 如果支持：带着证据再做结论
5. ONLY THEN：只有到这一步，才能声称成功
```

跳过任意一步，都不是“省事”，而是“没验证”。

## 常见错误模式 (Common Failures)

| 声称（Claim） | 必需证据（Requires） | 不足以证明（Not Sufficient） |
|-------|----------|----------------|
| Tests pass | 测试命令输出，且为 0 failures | 上一次结果、或“应该能过” |
| Linter clean | linter 输出 0 errors | 只跑了局部检查、或主观推断 |
| Build succeeds | build 命令退出码为 0 | linter 通过、日志看起来没问题 |
| Bug fixed | 原始症状对应的验证现在通过 | 代码改了，就假定修好了 |
| Regression test works | 经过完整红绿循环（red-green cycle）验证 | 只看到测试通过一次 |
| Agent completed | 通过 VCS diff 看见真实修改 | 只听 agent 说“成功了” |
| Requirements met | 逐条检查需求清单 | 测试通过就断言阶段完成 |

## 红旗信号，立刻停下 (Red Flags - STOP)

- 你开始用 “should”、“probably”、“seems to”
- 你在验证前表达满意，比如 “Great!”、“Perfect!”、“Done!”
- 你准备在没有验证的情况下 commit / push / 开 PR
- 你相信 agent 的成功汇报，而没有独立核验
- 你依赖部分验证（partial verification）
- 你开始想“就这一次”
- 你因为累了只想赶紧结束
- **任何暗示成功但实际上没跑验证的说法**

## 防止自我合理化 (Rationalization Prevention)

| 借口（Excuse） | 现实（Reality） |
|--------|---------|
| “Should work now” | 去跑验证命令 |
| “I'm confident” | 自信不等于证据 |
| “Just this once” | 没有例外 |
| “Linter passed” | linter ≠ compiler |
| “Agent said success” | 必须独立验证 |
| “I'm tired” | 疲惫不是理由 |
| “Partial check is enough” | 局部验证什么也证明不了 |
| “Different words so rule doesn't apply” | 规则看精神，不看措辞钻空子 |

## 关键模式 (Key Patterns)

**测试（Tests）：**
```
✅ [运行测试命令] [看到：34/34 pass] “All tests pass”
❌ “Should pass now” / “Looks correct”
```

**回归测试（Regression tests，TDD 红绿循环）：**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ “I've written a regression test” （但没有验证红绿循环）
```

**构建（Build）：**
```
✅ [运行 build] [看到：exit 0] “Build passes”
❌ “Linter passed” （linter 不检查编译）
```

**需求完成度（Requirements）：**
```
✅ 重读计划 → 建清单 → 逐条核验 → 报告缺口或完成情况
❌ “Tests pass, phase complete”
```

**Agent 委派（Agent delegation）：**
```
✅ Agent 报告成功 → 检查 VCS diff → 验证修改 → 报告真实状态
❌ 直接相信 agent 的成功汇报
```

## 这件事为什么重要 (Why This Matters)

来自 24 条失败记忆的结论：

- 你的协作方会说“我不相信你”，信任会被打断
- 未定义函数被带出去，会直接崩溃
- 需求遗漏会被带出去，功能不完整
- 虚假的“完成”会浪费时间，之后还要返工和重新定向
- 这违背了一个基本原则：“诚实（Honesty）是核心价值。如果你撒谎，你会被替换。”

## 何时应用 (When To Apply)

**以下场景一律适用：**

- 在任何成功/完成类表述之前
- 在任何表达满意的话语之前
- 在任何关于工作状态为正向的判断之前
- 在 commit、开 PR、结束任务之前
- 在进入下一个任务之前
- 在委派给 agent 之前

**适用范围包括：**

- 原句
- 同义改写
- 暗示成功的表达
- 任何可能让人理解为“已经完成/已经正确”的说法

## 底线 (The Bottom Line)

**验证不能走捷径。**

先运行命令。读取输出。然后再声称结果。

这是不可协商的要求。
