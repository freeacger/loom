# loom

**Language:** English | [简体中文](README.zh-CN.md)

`loom` is a small repository of workflow skills for Codex, Claude-style agents, and similar local agent setups.

Most skills in this repository are taken from or adapted from [obra/superpowers](https://github.com/obra/superpowers), then adjusted to fit personal workflow preferences. This repo does not try to present itself as a new framework or a complete platform. It is primarily a maintained personal skill set with a few local changes.

## What This Repository Is

- A curated set of reusable workflow skills
- A place to keep locally adjusted versions of upstream skills
- A reference repo for personal agent setup

## What This Repository Is Not

- Not a full agent product
- Not a plugin or installer
- Not a replacement for the upstream `superpowers` project

## Current Scope

The repository currently focuses on process and engineering workflow skills, especially:

- planning before implementation
- test-driven development
- systematic debugging
- code review workflows
- worktree-based isolation
- completion verification
- skill authoring

## Skills

The repository currently maintains these skills:

| Skill | Purpose |
|---|---|
| `decision-evaluation` | Compare bounded design options and recommend one with trade-offs |
| `design-decision-audit` | Review design or plan documents for missing decisions and rollout gaps |
| `design-orchestrator` | Route design-stage work across the specialized design skills |
| `design-readiness-check` | Decide whether a design is complete enough for implementation planning |
| `design-refinement` | Deepen an existing design tree until key branches are implementation-ready |
| `design-structure` | Turn a vague idea into an initial design tree and design skeleton |
| `dispatching-parallel-agents` | Split independent tasks across parallel agents |
| `executing-plans` | Execute a written implementation plan in batches with checkpoints |
| `finishing-a-development-branch` | Close out a finished branch with merge, PR, keep, or discard flows |
| `receiving-code-review` | Evaluate review feedback before applying changes |
| `requesting-code-review` | Request structured code review before moving on or merging |
| `subagent-driven-development` | Execute plan tasks with dedicated subagents and staged review |
| `systematic-debugging` | Find root cause before attempting fixes |
| `task-brief` | Normalize a raw request into a structured task brief before execution |
| `test-driven-development` | Enforce red-green-refactor for features and bug fixes |
| `using-git-worktrees` | Start work in an isolated git worktree |
| `verification-before-completion` | Verify claims with fresh evidence before saying work is done |
| `writing-clearly-and-concisely` | Improve documentation and other human-facing writing |
| `writing-plans` | Turn requirements into concrete implementation plans |

## Repository Layout

```text
loom/
├── skills/                  # Skill definitions
│   └── <skill-name>/
│       ├── SKILL.md         # Main skill document
│       └── ...              # Optional supporting files
├── docs/                    # Repo notes and execution plans
└── LICENSE
```

## Relationship to `obra/superpowers`

This repository is heavily influenced by `obra/superpowers`.

In practice, that means:

- some skills are copied directly or with minor edits
- some skills are adapted to fit local tool behavior and personal preferences
- naming, wording, and workflow details may differ from upstream

If you want the broader system, upstream documentation, or the original project direction, use [obra/superpowers](https://github.com/obra/superpowers) as the primary reference.

## How To Use

Install all skills globally via [skills.sh](https://skills.sh):

```bash
npx skills add freeacger/loom -y -g
```

This installs into `~/.claude/skills/` and `~/.agents/skills/` automatically.

Alternatively, pick individual skill folders from `skills/` and copy them into your local skill directory, adjusting wording or paths for your own environment.

## Why Keep A Separate Repo

Keeping these skills in a separate repo makes it easier to:

- track personal adjustments over time
- compare local changes against upstream
- reuse the same skills across machines
- document which workflows are actually in use

## License

This repository is licensed under the [MIT License](LICENSE).

Upstream skill content may have its own provenance. When reusing or redistributing skill text, check both this repository and the upstream source project.
