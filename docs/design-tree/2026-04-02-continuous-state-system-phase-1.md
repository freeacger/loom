# 连续状态系统 Phase 1 设计树 (Continuous State System Phase 1 Design Tree)

## 问题 (Problem)

当前设计树系列技能已经在“概念路由（concept routing）”上形成较清楚的能力边界，但对技能使用方而言，仍缺少一套跨 `design -> planning -> execution` 连续推进的显式状态系统。缺口不在单一 `writing-plans` 技能，而在于：

- 缺少可依赖的阶段状态（state）分层
- 缺少稳定的阶段交接（handoff）与版本锚点（version anchors）
- 缺少基于事件流（event stream）的恢复与一致性校验
- 历史经验（historical learnings）虽已识别为独立问题域，但不应进入 Phase 1 实现范围

本设计文档的目标，是把当前对话中已收敛的设计状态正式落盘，作为进入实现规划（implementation planning）前的设计树工件。

## 范围 (Scope)

### 包含 (Included)

- 面向技能使用方的连续状态系统（continuous state system）Phase 1 边界
- 主树、子树 A、子树 B 的问题域划分
- `docs/tasks/<task-id>/` 目录布局
- `design-state.json`、`plan-state.json`、`execution-state.json` 的状态分层
- `events.jsonl`、`status.md` 的职责边界
- 事件优先（event-first）的状态收敛顺序
- stale / recovery / invalid 的状态有效性（validity）规则
- Phase 1 与 Phase 2 的切分

### 不包含 (Excluded)

- `docs/memory/` 下正式历史经验系统的实现
- `memory-curation` 技能的详细输入输出契约
- memory 检索、排序、注入、淘汰的自动化实现
- 跨仓库或跨项目共享 memory
- UI dashboard 或可视化管理界面

## 假设 (Assumptions)

- 本设计面向“采用这些技能的使用方”，不是仅服务本仓库自身维护流程
- Phase 1 的目标是先跑通任务状态系统，不追求一次性覆盖完整历史经验系统
- `status.md` 是人读视图（human-readable view），不是机器真相（machine truth）

## 强制规则 (Mandatory Rules)

### 状态根目录规则 (State Root Rule)

- `docs/` 是唯一合法状态根目录（the only valid state root）
- 所有任务状态、事件流、记忆工件都必须位于 `docs/` 下
- 技能不得将这些工件写入仓库其他目录
- 若运行环境不允许使用 `docs/`，则该环境不在支持范围内

### 支持前提 (Support Preconditions)

- 仓库根目录可写
- `docs/` 可创建或可写
- 使用方接受 `docs/` 下出现状态工件与记忆工件

### 任务标识规则 (Task ID Rule)

- `task-id` 采用固定命名规范：`YYYYMMDD-<task-name>-<2位随机字符>`
- `<task-name>` 使用稳定、可读的 `kebab-case`
- `task-id` 必须在仓库内唯一

### 脚本协同规则 (Script Collaboration Rule)

- Phase 1 的状态维护机制不应只靠自然语言 skill 执行
- 对 `events.jsonl`、`states/*.json`、恢复与校验相关的确定性操作，应由脚本协同完成
- 脚本应放在对应 skill 目录下的 `scripts/` 子目录
- Phase 1 默认脚本语言为 Python
- shell 只允许作为薄包装（thin wrapper），不得承载核心状态逻辑

## 主树 (Primary Design Tree)

```text
design_tree
├── 1. 问题定义 (Problem Definition)
│   ├── 1.1 使用方可见能力边界 ✓
│   └── 1.2 非目标与排除项 ✓
├── 2. 范围与边界 (Scope and Boundaries)
│   ├── 2.1 共享契约 vs 本地适配 ✓
│   └── 2.2 单任务状态 vs 历史经验 ✓
├── 3. 状态层模型 (State Layer Model)
│   ├── 3.1 design_state ✓
│   ├── 3.2 plan_state ✓
│   ├── 3.3 execution_state ✓
│   └── 3.4 historical_learnings ✓
├── 4. 阶段路由规则 (Stage Routing Rules)
│   ├── 4.1 design -> planning ✓
│   ├── 4.2 planning -> execution ✓
│   └── 4.3 execution -> learning capture ✓
├── 5. Handoff 形式 (Handoff Forms)
│   ├── 5.1 摘要 + 引用 + 必要字段 ✓
│   ├── 5.2 版本锚点（version anchors）✓
│   └── 5.3 失效与再验证（stale / revalidation）✓
├── 6. 持久化策略 (Persistence Strategy)
│   ├── 6.1 docs/tasks 与 docs/memory 布局 ✓
│   ├── 6.2 事件优先、状态收敛（event-first）✓
│   └── 6.3 使用方依赖保证 ✓
├── 7. 可观测性与状态视图 (Observability and State Views)
│   ├── 7.1 status.md 作为人读视图 ✓
│   └── 7.2 真相裁定与恢复（truth / recovery）✓
├── 8. 历史经验接口 (Historical Learning Interface)
│   ├── 8.1 intake / learnings 分层 ✓
│   ├── 8.2 记忆分类表（memory taxonomy）✓
│   ├── 8.3 准入标准（admission criteria）✓
│   ├── 8.4 记忆沉淀技能（memory-curation）[OPEN]
│   └── 8.5 注入触发策略（injection trigger policy）✓
└── 9. 验证与退出条件 (Validation and Exit Conditions)
    ├── 9.1 状态一致性校验 ✓
    └── 9.2 子树派生条件 ✓
```

## 核心状态对象 (Core State Objects)

### 设计状态 (Design State)

`design_state` 持有设计阶段的权威信息，包括问题定义、范围、设计树、开放分支、决策节点、风险、验证要求与设计阶段状态。它不承担执行事实与运行期进度。

### 计划状态 (Plan State)

`plan_state` 持有实现计划（implementation plan）的拆分结果、依赖顺序、验证计划与进入执行前的阻塞项。它不复制完整设计树，只引用设计状态及其版本锚点。

### 执行状态 (Execution State)

`execution_state` 持有执行事实（execution facts），包括当前执行单元、已完成单元、活跃发现、阻塞项、最新验证结果与执行阶段状态。它不能反向改写设计或计划的权威内容，只能通过事件反馈推动再验证。

### 历史经验 (Historical Learnings)

`historical_learnings` 已被确认为独立问题域，但不进入 Phase 1 实现范围。Phase 1 只保留其接口与挂点，不实现完整生命周期。

## 目录布局 (Directory Layout)

Phase 1 约定的任务目录如下：

```text
docs/
  tasks/
    <task-id>/
      status.md
      events.jsonl
      states/
        design-state.json
        plan-state.json
        execution-state.json
```

目录职责如下：

- `events.jsonl`：历史真相（historical truth）
- `states/*.json`：当前真相（current truth）
- `status.md`：派生视图（derived view）

历史经验相关目录在 Phase 2 中再启用：

```text
docs/
  memory/
    intake/
      learnings.jsonl
    learnings/
      <memory-id>.json
```

任务目录不使用 `active/` 与 `completed/` 子目录区分状态。任务是否完成，只能由状态文件中的 `lifecycle_state` 表达，而不能由目录位置表达。

## 提交策略 (Commit Policy)

### `docs/tasks/`

- `docs/tasks/<task-id>/status.md`、`events.jsonl`、`states/*.json` 属于任务级状态工件（task-scoped state artifacts）
- 默认视为应提交工件（commit-worthy artifacts），因为它们共同定义了任务的当前真相、历史事件与恢复基础
- 如果某个使用方环境不希望将这些工件提交到版本控制（version control），则该环境不在当前 Phase 1 设计的默认支持范围内
- Phase 1 不使用目录迁移表达任务完成
- 若后续需要归档，归档只能作为可选维护动作（optional maintenance action），不能替代状态真相

### `docs/memory/`

- `docs/memory/intake/*.jsonl` 与 `docs/memory/learnings/*.json` 在 Phase 2 中默认也视为应提交工件
- `intake` 记录原始候选经验流，`learnings` 记录正式记忆对象，两者都属于系统可追溯性的组成部分
- 当前设计不提供 `.gitignore` 模式、临时目录回退模式或仓库外 memory 存储模式

## 状态契约 (State Contracts)

### 双轴状态模型 (Two-Axis Status Model)

所有阶段状态文件共享统一 `status` 子对象，并拆成两个轴：

- 生命周期状态（lifecycle_state）
  - `draft|in_progress|blocked|ready|completed|abandoned`
- 有效性状态（validity_state）
  - `valid|stale|recovery_needed|invalid`

最小形状如下：

```json
{
  "status": {
    "phase": "design|planning|execution",
    "lifecycle_state": "draft|in_progress|blocked|ready|completed|abandoned",
    "validity_state": "valid|stale|recovery_needed|invalid",
    "blocking_issues": [],
    "updated_at": "",
    "owner": ""
  }
}
```

任务完成的判定规则如下：

- 任务是否完成，只由 `execution-state.json.status.lifecycle_state = completed` 判定
- 目录位置不参与完成态判断
- 如果未来引入归档（archive），归档只能是派生存储动作，不是状态机语义

### 版本锚点 (Version Anchors)

每个状态文件至少包含：

```json
{
  "meta": {
    "state_version": 0,
    "last_applied_event_id": ""
  }
}
```

下游状态必须额外记录上游引用与版本锚点，例如：

```json
{
  "source_design_ref": "",
  "source_design_version": 0,
  "source_design_event_id": ""
}
```

```json
{
  "source_plan_ref": "",
  "source_plan_version": 0,
  "source_plan_event_id": ""
}
```

## 核心流程 (Core Flows)

### 事件优先收敛流程 (Event-First Convergence Flow)

统一写入顺序固定为：

```text
append event -> update state snapshot -> refresh status.md
```

解释如下：

- 先追加事件，确保变化先进入事件流
- 再更新状态快照，形成当前真相
- 最后刷新 `status.md`，提供人读总览

上述流程在实现上默认由脚本承担关键动作，包括：

- 追加 `events.jsonl`
- 原子更新 `states/*.json`
- 校验 `last_applied_event_id`
- 执行 replay / recovery
- 执行一致性校验

### 阶段交接流程 (Phase Handoff Flow)

Phase 1 只覆盖两段 handoff：

1. `design -> planning`
2. `planning -> execution`

每次合法 handoff 都必须留下：

- 上游状态引用
- 上游版本号
- 上游事件锚点
- `handoff_completed` 事件

## 并发与 Ownership (Concurrency and Ownership)

Phase 1 采用单写者 + ownership 模型：

- 任一时刻，同一 `task-id` 只允许一个 writer 修改 `events.jsonl` 与 `states/*.json`
- 当前 writer 对该任务拥有显式 ownership
- 未取得 ownership 的其他会话、agent 或人工流程默认只能只读
- 如果需要交接写入者，应先显式转移 ownership，再继续写入

该规则用于保护：

- 事件流与快照的一致性
- 版本锚点的可追溯性
- stale / recovery / invalid 状态判断的稳定性

### 唯一写入口规则 (Single Write Path Rule)

Phase 1 明确采用唯一写入口（single write path）：

- 只有 `skills/task-state-management/scripts/` 下的脚本允许直接写入：
  - `docs/tasks/<task-id>/events.jsonl`
  - `docs/tasks/<task-id>/states/*.json`
  - `docs/tasks/<task-id>/status.md`
- 其他 skill 不得直接 patch 或覆写上述状态工件
- `design-*`、`writing-plans`、`executing-plans` 等业务 skill 只能通过调用 `task-state-management` 脚本触发状态变化
- 如果某个实现绕过脚本直接修改状态工件，则视为违反 Phase 1 状态契约

### Ownership 最小契约 (Ownership Minimum Contract)

Phase 1 的 ownership 至少满足以下最小运行契约：

- ownership 必须有独立记录，不与 `design-state.json`、`plan-state.json`、`execution-state.json` 混写
- ownership 记录至少包含：
  - `task_id`
  - `owner_id`
  - `acquired_at`
  - `lease_expires_at`
- `acquire_ownership.py` 负责：
  - 首次获取 ownership
  - 续租（renew）
  - 冲突检测
  - 必要时的强制接管（force takeover）
- `transfer_ownership.py` 负责显式转移 ownership
- 未持有 ownership 的写入请求必须失败，而不是降级为 best effort 写入

### 脚本调用责任映射 (Script Invocation Responsibility Mapping)

Phase 1 采用“状态脚本拥有能力、业务 skill 负责调用”的分工：

- `design-*` 相关 skill 负责在设计阶段调用：
  - `create_task.py`
  - `append_event.py`
  - `update_state.py`
  - `handoff_state.py`
  - `refresh_status_view.py`
- `writing-plans` 负责在 planning 阶段调用：
  - `append_event.py`
  - `update_state.py`
  - `handoff_state.py`
  - `add_blocker.py`
  - `clear_blocker.py`
  - `refresh_status_view.py`
- `executing-plans` 负责在 execution 阶段调用：
  - `append_event.py`
  - `update_state.py`
  - `add_blocker.py`
  - `clear_blocker.py`
  - `revalidate_state.py`
  - `complete_task.py`
  - `refresh_status_view.py`
- `validate_state.py` 与 `replay_events.py` 由所有业务 skill 共享调用，但仍归 `task-state-management` 拥有

### 第一批实现切片 (First Verifiable Slice)

Phase 1 不要求 13 个脚本同时完成。第一批可验证切片（first verifiable slice）建议先落这 5 个：

- `create_task.py`
- `append_event.py`
- `update_state.py`
- `refresh_status_view.py`
- `validate_state.py`

这 5 个脚本应先验证以下最小闭环：

- 创建任务目录与初始状态
- 追加事件并分配 `event_seq`
- 更新快照并推进 `state_version`
- 由快照重建 `status.md`
- 对任务目录执行一致性校验

第二批再补：

- `handoff_state.py`
- `add_blocker.py`
- `clear_blocker.py`
- `revalidate_state.py`
- `complete_task.py`

Ownership 相关脚本可与第二批并行，也可以在第一批后立即补齐，取决于实现时是否需要真正支持多会话竞争同一 `task-id`。

## 技能与脚本组织 (Skill and Script Organization)

Phase 1 相关脚本默认由独立的 `task-state-management` skill 拥有。其他 skill 可以调用这些脚本，但不拥有它们。

推荐组织方式如下：

```text
skills/task-state-management/
  SKILL.md
  REFERENCE.md
  scripts/
    create_task.py
    acquire_ownership.py
    transfer_ownership.py
    append_event.py
    update_state.py
    handoff_state.py
    add_blocker.py
    clear_blocker.py
    complete_task.py
    refresh_status_view.py
    revalidate_state.py
    replay_events.py
    validate_state.py
```

组织原则如下：

- `task-state-management` 是状态维护脚本的单一真相（single source of truth）
- `design-*`、`writing-plans`、`executing-plans` 等其他 skill 可以调用这些脚本，但不应复制或分叉维护它们
- `SKILL.md` 负责定义规则、触发条件、边界与异常升级条件
- `REFERENCE.md` 负责补充细节说明
- `scripts/` 负责状态维护相关的确定性动作
- 状态机语义保留在设计文档与 skill 文本中
- 原子写入、重放、校验与恢复等高风险动作默认下沉到 Python 脚本

### 脚本接口总规则 (Script Interface Rules)

Phase 1 的状态维护脚本统一采用以下接口约定：

- 输入（input）优先通过显式命令行参数传递；结构化负载（structured payload）较复杂时允许读取 JSON 文件路径
- 输出（output）默认写到标准输出（stdout），且采用单个 JSON 对象，便于其他 skill 或脚本继续消费
- 错误信息写到标准错误（stderr），并返回非零退出码（non-zero exit code）
- 成功时必须返回至少以下字段：
  - `ok`
  - `task_id`
  - `changed_files`
  - `result`
- 任何会修改状态的脚本，都必须显式接收 `task-id`
- 任何会推进事件流的脚本，都必须返回本次写入或消费的 `event_id`；若有顺序分配，还必须返回 `event_seq`
- 任何会更新快照的脚本，都必须返回受影响状态文件的 `state_version`

### Phase 1 脚本范围与输入输出 (Phase 1 Script Scope and Inputs/Outputs)

#### `create_task.py`

- 输入：
  - `task_name`
  - 可选 `date`
  - 可选 `random_suffix`
  - 可选 `initial_goal`
- 输出：
  - `task_id`
  - `task_dir`
  - `changed_files`
  - 初始化后的 `design-state.json`、`plan-state.json`、`execution-state.json` 路径
  - 首个 `task_created` 事件的 `event_id` 与 `event_seq`

#### `acquire_ownership.py`

- 输入：
  - `task_id`
  - `owner_id`
  - 可选 `lease_seconds`
  - 可选 `force`
- 输出：
  - `task_id`
  - `owner_id`
  - ownership 文件路径或 ownership 记录位置
  - `lease_expires_at`
  - `changed_files`

#### `transfer_ownership.py`

- 输入：
  - `task_id`
  - `from_owner_id`
  - `to_owner_id`
  - 可选 `reason`
- 输出：
  - `task_id`
  - 原 ownership 信息
  - 新 ownership 信息
  - `changed_files`

#### `append_event.py`

- 输入：
  - `task_id`
  - `event_type`
  - `phase`
  - `source`
  - `summary`
  - `payload` 或事件负载文件路径
- 输出：
  - `task_id`
  - 新增事件的 `event_id`
  - 新增事件的 `event_seq`
  - `events_file`
  - `changed_files`

#### `update_state.py`

- 输入：
  - `task_id`
  - `state_kind`：`design|plan|execution`
  - `patch` 或补丁文件路径
  - `expected_last_applied_event_id`
  - 可选 `expected_state_version`
- 输出：
  - `task_id`
  - `state_file`
  - 更新后的 `state_version`
  - 更新后的 `last_applied_event_id`
  - `changed_files`

#### `handoff_state.py`

- 输入：
  - `task_id`
  - `from_phase`
  - `to_phase`
  - `source_state_version`
  - `source_event_id`
  - handoff 摘要或 handoff 文件路径
- 输出：
  - `task_id`
  - `from_state_file`
  - `to_state_file`
  - 下游状态写入结果
  - 产生的 `handoff_completed` 事件的 `event_id` 与 `event_seq`
  - `changed_files`

#### `add_blocker.py`

- 输入：
  - `task_id`
  - `state_kind`
  - `blocking_issue`
- 输出：
  - `task_id`
  - `state_file`
  - 新增 blocker 的 `blocking_issue_id`
  - 对应事件的 `event_id` 与 `event_seq`
  - `changed_files`

#### `clear_blocker.py`

- 输入：
  - `task_id`
  - `state_kind`
  - `blocking_issue_id`
- 输出：
  - `task_id`
  - `state_file`
  - 清除结果
  - 若状态从 `blocked` 恢复，则返回更新后的 `lifecycle_state`
  - 对应事件的 `event_id` 与 `event_seq`
  - `changed_files`

#### `complete_task.py`

- 输入：
  - `task_id`
  - `completion_summary`
  - 可选 `expected_validity_state`
  - 可选 `expected_no_blockers`
- 输出：
  - `task_id`
  - `execution-state.json` 路径
  - 更新后的 `lifecycle_state`
  - `task_completed` 事件的 `event_id` 与 `event_seq`
  - `changed_files`

#### `refresh_status_view.py`

- 输入：
  - `task_id`
  - 可选 `state_kind`
  - 可选 `template`
- 输出：
  - `task_id`
  - `status.md` 路径
  - 刷新后的视图摘要
  - `changed_files`

#### `revalidate_state.py`

- 输入：
  - `task_id`
  - `state_kind`
  - `against_source_version`
  - `reason`
- 输出：
  - `task_id`
  - `state_file`
  - 更新后的 `validity_state`
  - 更新后的 `state_version`
  - `state_revalidated` 事件的 `event_id` 与 `event_seq`
  - `changed_files`

#### `replay_events.py`

- 输入：
  - `task_id`
  - 可选 `from_event_seq`
  - 可选 `to_event_seq`
  - 可选 `state_kind`
- 输出：
  - `task_id`
  - 被重放的事件范围
  - 被重建或修复的状态文件列表
  - 每个状态文件的最终 `state_version`
  - `changed_files`

#### `validate_state.py`

- 输入：
  - `task_id`
  - 可选 `strict`
  - 可选 `state_kind`
- 输出：
  - `task_id`
  - 校验结果：`ok|warning|recovery_needed|invalid`
  - 发现列表（findings）
  - 建议动作（recommended_actions）
  - `changed_files`，默认为空

### Python 规范 (Python Conventions)

Phase 1 脚本默认采用 Python，并遵循以下实现规范：

- 目标 Python 版本固定为 `Python 3.11+`
- 每个脚本只负责一个清晰动作（single clear action），不要把创建、校验、修复混在同一入口
- 命令行接口（CLI interface）优先使用 `argparse`
- 成功输出固定为单个 JSON 对象；不得混入解释性自然语言
- 错误输出固定写到 `stderr`，并附带稳定的错误码（error code）或错误类型（error type）
- 写入 `states/*.json` 时必须采用“临时文件 + 原子替换（atomic replace）”策略
- 读写 JSON 时必须显式处理 UTF-8、空文件、损坏文件与 schema 缺失字段
- 任何修改状态的脚本都必须先校验 ownership，再执行写入
- 任何推进事件流的脚本都必须保证 `event_seq` 单调递增
- 任何重放（replay）逻辑都必须基于 `last_applied_event_id` 或 `event_seq` 保持幂等（idempotent）
- Python 注释、错误消息模板与帮助文本都应服务状态维护，不写冗长解释
- 如果未来需要 shell 包装，shell 只负责参数转发与环境准备，不得复制 Python 中的状态机逻辑

### 脚本验证标准 (Script Validation Criteria)

Phase 1 的状态维护脚本在进入可用状态前，至少应满足以下验证标准：

#### 接口验证 (Interface Validation)

- 每个脚本都必须覆盖缺失参数、非法参数、非法 `task_id` 与非法 `state_kind` 的失败路径
- 成功输出必须始终是单个 JSON 对象，且包含约定字段：
  - `ok`
  - `task_id`
  - `changed_files`
  - `result`
- 错误输出必须写入 `stderr`，并返回稳定的非零退出码
- 任何声明会产出 `event_id`、`event_seq`、`state_version` 的脚本，都必须在成功返回中稳定提供这些字段

#### 一致性验证 (Consistency Validation)

- `append_event.py` 必须保证同一任务下 `event_seq` 单调递增
- `update_state.py`、`handoff_state.py`、`revalidate_state.py` 必须保证：
  - `last_applied_event_id` 与实际事件链一致
  - `state_version` 单调递增
  - `source_*_version` 与 `source_*_event_id` 不回退
- `refresh_status_view.py` 生成的 `status.md` 必须完全可由 `states/*.json` 推导，不得引入新的机器真相字段
- `validate_state.py` 必须能识别至少以下结果：
  - `ok`
  - `warning`
  - `recovery_needed`
  - `invalid`

#### 恢复验证 (Recovery Validation)

- 当事件已成功写入、但状态快照未更新时，`replay_events.py` 必须能基于事件流恢复快照
- 当 `status.md` 过期时，`refresh_status_view.py` 必须能在不修改核心状态的前提下重建视图
- 当快照损坏、缺失或与事件链冲突时，`validate_state.py` 必须显式报告 `recovery_needed` 或 `invalid`
- `replay_events.py` 必须保持幂等：重复执行同一重放范围，不得重复推进 `state_version` 或重复应用 blocker、handoff、完成态等副作用

#### Ownership 与并发验证 (Ownership and Concurrency Validation)

- 任何修改状态的脚本都必须在写入前验证当前 ownership
- 未持有 ownership 的写入请求必须被拒绝，而不是静默覆盖
- `acquire_ownership.py` 必须能覆盖首次获取、续租、冲突获取与强制接管等路径
- `transfer_ownership.py` 必须保证 ownership 变更前后状态可追溯，且不会产生“双写者可同时写入”的窗口

#### 生命周期验证 (Lifecycle Validation)

- `add_blocker.py` 与 `clear_blocker.py` 必须正确驱动 `lifecycle_state` 在 `in_progress`、`blocked` 间迁移
- `revalidate_state.py` 必须是 `stale -> valid` 的唯一合法自动化入口
- `complete_task.py` 只能在满足完成前提时写入 `completed`，例如：
  - `validity_state = valid`
  - blocker 已清空，或调用方显式放宽该要求
- 已完成任务在重复刷新 `status.md`、重复执行校验或重复读取时，不得回退为未完成状态

## 真相裁定与恢复 (Truth Order and Recovery)

### 真相裁定顺序 (Truth Order)

冲突时按以下顺序裁定：

1. `events.jsonl` 负责解释“发生了什么”
2. `states/*.json` 负责解释“现在是什么”
3. `status.md` 负责解释“现在最值得人看什么”

### 恢复规则 (Recovery Rules)

- 事件已写入但快照未更新：
  - 进入 `recovery_needed`
  - 通过事件重放（replay）修复快照
- 快照已更新但 `status.md` 过期：
  - 只刷新 `status.md`
- 事件链与快照冲突：
  - 进入 `invalid`
  - 禁止静默继续自动推进

## 子树 A：跨阶段推进工作流 (Child Tree A: Cross-Stage Progression Workflow)

```text
design_tree
├── 1. 阶段定义 (Stages) ✓
├── 2. 输入与输出 (Inputs and Outputs) ✓
├── 3. 状态转移规则 (State Transition Rules) ✓
├── 4. Blocker 与阻力处理 (Blocker Handling) ✓
├── 5. Readiness 与质量门禁 (Readiness and Quality Gates) ✓
├── 6. 恢复与重试路径 (Recovery and Retry Paths) ✓
├── 7. 用户状态视图 (User-Facing Status Views) ✓
└── 8. 验证 (Validation) ✓
```

该子树负责：

- 阶段推进
- blocker / recovery
- readiness / progress 视图
- 再验证入口（revalidation entry points）

它不拥有 memory 生命周期与 memory 注入能力。

## 子树 B：历史经验回注系统 (Child Tree B: Historical Learning Injection System)

```text
design_tree
├── 1. 经验来源 (Learning Sources) ✓
├── 2. 经验分类与准入 (Taxonomy and Admission) ✓
├── 3. intake 与正式记忆分层 (Intake vs Curated Memory) ✓
├── 4. 注入触发策略 (Injection Trigger Policy) ✓
├── 5. 注入记录与采纳边界 (Injection vs Apply Boundary) ✓
├── 6. 记忆沉淀技能（memory-curation）[OPEN]
└── 7. 验证与淘汰 (Validation and Deprecation) ✓
```

该子树已完成问题域边界定义，但不进入 Phase 1 实现。`memory-curation` 被明确降级为子树中的待完成能力项（pending capability），而不是新的顶层状态层。

## 使用方依赖保证 (User-Facing Reliability Guarantees)

Phase 1 向使用方承诺以下最小保证：

- 一旦事件成功追加到 `events.jsonl`，该变化最终应可收敛到状态快照
- 每次合法 handoff 都可追溯到上游引用与版本锚点
- 若事件与快照不一致，系统必须显式进入 `recovery_needed` 或 `invalid`
- `status.md` 允许短暂落后，但必须可由快照重建

Phase 1 明确不保证：

- memory 自动沉淀
- memory 自动注入与排序
- 跨任务自动经验共享
- stale 自动恢复为 valid
- 多写者并发修改同一任务目录

## 已冻结决策 (Frozen Decisions)

- Phase 1 只实现 `docs/tasks/` 下的连续状态系统
- Phase 2 再引入 `docs/memory/` 与 `memory-curation`
- 当前任务状态采用 3 个独立 JSON，而不是单一 `state.json`
- `status.md` 不是机器真相
- `events.jsonl` 是 append-only 事件流
- stale 只能通过当前阶段 owner 的再验证清除
- `injected` 与 `applied` 必须严格分离
- Phase 1 采用单写者 + ownership 模型
- 任务完成只由状态字段表达，不由目录迁移表达
- `task-id` 固定采用 `YYYYMMDD-<task-name>-<2位随机字符>`
- 状态维护相关的确定性操作默认脚本化
- Phase 1 默认脚本语言为 Python
- 状态维护脚本由独立的 `task-state-management` skill 拥有

## Phase 切分 (Phase Split)

### Phase 1 (MVP)

Phase 1 只实现任务状态系统最小闭环：

- `docs/tasks/<task-id>/states/*.json`
- `events.jsonl`
- `status.md`
- handoff、版本锚点、stale / recovery / invalid
- 基本一致性校验与 revalidation
- 单写者 + ownership
- 通过状态字段表达任务完成
- Python 脚本承担状态维护关键动作

### Phase 2

Phase 2 再实现历史经验系统：

- `docs/memory/intake/learnings.jsonl`
- `docs/memory/learnings/<memory-id>.json`
- `memory-curation`
- memory lifecycle
- learning injection / apply

## Readiness 结论 (Readiness Verdict)

本设计在主树与两个子树上已达到“停止继续扩树”的程度。为进入实现规划，关键切分已经完成：

- 主树已基本闭合
- 子树 A 已具备进入实现规划的边界清晰度
- 子树 B 已完成问题域收敛，但整体推迟到 Phase 2

因此，本设计文档的最终结论是：

- **Phase 1 设计已准备进入实现规划（planning-ready）**
- **Phase 2 记忆系统仍保留为后续阶段设计与实现事项**

## 下一步 (Next Step)

下一步应基于本文档进入 `writing-plans`，为 Phase 1 产出实施计划（implementation plan），而不是继续扩展设计树。
