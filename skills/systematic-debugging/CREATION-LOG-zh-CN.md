# 创建日志：系统化调试技能 (Creation Log: Systematic Debugging Skill)

一个关于如何抽取、结构化并加固（bulletproofing）关键技能的参考示例。

## 源材料 (Source Material)

从 `/Users/jesse/.claude/CLAUDE.md` 中抽取出的调试框架：

- 四阶段系统化流程（Investigation → Pattern Analysis → Hypothesis → Implementation）
- 核心要求：**永远找根因，绝不修症状**
- 为抵抗时间压力与自我合理化而设计的规则

## 抽取决策 (Extraction Decisions)

**保留：**

- 完整的四阶段框架
- 明确的反捷径规则
- 抵抗压力的话术
- 每阶段的具体步骤

**移除：**

- 项目特定上下文
- 同一规则的重复表述
- 叙事性解释（压缩成原则）

## 结构设计 (Structure Following skill-creation/SKILL.md)

1. 丰富的 `when_to_use`
2. `technique` 类型，强调可执行过程
3. 关键词覆盖：`root cause`、`symptom`、`workaround`、`debugging`、`investigation`
4. 增加 “fix failed” 决策流图
5. 按 phase 拆分成可扫读 checklist
6. 加入 anti-patterns 小节

## 加固方式 (Bulletproofing Elements)

### 语言选择 (Language Choices)

- 使用 “ALWAYS” / “NEVER”，而不是 “should”
- 使用 “STOP and re-analyze” 这类显式暂停语句
- 使用 “Don't skip past” 来精准拦截真实错误行为

### 结构性防线 (Structural Defenses)

- 强制要求 Phase 1
- 单一假设规则（single hypothesis rule）
- 明确规定首次修复失败后的动作
- 用 anti-patterns 小节列出捷径长什么样

### 冗余强化 (Redundancy)

- 根因要求在多个 section 中重复出现
- “NEVER fix symptom” 在不同上下文里反复强调
- 每个阶段都带“不要跳过”的提醒

## 测试方法 (Testing Approach)

按 `skills/meta/testing-skills-with-subagents` 设计了 4 个验证测试：

### 测试 1：学术场景 (Academic Context)
- 没有时间压力
- **结果：** 完整遵守流程

### 测试 2：时间压力 + 明显快修
- 用户很赶，症状修法看起来很诱人
- **结果：** 成功抵抗捷径，找到了真实根因

### 测试 3：复杂系统 + 高不确定性
- 多层故障，根因不明显
- **结果：** 穿透各层追踪，最终定位源头

### 测试 4：第一次修复失败
- 假设不成立，很容易想继续叠补丁
- **结果：** 停止、重分析、形成新假设

**全部测试通过。** 未发现合理化倾向。

## 迭代记录 (Iterations)

### 初始版本 (Initial Version)

- 完整四阶段框架
- anti-patterns 小节
- “fix failed” 决策流图

### 增强 1：加入 TDD 关联 (Enhancement 1: TDD Reference)

- 增加对 `skills/testing/test-driven-development` 的引用
- 加入一段说明：TDD 的“最小实现”与 debugging 的“找根因”不是同一件事
- 用于防止方法论混淆

## 最终结果 (Final Outcome)

一个经过加固的技能，具备以下特征：

- ✅ 明确要求做根因调查
- ✅ 能抵抗时间压力下的自我合理化
- ✅ 为每一阶段提供具体步骤
- ✅ 显式列出反模式
- ✅ 在多种压力场景下测试通过
- ✅ 澄清了与 TDD 的关系
- ✅ 可以投入使用

## 关键洞察 (Key Insight)

**最重要的加固点：** anti-patterns 小节把“当下看起来很合理的捷径”写得非常具体。当 Claude 心里冒出“我先加一个 quick fix 吧”时，看到这一模式已被明确列为错误，会形成认知阻力。

## 使用示例 (Usage Example)

遇到 bug 时：

1. 加载技能：`skills/debugging/systematic-debugging`
2. 读 overview（10 秒）- 重新提醒根因要求
3. 按 Phase 1 checklist 调查
4. 一旦想跳步骤，看到 anti-pattern，立刻停下
5. 全流程完成，找到根因

**时间投入：** 5 到 10 分钟  
**节省时间：** 避免数小时的症状打地鼠

---

*Created: 2025-10-03*  
*Purpose: 作为技能抽取与 bulletproofing 的参考示例*
