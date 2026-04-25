# task-journal 取代 task-state-management 决策 (Task-Journal Replaces Task-State-Management)

> **状态 (Status):** 已采纳 (accepted)，2026-04-26。
>
> **取代关系 (Supersedes):**
> - `docs/design-decisions/2026-04-03-design-review-closure-and-task-state-integration.md`
> - `docs/design-tree/2026-04-02-continuous-state-system-phase-1.md`
>
> **影响范围 (Affects):** 所有需要把任务状态外化（externalize task state）落盘的 skill；具体的 tier 划分见 `skills/task-journal/SKILL.md`。

## 背景 (Context)

仓库在 2026-04-02 上线了 `task-state-management` 作为任务状态真相（task state source of truth）。它包含九个 Python 脚本、九种状态枚举、四类一等工件（status / events / states / ownership）、ownership lease、replay 恢复以及 v1 CLI 稳定承诺，目录定义在 `docs/tasks/<task-id>/`。

设施的诊断（diagnosis）是对的：**多个 skill 在没有共享状态时容易让任务状态在自然语言之间漂移（drift）**，handoff 退化为口头约定。

设施的实现并不匹配真实使用规模（real usage scale）：

- `docs/tasks/` 自上线起一直为空，没有任何真实任务被写入
- 单用户、Claude Code 主导的工作流没有 ownership 争用、replay 恢复、跨 agent 一致性这些诉求
- 工业级状态机（industrial-grade state machine）所需的写入摩擦（write friction）反而抑制了实际登记，进一步让 `docs/tasks/` 留空

> 失败模式（failure mode）不是"状态机不够强"，而是"问题尚未观察到失败时就预判性建造（speculative construction）"。

## 决策 (Decision)

把"状态真相（state truth）"重新交给文件系统 + git + memory 这三套已有持久化层（existing persistence layers）：

1. **数据载体 (Data carrier)**：每个任务一个目录 `<repo>/.agents/tasks/<task-id>/`，扁平布局，无 `active/` / `completed/` 分区；默认 `git` 不追踪（已被 `.agents/` 通配覆盖）。
2. **brief.md**：任务简报（task brief），首条 journal entry 写入后冻结（immutable）。
3. **journal.md**：append-only 的 markdown，所有 skill 在自己的里程碑（milestone）追加 entry。
4. **artifacts/**：任务私有的工件目录（task-private artifacts），承载超 15 行的长 body。

约束（constraints）由 `skills/task-journal/SKILL.md` 这份 prompt 与一个轻量 linter `scripts/lint_tasks.py` 守门，**不再造状态机（no state machine）**。

新设施总规模 ~300 行（含两个 stdlib helper），相比 `task-state-management` ~2000 行下降一个数量级。

具体协议（protocol）见 `skills/task-journal/SKILL.md`，本文不重复。

## 被否决的替代方案 (Alternatives Considered)

### 方案 A：维持 `task-state-management`，等首批真实使用再调整

- **拒绝原因**：维持成本（maintenance cost）已被支付（v1 CLI 稳定承诺、9 个脚本、9 个状态枚举），但收益（real usage）持续为零；继续维持会让所有下游 skill 接入时承担一份它们用不上的复杂度。

### 方案 B：用 SQLite 或单一 JSON 状态文件作为状态真相

- **拒绝原因**：相比 markdown，结构化存储让人类直接读写的成本上升；当前问题不在"如何查询状态"，而在"如何让 skill 在不互相约定的前提下也能记下里程碑"。markdown 命中后者的成本最低。

### 方案 C：状态机精简版（保留核心枚举 + 单一 events.jsonl）

- **拒绝原因**：任何"少量保留状态枚举"都会迅速回弹为完整状态机——枚举一旦稳定，下游 skill 会期望它表达更多语义，最终回到原点。append-only journal 没有枚举可膨胀（no enums to bloat）。

### 方案 D：只在 memory 系统里登记任务，不落到文件

- **拒绝原因**：memory 是私有给单个 agent 实例的，不是项目级的真相载体；多个 skill 之间需要一份可共享、可被 lint、可被 grep 的工件。

## 影响 (Consequences)

### 正面 (Positive)

- LLM 写入摩擦接近零：追加 markdown 即可，不必学习状态枚举或调用脚本
- 演化成本低：没有 schema lock；新增字段、调整约定都是 prompt-only 改动
- 跨工具读取友好：grep / cat / 编辑器都直接可用，不需要专用 reader
- 升级路径显式：本文末"未来演进"段落给出 7 类失效场景（failure scenarios）与对应升级方向，避免下一轮重走老路（regression）

### 负面 (Negative / Trade-offs)

- 没有 ownership lease，并发写入需要单写者协议（single-writer protocol）；当前单用户场景天然满足
- 没有结构化查询：跨任务统计需要 grep + 自建脚本；当 task 数 > 50 且查询频繁时再上 index（见升级信号）
- 无完成态目录迁移（no completion migration）：`done:` entry 即完成标记；这是有意为之，避免迁移引入的旁路状态
- 缺失 entry 是 warn 而非 error：约束相对宽松，依赖 SKILL.md prompt 与 review

## 未来演进与升级信号 (Future Evolution & Upgrade Signals)

`task-journal` 是**可被替换的初始约定（replaceable initial convention）**，不是终态。下表枚举可以触发再次升级的 7 类失效场景。每类都规定：触发条件（signal）、对应升级方向（upgrade direction）、和必须的证据形态。

| 失效场景 | 显式信号 | 升级方向 |
|---|---|---|
| 多 agent 并发写入 (concurrent writers) | journal 出现交错丢失（interleaved/lost entries），或 lint 检出多次时间戳乱序 | 引入 file lock 或单写者协议（single-writer protocol） |
| 跨任务索引查询频繁 (cross-task index queries) | 任务总数 > 50，且每周需要 ≥ 1 次 "哪些 task 引用了 X" 的查询 | 加 index 文件或 SQLite |
| 单 task 超长 journal (oversized journal) | 单文件 > 200 行或体感读取慢 | 滚动归档（rolling archive，例如 `journal-2026-Q1.md`） |
| 状态查询频繁 (frequent status queries) | 同一类 grep 查询每周 ≥ 5 次 | 加结构化 summary 命令 |
| 多人协作 (multi-human collaboration) | 仓库出现第 2 个真实人在用 task-journal | 切换 git-tracked + 加 `ownership` 字段 |
| journal 损坏 (corruption) | 实际损坏案例 ≥ 1 次 | 加 backup / checkpoint 机制 |
| CI / hook 集成 (automated invocation) | 出现稳定的自动调用需求（CI、pre-merge 等） | 加 thin CLI（每次只加一个命令） |

### Meta 守门 (Meta-Gate)

> 任何"重新加状态机（re-add the state machine）"的 PR 必须满足：
>
> 1. 指明已观察到的失效场景属于上面 7 类中**哪一类**
> 2. 说明信号触发次数（signal hit count）
> 3. 升级方向**限定在单一失效场景**，不附带其他范围扩张（no scope creep）
>
> 否则不接受。本守门写入 ADR，原因是上一轮 `task-state-management` 在没有任何观察到的失效（zero observed failure）时被建造，希望避免重演。

## 落地 (Implementation)

落地按以下顺序在同一窗口完成（详见 `/Users/youjunxin/.claude/plans/dreamy-forging-church.md`）：

1. 新建 `skills/task-journal/`（SKILL.md + 两个 stdlib helper + evals）
2. 评测通过后发布 (`mise run release`)
3. 标本文件取代的两份旧 design-decisions / design-tree 为 superseded
4. 移动三份 `docs/exec-plans/active/2026-04-02-task-state-management-phase-1*.md` 到 `completed/`
5. 删除 `docs/standards/task-state-management-*.md` 与 `docs/standards/skills/task-state-management-invocation-matrix.md`
6. 给 Tier B/C skill 的 SKILL.md 加 "Journal Integration" 段
7. 改 `task-brief` 的 Output 渲染规则与"创建任务目录"段落
8. 删除 `skills/task-state-management/`、`tests/task-state-management/`、`mise/tasks/check-task-state-management`
9. 同步 install path（`mise run pull` + 手动清理 `~/.claude` 与 `~/.agents` 下旧目录）

实施细节不属于本 ADR 范围。
