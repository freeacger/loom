# loom

**语言：** [English](README.md) | 简体中文

`loom` 是一个面向 Codex、Claude 类代理工具以及类似本地 agent 环境的工作流 skill 仓库。

本仓库中的大多数 skill 主要来自或参考自 [obra/superpowers](https://github.com/obra/superpowers)，然后再根据个人使用习惯做调整。它不是一个新的框架，也不是一个完整的平台，更接近于一套持续维护的个人 skill 集合。

## 这个仓库是什么

- 一组可复用的工作流 skill
- 一份带有本地调整的上游 skill 集合
- 一个服务于个人 agent 配置的参考仓库

## 这个仓库不是什么

- 不是完整的 agent 产品
- 不是插件或安装器
- 不是 `superpowers` 项目的替代品

## 当前范围

当前内容主要聚焦在工程流程类 skill，尤其包括：

- 先设计再实现
- 测试驱动开发
- 系统化排障
- 代码评审流程
- 基于 worktree 的隔离开发
- 完成前验证
- skill 编写与维护

## 当前维护的 Skills

目前仓库维护以下 skills：

| Skill | 用途 |
|---|---|
| `brainstorming` | 已停用的历史技能，仅在迁移期间保留目录作参考 |
| `decision-evaluation` | 对有边界的设计决策做方案比较并给出推荐 |
| `design-decision-audit` | 审查设计文档或计划文档中的缺失决策与上线缺口 |
| `design-orchestrator` | 在多个设计技能之间编排和路由设计阶段工作 |
| `design-readiness-check` | 判断当前设计是否足够完整，可以进入实现规划 |
| `design-refinement` | 将已有设计树继续细化到关键分支可落地的粒度 |
| `design-structure` | 将模糊想法整理成初始设计树和设计骨架 |
| `dispatching-parallel-agents` | 将彼此独立的任务分派给并行 agent |
| `executing-plans` | 按检查点分批执行已有实施计划 |
| `finishing-a-development-branch` | 在开发完成后处理合并、提 PR、保留或丢弃分支 |
| `receiving-code-review` | 收到评审意见后先做技术核实再决定修改 |
| `requesting-code-review` | 在继续开发或合并前发起结构化代码评审 |
| `subagent-driven-development` | 用专门的 subagent 执行计划任务并做分阶段评审 |
| `systematic-debugging` | 修复前先定位根因 |
| `task-brief` | 在执行前把原始请求整理成结构化任务简报 |
| `test-driven-development` | 用红绿重构流程驱动功能开发与修复 |
| `using-git-worktrees` | 在隔离的 git worktree 中开始开发 |
| `verification-before-completion` | 在声称完成前先用新鲜证据验证结果 |
| `writing-clearly-and-concisely` | 改进文档和其他面向人的文字表达 |
| `writing-plans` | 将需求整理成可执行的实施计划 |

## 仓库结构

```text
loom/
├── skills/                  # Skill 定义
│   └── <skill-name>/
│       ├── SKILL.md         # 主 skill 文档
│       └── ...              # 可选的辅助文件
├── docs/                    # 仓库说明和执行计划
└── LICENSE
```

## 与 `obra/superpowers` 的关系

本仓库明显受到 `obra/superpowers` 的影响。

具体来说：

- 有些 skill 基本直接沿用，只做少量修改
- 有些 skill 会根据本地工具行为和个人工作习惯调整
- 名称、措辞和流程细节可能与上游不完全一致

如果你想了解更完整的体系、上游文档或原始项目方向，应优先参考 [obra/superpowers](https://github.com/obra/superpowers)。

## 如何使用

通过 [skills.sh](https://skills.sh) 全局安装所有 skill：

```bash
npx skills add freeacger/loom -y -g
```

这会自动安装到 `~/.claude/skills/` 和 `~/.agents/skills/`。

也可以从 `skills/` 中挑选单个目录手动复制到本地 skill 目录，根据自己的环境调整措辞或路径。

## 为什么单独维护这个仓库

将这些 skill 单独放在一个仓库里，便于：

- 跟踪个人化调整
- 对比本地版本与上游版本的差异
- 在多台机器之间复用
- 记录当前实际在用的工作流

## 许可证

本仓库采用 [MIT License](LICENSE)。

对于来自上游项目的 skill 内容，请在复用或再分发前同时检查本仓库和上游项目的来源与许可说明。
