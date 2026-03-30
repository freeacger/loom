# 设计评审 Prompt 方法论 (System Design Review Prompt Methodology)

## 背景 (Context)

用户想学习如何设计用于评审系统设计方案（System Design Document）的 prompt，了解通用方法论和最佳实践。本文档综合了项目现有评审体系（AGENTS.md、design-decision-checklist.md）和业界最新实践进行系统化整理。

---

## 一、评审 Prompt 的核心构成要素 (Core Building Blocks)

一个高质量的设计评审 prompt 由以下 8 个模块构成，缺一不可：

```
[1] 上下文注入（Context Injection）
[2] 角色设定（Persona）
[3] 审查维度（Dimensions）
[4] 优先级定义（Priority Rubric）
[5] 输出格式（Output Format）
[6] Few-Shot 示例（Examples）
[7] 自检指令（Self-Check）
[8] 置信度要求（Confidence Declaration）
```

---

## 二、模块详解 (Module Details)

### 模块 1：上下文注入（Context Injection）

**为什么关键**：LLM 没有你的项目背景。没有上下文的审查 = 泛化建议，而非针对性发现。

**注入层次（按优先级）**：

| 层次 | 内容 | 注入时机 |
|------|------|----------|
| 项目规范层 | 架构分层约束、编码风格、禁止事项 | 始终注入 |
| 技术栈层 | 语言版本、ORM 用法、框架约定 | 始终注入 |
| 业务逻辑层 | 领域模型、关键业务规则 | 按需注入 |
| 变更上下文层 | 本次设计的目的、解决的问题 | 始终注入 |
| 历史决策层 | 相关历史决策、已知技术债 | 有时注入 |

**Anthropic 推荐结构（长文本用 XML 标签包裹，放在 prompt 顶部）**：

```xml
<documents>
  <document index="1">
    <source>architecture_constraints.md</source>
    <document_content>
    分层约束：Handler → Service → DAO/Manager → Model
    禁止 Service 直接调用其他 Service
    所有 DB 调用必须使用 .WithContext(ctx)
    </document_content>
  </document>
  <document index="2">
    <source>design_document.md</source>
    <document_content>{{待审查的设计文档全文}}</document_content>
  </document>
</documents>

{{审查指令放在这里}}
```

**关键技巧**：长文本放顶部，查询/指令放底部，可提升约 30% 的检索准确率。

---

### 模块 2：角色设定（Persona）

**有效实践**：具体角色 > 泛化角色。

```
❌ 弱："你是一个有经验的开发者"
✓ 强："你是一个精通 Go 微服务、MySQL 分库分表和分布式事务的后端架构师，
      熟悉 Go 的 context 传递规范和 GORM 使用约束"
```

**角色与任务匹配**：

| 审查类型 | 推荐角色 |
|----------|----------|
| 整体架构审查 | 后端架构师（精通目标技术栈） |
| 安全专项 | 安全架构师 |
| 性能专项 | 性能工程师 |
| 数据一致性专项 | 分布式系统专家 |
| 产品/策略层 | CEO/技术 VP（战略视角） |

**Panel-of-Experts 技术（复杂设计专用）**：
让多个专家角色分别独立评审后互相批评，实测可将误报率从 40% 降至 20%，代价是 token 成本翻倍。适合高价值、高风险的关键设计。

---

### 模块 3：审查维度（Dimensions）

**设计原则**：

1. **限定数量**：3-7 个维度。超过 7 个会导致 LLM 注意力分散，关键问题被低价值评论淹没
2. **每个维度要有判定标准**（Rubric），而非模糊描述
3. **使用问题特定的 Rubric**，而非通用 Rubric（研究证实更有效）

**示例对比**：

```
❌ 弱维度："检查性能"

✓ 强维度（含 Rubric）："检查查询性能
   判定标准：
   - 是否存在 N+1 查询（循环内执行 SELECT）
   - WHERE 子句使用的列是否有索引支撑
   - 是否在事务内执行慢查询或批量操作
   - 是否有无 LIMIT 的全表扫描可能"
```

**项目现有维度（AGENTS.md）可直接复用**：
1. 正确性和项目规范（对照 CONTRIBUTING.md）
2. 性能瓶颈
3. KISS 和 DRY
4. 可观测性（结构化日志、指标、告警）
5. 幂等性和数据一致性

**设计文档专用维度（来自 design-decision-checklist.md）**：
- 迁移和切换策略（Migration & Cutover）
- 数据处理（Data Handling）
- Schema 和存储
- 向后兼容性（Backward Compatibility）
- 条件模块（并发锁、异步任务、状态机等按需触发）

---

### 模块 4：优先级定义（Priority Rubric）

**核心要求**：每个级别必须有影响描述和行动指引，而非仅仅是"高/中/低"标签。

项目现有 P0-P3 定义（AGENTS.md）已经符合最佳实践标准，可直接嵌入 prompt：

```
P0（阻塞）：导致数据丢失、安全漏洞、发布失败或行为不正确
P1（高）：高概率 bug、强回归风险、重大需求缺口 → 合并前必须修复
P2（中）：有意义的正确性/可维护性风险 → 合并前应修复，除非有理由延期
P3（低）：清晰度、一致性改进 → 可稍后处理
```

**补充：置信度与优先级联用**（减少误报的关键）：

```
CR01 [P1] [置信度: 高] 标题
CR02 [P2] [置信度: 中] 标题  ← 提示读者需要进一步验证
```

---

### 模块 5：输出格式（Output Format）

**结构化要求**的价值：可解析、可追踪、可审计。

**每个发现必须包含四要素链**（项目现有规范，与业界最佳实践一致）：

```
1. What：问题是什么
2. How：当前设计如何触发这个问题（引用具体章节或代码）
3. Example：一个具体的触发场景/案例
4. Why：为什么这对当前变更有影响
```

**发现格式模板**：

```markdown
### CR01 [P1] — 标题（Title）

**问题（What）**：...

**触发路径（How）**：（引用设计文档第 X 节）...

**具体场景（Example）**：...

**影响（Why）**：...

**建议选项（Options）**：

| 选项 | 方案 | 优点 | 权衡 |
|------|------|------|------|
| A（推荐）| ... | ... | ... |
| B | ... | ... | ... |
```

**推荐加入的结构化章节**：
- 执行摘要（触发的条件模块列表 + 发现数量分布）
- 发现列表（按优先级排序）
- 建议补充内容（可直接粘贴进设计文档的文本块）
- 开放问题（需设计作者回答的问题）

---

### 模块 6：Few-Shot 示例（Examples）

**量化效果**：3-5 个高质量示例可将输出质量提升 4%-33%（GPT-3.5 CodeBLEU 指标）。

**示例质量要求**：
- 必须贴近实际用例（不要用玩具例子）
- 覆盖边界情况（如"看起来有问题但实际合理的模式"）
- 用 `<example>` 标签包裹，与指令明确区分

**示例模板**：

```xml
<example>
<finding id="CR01" priority="P1" confidence="high">
<what>迁移切换期间缺少回滚计划</what>
<how>设计文档第 3 节描述了"一次性迁移所有历史数据"，
     但未说明迁移失败时如何恢复旧状态</how>
<example_case>迁移执行到 50% 时数据库连接超时，
             新表部分写入，旧系统已停止写入，无法回滚</example_case>
<why>违反 design-decision-checklist.md 的 Migration & Cutover 要求，
     生产环境数据不一致风险</why>
</finding>
</example>

<example>
<finding id="CR02" priority="P3" confidence="high">
<what>日志事件名称使用驼峰命名，不符合项目规范</what>
<how>设计文档第 5 节定义了 "userSignedIn" 事件，
     但项目约定使用 snake_case（参考 code_style.md）</how>
<example_case>日志分析 SQL 中 WHERE event_name = 'user_signed_in' 无法匹配</example_case>
<why>不影响功能，但影响日志可查询性和跨系统一致性</why>
</finding>
</example>
```

---

### 模块 7：自检指令（Self-Check）

在 prompt 末尾加自检步骤，可可靠地捕获 LLM 的遗漏和错误：

```
在输出最终报告之前，请验证：
□ 每个发现是否都引用了设计文档的具体段落？
□ 每个发现是否都给出了至少一个修复建议？
□ 是否所有 P0/P1 发现都提供了选项表格（Options Table）？
□ 优先级排序是否从高到低？
□ 不确定的发现是否标注了置信度为"中/低"？
```

---

### 模块 8：置信度要求（Confidence Declaration）

**为什么重要**：LLM 倾向于给出过于确定的判断，引入置信度可显著降低误报。

```
对每个发现，必须评估置信度：
- 高（High）：有直接证据，可在设计文档中找到具体触发点
- 中（Medium）：有间接证据，但需要设计作者确认
- 低（Low）：潜在风险，建议作者自查
```

---

## 三、Chain-of-Thought vs 直接评估 (CoT vs Direct Evaluation)

**设计审查场景的推荐做法**：

```
使用 CoT 分析每个维度，但用结构化格式输出最终结果。
```

**实践方式（Anthropic 官方推荐）**：

```xml
<thinking>
（在这里分析每个维度，推理是否有问题，写下中间步骤）
</thinking>

<report>
（在这里输出结构化的审查报告，不要包含推理过程）
</report>
```

**注意**：
- CoT 仅在复杂推理场景有效（如并发安全、分布式一致性分析）
- 对于简单模式匹配（如命名规范检查），直接评估更高效
- 用"think thoroughly before answering"通常比手写分步骤指令更好

---

## 四、完整 Prompt 黄金模板 (Complete Golden Template)

```
<documents>
  <document index="1">
    <source>project_constraints</source>
    <document_content>
    [架构约束、编码规范、禁止事项]
    </document_content>
  </document>
  <document index="2">
    <source>design_document</source>
    <document_content>
    [待审查的设计文档全文]
    </document_content>
  </document>
</documents>

---

你是一个精通 [技术栈] 的后端架构师，深度熟悉以上项目约束。

你的任务是对上述设计文档进行结构化审查，重点检查以下维度：

**维度 1：[维度名称]**
判定标准：
- [具体可操作的检查点 1]
- [具体可操作的检查点 2]

**维度 2：[维度名称]**
...

**优先级定义**：
- P0：[影响描述] → 阻塞，必须修复
- P1：[影响描述] → 合并前修复
- P2：[影响描述] → 应修复
- P3：[影响描述] → 可延期

**输出格式**：
每个发现必须包含：
1. ID 和优先级（如 CR01 [P1]）
2. 问题描述（What）
3. 触发路径（How，引用设计文档具体段落）
4. 具体场景（Example）
5. 影响说明（Why）
6. 修复选项表格（P0/P1 必须）
7. 置信度（High / Medium / Low）

最终报告结构：
1. 执行摘要（触发的条件模块 + 发现数量分布）
2. 发现列表（按 P0→P3 排序）
3. 建议补充内容（可复制进设计文档的段落）
4. 开放问题（需设计作者回答）

<examples>
[1-3 个高质量示例，覆盖典型发现和边界情况]
</examples>

<thinking>
请在此标签内逐一分析每个维度，写下你的推理过程。
</thinking>

完成分析后，在 <report> 标签内输出结构化审查报告。

在输出前自检：
□ 每个发现是否引用了设计文档的具体段落？
□ P0/P1 是否都有选项表格？
□ 不确定的发现是否标注了置信度为"中/低"？
```

---

## 五、常见反模式 (Anti-Patterns to Avoid)

| 反模式 | 后果 | 替代方案 |
|--------|------|----------|
| 万能审查者（无维度限定） | 泛化建议淹没关键问题 | 限定 3-7 个维度，每个有 Rubric |
| 无锚点评估（无项目规范） | 不相关或错误的建议 | 注入架构约束、编码规范 |
| 结论先行（无四要素链） | 无法判断严重性和可信度 | 强制要求 What→How→Example→Why |
| 过度依赖 Persona | 数据不足时引入噪声 | 仅在有足够上下文时使用角色设定 |
| 忽视置信度 | 误报率高，浪费作者时间 | 每个发现附置信度 |
| 静态 Prompt（不迭代） | 质量停滞 | 版本控制 prompt，建立验证集定期测试 |
| 上下文过载 | 关键信息被稀释 | 按需注入，优先级分层 |

---

## 六、与现有体系的对应关系 (Mapping to Existing System)

项目现有体系已经实现了最佳实践中的大多数要求：

| 最佳实践 | 现有实现 | 状态 |
|----------|----------|------|
| 分层维度 + Rubric | AGENTS.md 5 维度 + checklist | ✅ |
| P0-P3 优先级定义 | AGENTS.md Review Output | ✅ |
| 四要素解释链 | AGENTS.md Review Output | ✅ |
| 结构化输出格式（CR01 [P1]） | AGENTS.md | ✅ |
| 条件模块触发 | design-decision-checklist.md | ✅ |
| 选项表格（Options Table） | 近期 audit 报告中 | ✅ |
| 置信度声明 | 未明确要求 | ⚠️ 可补充 |
| Few-Shot 示例嵌入 prompt | skill 文件中未见示例 | ⚠️ 可补充 |
| CoT 显式分离 `<thinking>` | 未明确使用 | ⚠️ 可补充 |
| 上下文注入结构（XML 标签） | 未标准化 | ⚠️ 可改进 |
