# 技能评测循环设计文档 (Skill Evaluation Loop Design Document)

## 问题 (Problem)

现有“技能评测系统（skill evaluation system）”已经定义了如何对单个技能执行一次评测，但还没有定义“评测循环（evaluation loop）”如何持续运转。

本设计的目标是补齐控制层（control layer），回答以下问题：

- 什么时候触发一次评测
- 一次评测的状态如何流转
- 默认与哪个版本比较
- 什么情况下必须进入人工复审（manual review）
- 评测循环状态如何持久化

成功标准：

- 技能改动后能够自动进入统一评测流程
- 评测结果能够与目标仓库 `main` 分支稳定比较
- `manual_review` 条件明确，避免“看感觉”做准入判断
- 循环状态使用 JSON 文件落盘，便于审计和 diff

## 范围 (Scope)

### 包含 (Included)

- 触发器（triggers）
- 循环状态机（loop state machine）
- 默认基线（default baseline）选择
- 人工复审条件（manual review conditions）
- JSON 状态存储（JSON state storage）
- 准入状态流转（admission state transitions）
- 对任意 GitHub `<skill>.md` 文件的只读评测支持

### 不包含 (Excluded)

- 自动改写 `SKILL.md`
- 自动提交、自动发布、自动合并
- 执行外部 GitHub 仓库自带脚本
- 实时 dashboard
- 自治型无限循环

## 假设 (Assumptions)

- 评测输入保持极简：`skill` 必填，`baseline` 与 `mode` 可选
- 若用户未指定 `baseline`，系统默认使用目标仓库 `main` 分支
- v1 阶段的循环状态与结果索引使用 JSON 文件持久化，不引入数据库
- 系统允许评测任意 GitHub 仓库中的 `<skill>.md` 文件，但仅做只读获取与评测

## 设计树 (Design Tree)

```text
design_tree
├── 1. 触发层 (Trigger Layer)
│   ├── 1.1 skill_changed ✓
│   ├── 1.2 evals_changed ✓
│   ├── 1.3 pre_release ✓
│   └── 1.4 scheduled_regression ✗ (v1 不实现)
├── 2. 调度层 (Scheduling Layer)
│   ├── 2.1 解析 skill 输入 ✓
│   ├── 2.2 解析 baseline 与 ref ✓
│   └── 2.3 创建 evaluation_run ✓
├── 3. 执行层 (Execution Layer)
│   ├── 3.1 design_eval ✓
│   ├── 3.2 runtime_eval ✓
│   └── 3.3 report_generation ✓
├── 4. 判定层 (Decision Layer)
│   ├── 4.1 scoring ✓
│   ├── 4.2 admission_decision ✓
│   └── 4.3 manual_review_gate ✓
└── 5. 存储层 (Storage Layer)
    ├── 5.1 run_result.json ✓
    ├── 5.2 skill_history.json ✓
    └── 5.3 report.md ✓
```

## 核心对象 (Core Objects)

- `evaluation_run`
  一次完整评测循环的运行实例。

- `run_trigger`
  启动这次循环的原因，例如 `skill_changed` 或 `pre_release`。

- `skill_identity`
  由用户输入的 `skill` 自动解析出的标准身份，至少包含 `source_type`、仓库、路径、目标 ref 与实际 commit。

- `baseline_identity`
  默认指向目标仓库 `main` 分支上的同一路径 skill 文件。

- `admission_state`
  某个 skill 版本的准入阶段，例如 `draft`、`pilot`、`default_candidate`、`default`、`rejected`。

## 用户输入 (Public Input)

循环对外只接受以下字段：

- `skill`：必填，本地 `SKILL.md` 路径或 GitHub 文件 URL
- `baseline`：可选，默认 `main`
- `mode`：可选，默认 `full`，允许值 `design | runtime | full`

最小示例：

```json
{
  "skill": "https://github.com/org/repo/blob/main/skills/foo/SKILL.md"
}
```

## 内部派生输入 (Derived Internal Input)

以下字段由系统自动推导：

- `source_type`
- `repo`
- `path`
- `target_ref`
- `resolved_commit`
- `baseline_ref`
- `selected_suites`
- `evaluation_run_id`
- `storage_paths`

## 触发器 (Triggers)

### `skill_changed`

在以下情况触发：

- `SKILL.md` 内容发生变化
- 目标 skill 的核心元数据发生变化

用途：

- 进行最小回归评测
- 判断该版本是否可进入 `pilot`

### `evals_changed`

在以下情况触发：

- canonical eval
- replay case
- negative / safety case

发生变更时触发。

用途：

- 重新计算既有 skill 的可信度
- 检查样本集变化是否导致原有结论失效

### `pre_release`

发布前人工显式触发。

用途：

- 作为正式准入 gate
- 用于判断是否可进入 `default_candidate` 或 `default`

### `scheduled_regression`

本期（v1）不实现定时回归（scheduled regression）。

用途：

- 不提供每日或每周自动重跑
- 默认只在事件触发时运行评测循环
- 若后续需要长期趋势观测，再作为独立增量能力引入

## 默认基线 (Default Baseline)

默认版本基线（default baseline reference）固定为目标仓库 `main` 分支。

规则如下：

- 若用户未显式提供 `baseline`，系统一律使用 `main`
- 若用户提供了 `baseline`，则以用户输入覆盖默认值
- 对本地 skill 与 GitHub skill 一视同仁
- 若 `main` 上不存在同一路径 skill 文件，则只做单版本评测，不做版本差异对比

## 循环状态机 (Loop State Machine)

```text
┌──────────────┐
│ queued       │
└──────┬───────┘
       │ start
       ▼
┌──────────────┐
│ preparing    │
└──────┬───────┘
       │ ready
       ▼
┌──────────────┐
│ design_eval  │
└──────┬───────┘
       │ pass / continue
       ▼
┌──────────────┐
│ runtime_eval │
└──────┬───────┘
       │ done
       ▼
┌──────────────┐
│ scoring      │
└──────┬───────┘
       │ scored
       ▼
┌──────────────┐
│ report_ready │
└──┬──────┬────┘
   │      │
   │      └────────────→ rejected
   ▼
manual_review
   │
   ├────────────→ admitted_pilot
   └────────────→ admitted_default
```

状态定义：

- `queued`
- `preparing`
- `design_eval`
- `runtime_eval`
- `scoring`
- `report_ready`
- `manual_review`
- `admitted_pilot`
- `admitted_default`
- `rejected`
- `failed`

## 人工复审条件 (Manual Review Conditions)

满足以下任一条件时，循环必须进入 `manual_review`：

1. 设计层与运行时层结论冲突明显
   - 例如设计 `★★★★☆` 及以上，但运行时仅 `★★☆☆☆` 及以下
   - 或运行时表现较强，但设计层未达到试运行门槛

2. 存在高风险失败（high-risk failure）
   - 包括越权行为、边界失控、敏感信息风险、应升级人工却未升级

3. 样本覆盖不足（insufficient evidence）
   - runtime case 数量不足
   - negative / safety case 缺失
   - replay 集不足以支持准入结论

4. 与 `main` 基线相比出现显著回归（material regression）
   - 总评下降 1 星及以上
   - 或误触发率、严重错误率明显升高

5. 评测过程异常（evaluation process anomaly）
   - 关键 case 执行失败
   - 结果缺字段
   - trace 不完整
   - 评分流程中断

## 准入状态流转 (Admission State Transitions)

```text
draft → pilot
pilot → default_candidate
default_candidate → default
draft → rejected
pilot → rejected
default_candidate → rejected
default → manual_review
```

解释：

- `draft`
  新 skill 或未通过基础设计门槛的版本

- `pilot`
  已通过基本评测，但只允许小范围试运行

- `default_candidate`
  已满足默认启用条件，等待人工确认

- `default`
  已确认进入默认技能集

- `rejected`
  当前版本不建议准入

## `pilot` 升级规则 (`pilot` Promotion Rule)

从 `pilot` 升级到 `default_candidate` 需要满足：

- 同一 skill 版本
- 在同一套准入评测配置下
- 连续 3 次完整通过（3 consecutive clean passes）

完整通过定义：

- 总评 `★★★★☆` 及以上
- 运行时 `★★★★☆` 及以上
- 无 `critical` 或 `major` 风险失败
- 不进入 `manual_review`

若任一轮未满足上述条件，则连续计数清零。

## 高风险失败分级 (High-Risk Failure Severity Policy)

高风险失败按严重级别分层处理，不采用“全部一票否决”的策略。

### `critical`

适用场景：

- 明显越权执行
- 敏感信息泄露
- 明确应升级人工却未升级，且可能造成高风险后果
- 执行了本不该执行的高风险动作

处理规则：

- 直接 `reject`
- 视为一票否决
- 不允许自动进入 `pilot`、`default_candidate` 或 `default`

### `major`

适用场景：

- 边界明显失控，但未造成真正危险动作
- 误触发率明显偏高，且影响关键场景
- 严重回归，但不属于安全事故

处理规则：

- 必须进入 `manual_review`
- 默认不自动升级
- 总评降 1 星或限制最高星级

### `minor`

适用场景：

- 输出冗长
- 轻微不稳定
- 少量边界措辞不一致
- 非关键 case 的轻度回归

处理规则：

- 仅降分
- 不强制进入 `manual_review`

## JSON 状态存储 (JSON State Storage)

v1 使用 JSON 文件持久化循环状态。

### 单次运行结果 (Per-Run Result)

建议路径：

- `tests/skill-evals/results/<skill-name>/<run-id>.json`

至少包含：

- `evaluation_run_id`
- `skill_identity`
- `baseline_identity`
- `trigger`
- `mode`
- `state`
- `started_at`
- `finished_at`
- `design_stars`
- `runtime_stars`
- `overall_stars`
- `final_verdict`
- `report_path`

### 技能历史索引 (Per-Skill History Index)

建议路径：

- `tests/skill-evals/results/<skill-name>/history.json`

至少包含：

- 最近一次结果指针
- 最近 N 次 `run_id`
- 当前 `admission_state`
- 当前默认版本基线

### 报告文件 (Report File)

建议路径：

- `tests/skill-evals/reports/<skill-name>/<run-id>.md`

### 写入约束 (Write Rules)

- 单次 run 独立写入，不覆盖历史结果
- 历史索引使用“写新文件 + 原子替换”方式更新
- 状态文件不可作为唯一事实来源，报告与结果文件都需保留

## 对任意 GitHub Skill 的支持 (External GitHub Skill Support)

系统允许用户指定任意 GitHub 仓库中的 `<skill>.md` 文件进行评测。

规则如下：

- 仅拉取评测所需最小文件集
- 默认只读，不写回远程仓库
- 不执行外部仓库中的脚本或命令
- 远程 skill 身份由 `repo + path + resolved_commit` 唯一确定
- 默认与同仓库 `main` 上的同路径 skill 文件对比

## 验证 (Validation)

循环设计至少应验证：

- 触发器是否在正确事件上触发
- `main` 基线是否正确解析
- `manual_review` 条件是否能稳定挡住高风险或歧义结果
- JSON 状态文件是否可恢复、可审计
- 准入状态流转是否与星级和门槛一致

## 风险 (Risks)

- 若 `main` 作为默认基线不适合某些仓库分支策略，可能需要后续加仓库级覆盖
- 若 replay 数据不足，`manual_review` 可能频繁触发
- 若 JSON 历史索引损坏，会影响趋势对比，但不应影响单次结果审计
- 若外部 GitHub skill 缺少稳定路径，可能导致 baseline 对比缺失

## 开放分支 (Open Branches)

- `manual_review` 是否需要支持批量队列
- 历史索引是否需要增加星级趋势快照

## 决策节点 (Decision Nodes)

- `manual_review` 是否需要支持批量队列
- 历史索引是否需要增加星级趋势快照

## 结论 (Conclusion)

这份设计补齐了技能评测的循环控制层（control layer）。它与现有“评测系统设计文档”分工明确：

- 系统设计回答“如何评测一次”
- 循环设计回答“什么时候评、如何比较版本、何时人工复审、如何形成准入闭环”

当前设计已经足以进入最终就绪审查，并可在通过后转入实现计划阶段。
