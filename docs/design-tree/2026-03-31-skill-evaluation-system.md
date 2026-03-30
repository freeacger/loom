# 技能评测系统设计文档 (Skill Evaluation System Design Document)

## 问题 (Problem)

需要一套只做评估、不做自动改进的技能评测系统，用尽量接近生产环境（production-like）的方式，判断一个技能是否达到准入标准，并用直观的 5 星评分说明它是一般、普通、优秀还是卓越。

成功标准：

- 能同时回答“设计本身是否合格”和“运行时是否有效”这两个问题
- 能输出统一的 JSON 结果与 Markdown 报告
- 能给出 5 星制总评，其中 3 星及格、4 星优秀、5 星卓越
- 能支持准入结论，而不是只给一堆零散指标

## 范围 (Scope)

### 包含 (Included)

- 设计层评估（design evaluation）
- 运行时评估（runtime evaluation）
- 5 星评分与等级映射
- JSON 结果契约（result schema）
- Markdown 报告契约（report schema）
- baseline 对照与 replay / negative / safety case 分类
- 准入结论生成

### 不包含 (Excluded)

- 自动改写 `SKILL.md`
- 自动生成候选 skill 版本
- 在线生产流量自动灰度
- 实时 dashboard
- 多模型矩阵优化搜索

## 假设 (Assumptions)

- 技能评测对象可以来自当前仓库，也可以来自任意 GitHub 仓库中的 `<skill>.md`
- 已存在部分 canonical eval，例如 `evals/evals.json`
- 运行时主要通过与生产一致或近似一致的 Claude Code 调用方式回放
- 评测系统本身拥有独立的 case registry 与 result store

## 设计树 (Design Tree)

```text
design_tree
├── 1. 评测输入与样本
│   ├── 1.1 Canonical evals ✓
│   ├── 1.2 Production replay cases ✓
│   └── 1.3 Negative / safety cases ✓
├── 2. 评测执行层
│   ├── 2.1 Scenario runner ✓
│   ├── 2.2 Baseline run ✓
│   └── 2.3 Skill-enabled run ✓
├── 3. 证据采集与结果存储
│   ├── 3.1 Trace collector ✓
│   ├── 3.2 Result JSON schema ✓
│   └── 3.3 Markdown report schema ✓
├── 4. 评分引擎
│   ├── 4.1 设计层评分 ✓
│   ├── 4.2 运行时评分 ✓
│   ├── 4.3 总评与短板约束 ✓
│   └── 4.4 5 星映射规则 ✓
├── 5. 准入判定
│   ├── 5.1 总评等级 ✓
│   ├── 5.2 诊断文案 ✓
│   └── 5.3 准入建议 ✓
└── 6. 验证与扩展
    ├── 6.1 与现有 skill-creator eval 对接 [OPEN]
    ├── 6.2 Shadow mode [OPEN]
    └── 6.3 发布流程集成 [OPEN]
```

## 核心对象 (Core Objects)

- `skill_under_test`：被评测技能
- `eval_case`：单个评测样本
- `run`：一次实际执行
- `trace`：执行证据，包含触发、轮数、延迟、输出等
- `scorecard`：设计层、运行时层与总评结果
- `report`：给人看的结论性报告

## 核心流程 (Core Flows)

### 评测主流程 (Main Evaluation Flow)

1. 读取 `skill_under_test`
2. 加载 case 集合
3. 对每个 case 运行 baseline
4. 对每个 case 运行 skill-enabled 场景
5. 收集 trace
6. 计算设计层分数与运行时分数
7. 应用星级映射与短板约束
8. 生成 JSON 结果与 Markdown 报告

### 评分流程 (Scoring Flow)

1. 设计层按 5 个维度打分
2. 运行时按 5 个维度打分
3. 计算加权总分：`0.4 * 设计分 + 0.6 * 运行时分`
4. 应用短板约束：
   - 任一单项低于 60，总评最高 3 星
   - 任一单项低于 40，总评最高 2 星
   - 存在高风险失败时降 1 星或直接拒绝
5. 生成定位文案与准入建议

## 接口与数据 (Interfaces and Data)

### 用户输入 (Public Evaluation Input)

系统对外只要求以下字段：

- `skill`：必填，本地 `SKILL.md` 路径或 GitHub skill 文件 URL
- `baseline`：可选，默认 `main`
- `mode`：可选，默认 `full`，允许值为 `design | runtime | full`

最小调用示例：

```json
{
  "skill": "https://github.com/org/repo/blob/main/skills/foo/SKILL.md"
}
```

### 内部派生输入 (Derived Internal Input)

以下字段由系统自动推导，不要求用户显式提供：

- `source_type`
- `repo`
- `path`
- `ref`
- `resolved_commit`
- `baseline_ref`
- `selected_case_suites`
- `execution_profiles`
- `evaluation_run_id`

### 评测输出 (Evaluation Outputs)

- `mode`
- `design.raw_score`
- `design.stars`
- `runtime.raw_score`
- `runtime.stars`
- `overall.raw_score`
- `overall.stars`
- `overall.diagnosis`
- `recommendation.admission`

### 样本分类 (Case Types)

- `design`
- `runtime`
- `replay`
- `negative`
- `safety`

### 技能身份 (Skill Identity)

系统内部统一使用以下字段标识评测对象：

- `source_type`
- `repo`
- `path`
- `ref`
- `resolved_commit`
- 可选 `display_name`

其中：

- `source_type` 允许值为 `local_repo | github_file`
- `repo + path + resolved_commit` 构成稳定版本身份
- `display_name` 仅用于报告展示，不作为唯一主键

## 评分规则 (Scoring Rules)

### 设计层评分 (Design Evaluation)

- 边界清晰度：30%
- 流程完整性：25%
- 输出契约清晰度：20%
- 风险与升级条件：15%
- 可维护性：10%

### 运行时评分 (Runtime Evaluation)

- 路由正确性：35%
- 结果质量：30%
- 边界遵守：15%
- 生产效率：10%
- 稳定性：10%

### 星级映射 (Star Mapping)

- `90-100` → `★★★★★` 卓越
- `80-89` → `★★★★☆` 优秀
- `60-79` → `★★★☆☆` 及格
- `40-59` → `★★☆☆☆` 不及格
- `<40` → `★☆☆☆☆` 很差

### 诊断文案 (Diagnosis Labels)

- 双高
- 设计强，运行弱
- 设计弱，运行强
- 双弱
- 边界风险型
- 效率拖累型

## 结果契约 (Output Contracts)

### JSON 结果契约 (Result JSON Schema)

结果文件必须包含：

- `mode`
- `skill`
- `summary`
- `overall`
- `recommendation`
- `design` 与 `runtime`
- 可选 `cases`
- 可选 `skipped_layers`

其中：

- `mode=full` 时，`design` 与 `runtime` 都必须提供完整评分
- `mode=design` 时，`runtime` 允许以 `skipped` 形式返回
- `mode=runtime` 时，`design` 允许以 `skipped` 形式返回
- `overall` 必须额外给出 `diagnosis` 与 `final_verdict`
- `recommendation` 必须给出最终星级、等级文案、准入建议和原因

### Markdown 报告契约 (Markdown Report Schema)

报告必须包含：

- 元数据
- 总览
- 结论摘要
- 设计层评分
- 运行时评分
- 代表性样本
- 风险与阻塞项
- 准入建议
- 附录

章节顺序固定，标题使用双语格式。

## 风险 (Risks)

- 仅依赖 synthetic case 会高估 skill 表现
- 若没有 no-skill baseline，无法判断 skill 是否真的带来增益
- 如果 trace 不完整，会导致定位偏差
- 若设计层和运行时层混成一个分数，问题归因会失真
- 若对外输入暴露过多内部字段，会提高误用率并降低接口稳定性

## 验证 (Validation)

- 用已有 `evals/evals.json` 跑 canonical eval
- 用 production replay 跑运行时 case
- 用 negative / safety case 验证误触发与边界问题
- 对同一 skill 进行重复运行，检查稳定性与方差
- 用 JSON Schema 校验评测结果文件
- 用 Markdown schema 检查报告结构完整性

## 开放分支 (Open Branches)

- 如何统一接入现有 `skill-creator` 的执行结果格式
- 是否需要为 shadow mode 单独定义 trace 字段
- 报告是否要增加趋势对比（跨版本 comparison）

## 决策节点 (Decision Nodes)

- Result store 是先用 JSON 文件还是 SQLite
- Runtime replay 是直接复用 Claude CLI 录制回放，还是抽象为统一 adapter
- 高风险失败是否一律一票否决，还是区分 severity

## 外部依赖 (External Dependencies)

- `JSON Schema Draft 2020-12`：用于结果文件校验 ✓
- GitHub raw file fetch：用于获取外部仓库中的 `<skill>.md` ✓
- Markdown 报告约定：仓库内自定义，无外部依赖 ✓

## 结论 (Conclusion)

当前设计已经完成核心收敛，足以进入实现规划。剩余问题主要是存储与接入层的工程细节，而不是架构主干问题。
