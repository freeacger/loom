# loom

**语言：** [English](README.md) | 简体中文

`loom` 是一个面向 Codex、Claude 类代理工具以及类似本地 agent 环境的工作流 skill 仓库。提供结构化、可组合的 skill，覆盖从想法到可发布代码的完整工程流程：设计、规划、实现、评审。

早期版本大量参考了 [obra/superpowers](https://github.com/obra/superpowers)，但项目已逐步发展出自己的设计流程管道、并行 agent 工作流和 skill 开发工具链。

## 覆盖范围

覆盖完整的工程生命周期：

- **设计** — 从模糊想法到可实施的结构化设计方案
- **规划** — 将需求转化为具体的、可分批执行的实施计划
- **实现** — 测试驱动开发、并行 agent 分派、计划执行
- **评审** — 代码评审（发起与接收）、设计文档审计
- **质量** — 系统化排障、完成前验证、清晰写作

## Skills

19 个 skill，按阶段分组：

### 设计 (Design)

| Skill | 用途 |
|---|---|
| `design-orchestrator` | 在多个设计技能之间编排和路由设计阶段工作 |
| `design-structure` | 将模糊想法整理成初始设计树和设计骨架 |
| `design-refinement` | 将已有设计树继续细化到关键分支可落地的粒度 |
| `decision-evaluation` | 对有边界的设计决策做方案比较并给出推荐 |
| `design-readiness-check` | 判断当前设计是否足够完整，可以进入实现规划 |
| `design-decision-audit` | 审查设计文档或计划文档中的缺失决策与上线缺口 |

### 规划 (Planning)

| Skill | 用途 |
|---|---|
| `task-brief` | 在执行前把原始请求整理成结构化任务简报 |
| `writing-plans` | 将需求整理成可执行的实施计划 |

### 实现 (Implementation)

| Skill | 用途 |
|---|---|
| `test-driven-development` | 用红绿重构流程驱动功能开发与修复 |
| `executing-plans` | 按检查点分批执行已有实施计划 |
| `subagent-driven-development` | 用专门的 subagent 执行计划任务并做分阶段评审 |
| `dispatching-parallel-agents` | 将彼此独立的任务分派给并行 agent |
| `using-git-worktrees` | 在隔离的 git worktree 中开始开发 |
| `systematic-debugging` | 修复前先定位根因 |

### 评审与质量 (Review & Quality)

| Skill | 用途 |
|---|---|
| `requesting-code-review` | 在继续开发或合并前发起结构化代码评审 |
| `receiving-code-review` | 收到评审意见后先做技术核实再决定修改 |
| `finishing-a-development-branch` | 在开发完成后处理合并、提 PR、保留或丢弃分支 |
| `verification-before-completion` | 在声称完成前先用新鲜证据验证结果 |
| `writing-clearly-and-concisely` | 改进文档和其他面向人的文字表达 |

## 仓库结构

```text
loom/
├── skills/                  # Skill 定义
│   └── <skill-name>/
│       ├── SKILL.md         # 主 skill 文档
│       ├── agents/          # 并行 agent 模板（可选）
│       └── evals/           # 评估测试用例（可选）
├── docs/
│   ├── standards/           # 标准与风格指南
│   ├── design-decisions/    # 设计决策记录
│   ├── design-tree/         # 设计阶段分析产物
│   ├── exec-plans/          # 执行计划（活跃/已完成）
│   ├── reports/             # 时效性报告与审计产物
│   └── workflows/           # 工作流文档
├── scripts/                 # 工具脚本（hooks、生成器）
├── mise/                    # Mise 任务定义
├── tests/                   # 评估工作空间
├── AGENTS.md                # Agent 规则
├── mise.toml                # 任务运行器配置
└── LICENSE
```

## 快速开始

通过 [skills.sh](https://skills.sh) 全局安装所有 skill：

```bash
npx skills add freeacger/loom -y -g
```

这会自动安装到 `~/.claude/skills/` 和 `~/.agents/skills/`。

也可以从 `skills/` 中挑选单个目录手动复制到本地 skill 目录。

## 致谢

部分 skill 的初始版本来源于或参考了 [obra/superpowers](https://github.com/obra/superpowers)，感谢其奠定的基础。这些 skill 在本仓库中已被大幅重写和扩展。

## 许可证

[MIT License](LICENSE)。
