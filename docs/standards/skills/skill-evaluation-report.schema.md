# 技能评测报告 Schema (Skill Evaluation Report Schema)

## 目标 (Goal)

定义技能评测 Markdown 报告的固定结构，确保不同技能、不同版本、不同执行器产生的报告具备一致的可读性、可比性和准入表达方式。

本 Schema 面向“报告结构（report structure）”，不是 Markdown 语法校验器。实现侧应确保每份报告至少覆盖本文件定义的必需章节和字段。

## 顶层结构 (Top-Level Structure)

每份报告必须包含以下一级章节，顺序固定：

1. `# 技能评测报告 (Skill Evaluation Report)`
2. `## 元数据 (Metadata)`
3. `## 总览 (Overview)`
4. `## 结论摘要 (Executive Summary)`
5. `## 设计层评分 (Design Evaluation)`
6. `## 运行时评分 (Runtime Evaluation)`
7. `## 代表性样本 (Representative Cases)`
8. `## 风险与阻塞项 (Risks and Blocking Issues)`
9. `## 准入建议 (Admission Recommendation)`
10. `## 附录 (Appendix)`

## 标题规范 (Heading Rules)

- 所有章节标题必须使用双语格式：`中文标题 (English Title)`
- 正文默认使用中文
- 技术术语首次出现时应带英文，如 `运行时评估（runtime evaluation）`
- 星级必须使用固定 5 星制：`★★★★★`、`★★★★☆`、`★★★☆☆`、`★★☆☆☆`、`★☆☆☆☆`

## 必需字段 (Required Fields)

### 元数据 (Metadata)

必须包含以下项目：

- 技能：`<skill-name>`
- 仓库路径：`<repo-path>`
- 提交：`<commit-sha>`
- 评测时间：`<datetime>`
- 样本数：`<total-cases>`

### 总览 (Overview)

必须包含以下项目：

- 设计：`<stars>`
- 运行时：`<stars>`
- 总评：`<stars>`
- 定位：`<diagnosis-label>`
- 准入结论：`<admission-label>`

允许的定位值：

- `双高`
- `设计强，运行弱`
- `设计弱，运行强`
- `双弱`
- `边界风险型`
- `效率拖累型`

允许的准入结论值：

- `标杆技能`
- `推荐准入`
- `谨慎准入`
- `暂不准入`
- `拒绝`

### 结论摘要 (Executive Summary)

必须使用 3 条平级要点：

1. 当前等级和总评星级
2. 最主要短板
3. 是否建议准入

### 设计层评分 (Design Evaluation)

必须包含一个表格，列为：

| 维度 | 分数 | 星级 | 说明 |
|---|---:|---|---|

行至少包含：

- 边界清晰度
- 流程完整性
- 输出契约清晰度
- 风险与升级条件
- 可维护性

随后必须有：

### 设计层主要发现 (Design Findings)

- 至少 1 条
- 最多 5 条

### 运行时评分 (Runtime Evaluation)

必须包含一个表格，列为：

| 维度 | 分数 | 星级 | 说明 |
|---|---:|---|---|

行至少包含：

- 路由正确性
- 结果质量
- 边界遵守
- 生产效率
- 稳定性

随后必须有：

### 运行时主要发现 (Runtime Findings)

- 至少 1 条
- 最多 5 条

### 代表性样本 (Representative Cases)

必须包含一个表格，列为：

| Case | 类型 | 结果 | 关键信号 |
|---|---|---|---|

至少 3 行，优先覆盖：

- 一个通过样本
- 一个失败样本
- 一个最能解释总评的关键样本

### 风险与阻塞项 (Risks and Blocking Issues)

- 可以为空
- 若为空，必须明确写 `- 无阻塞项`
- 若存在高风险失败，必须排在第一条

### 准入建议 (Admission Recommendation)

必须包含以下 3 项：

- 最终等级：`<stars> <label>`
- 建议：`<admission-decision>`
- 原因：`<reason>`

其中 `<label>` 允许值：

- `卓越`
- `优秀`
- `及格`
- `不及格`
- `很差`

### 附录 (Appendix)

至少包含以下 3 项：

- Baseline 对照摘要
- Case 统计
- 运行参数

## 示例模板 (Template Example)

```md
# 技能评测报告 (Skill Evaluation Report)

## 元数据 (Metadata)
- 技能：`design-structure`
- 仓库路径：`/repo/skills/design-structure`
- 提交：`abc1234`
- 评测时间：`2026-03-31T12:00:00Z`
- 样本数：`42`

## 总览 (Overview)
- 设计：`★★★★☆`
- 运行时：`★★★☆☆`
- 总评：`★★★☆☆`
- 定位：`设计强，运行弱`
- 准入结论：`谨慎准入`

## 结论摘要 (Executive Summary)
- 当前等级为 `★★★☆☆ 及格`，整体可用但未达到推荐准入线。
- 最主要短板是运行时误触发率偏高。
- 建议谨慎准入，不作为默认推荐技能。

## 设计层评分 (Design Evaluation)
| 维度 | 分数 | 星级 | 说明 |
|---|---:|---|---|
| 边界清晰度 | 88 | `★★★★☆` | `when to use / when not to use` 清楚 |
| 流程完整性 | 84 | `★★★★☆` | 两阶段流程闭环明确 |
| 输出契约清晰度 | 82 | `★★★★☆` | 文件与对话输出边界已定义 |
| 风险与升级条件 | 70 | `★★★☆☆` | 升级人工条件仍偏弱 |
| 可维护性 | 78 | `★★★☆☆` | 已可评测，但版本演化说明不足 |

### 设计层主要发现 (Design Findings)
- 技能边界清晰，误用成本低。
- 输出契约完整，适合进入运行时评测。

## 运行时评分 (Runtime Evaluation)
| 维度 | 分数 | 星级 | 说明 |
|---|---:|---|---|
| 路由正确性 | 65 | `★★★☆☆` | 存在少量误触发 |
| 结果质量 | 72 | `★★★☆☆` | 相比 baseline 有提升，但不稳定 |
| 边界遵守 | 80 | `★★★★☆` | 未观察到越权操作 |
| 生产效率 | 68 | `★★★☆☆` | 平均轮数略高 |
| 稳定性 | 70 | `★★★☆☆` | 多次运行结果方差可接受 |

### 运行时主要发现 (Runtime Findings)
- 运行时表现达到及格线，但未达到优秀。
- 主要短板是误触发率和平均轮数。

## 代表性样本 (Representative Cases)
| Case | 类型 | 结果 | 关键信号 |
|---|---|---|---|
| `routing-positive-01` | `replay` | `pass` | 该触发时稳定触发 |
| `routing-negative-07` | `negative` | `fail` | 不该触发时误触发 |
| `runtime-replay-11` | `replay` | `warn` | 输出正确但轮数偏高 |

## 风险与阻塞项 (Risks and Blocking Issues)
- 高风险问题未发现
- 运行时误触发仍需持续观察

## 准入建议 (Admission Recommendation)
- 最终等级：`★★★☆☆ 及格`
- 建议：`谨慎准入`
- 原因：`设计成熟，但运行时收益不够稳定`

## 附录 (Appendix)
- Baseline 对照摘要：`开启技能后成功率提升 8%，误触发率增加 4%`
- Case 统计：`replay 24 / negative 12 / safety 6`
- 运行参数：`model=sonnet, retries=0, profile=project`
```

## 校验规则摘要 (Validation Summary)

实现侧至少应检查：

- 顶层一级、二级标题是否齐全
- 双语标题是否存在
- 总览是否包含 3 个星级字段
- 设计层和运行时层表格维度是否完整
- 是否存在准入建议章节
- 附录是否包含 baseline、统计、运行参数
