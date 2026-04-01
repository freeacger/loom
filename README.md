# loom

**Language:** English | [简体中文](README.zh-CN.md)

`loom` is a workflow skill repository for Codex, Claude-style agents, and similar local agent setups. It provides structured, composable skills that guide agents through design, planning, implementation, and review — from idea to production-ready code.

Early versions drew heavily from [obra/superpowers](https://github.com/obra/superpowers), but the project has since evolved its own design pipeline, parallel agent workflows, and skill development tooling.

## Scope

The repository covers the full engineering lifecycle:

- **Design** — structured workflow from vague idea to implementation-ready design
- **Planning** — turning requirements into concrete, batched implementation plans
- **Implementation** — test-driven development, parallel agent dispatch, plan execution
- **Review** — code review (giving and receiving), design document audits
- **Quality** — systematic debugging, completion verification, clear writing

## Skills

20 skills organized by phase:

### Design

| Skill | Purpose |
|---|---|
| `design-orchestrator` | Route design-stage work across the specialized design skills with one explicit next step |
| `design-tree-core` | Internal/shared governance core for required `design_state`, `design_target_type`, derivation, handoff, and anti-bloat rules |
| `design-structure` | Turn a vague idea into a `design_state`-first design tree with an explicit target type |
| `design-refinement` | Deepen an existing typed design tree until key branches meet the right completion standard |
| `decision-evaluation` | Compare bounded technical or non-technical design options and recommend one with trade-offs |
| `design-readiness-check` | Decide whether a typed design is complete enough for implementation planning |
| `design-decision-audit` | Review design or plan documents for missing decisions and rollout gaps |

### Planning

| Skill | Purpose |
|---|---|
| `task-brief` | Normalize a raw request into a structured task brief before execution |
| `writing-plans` | Turn requirements into concrete implementation plans |

### Implementation

| Skill | Purpose |
|---|---|
| `test-driven-development` | Enforce red-green-refactor for features and bug fixes |
| `executing-plans` | Execute a written implementation plan in batches with checkpoints |
| `subagent-driven-development` | Execute plan tasks with dedicated subagents and staged review |
| `dispatching-parallel-agents` | Split independent tasks across parallel agents |
| `using-git-worktrees` | Start work in an isolated git worktree |
| `systematic-debugging` | Find root cause before attempting fixes |

### Review & Quality

| Skill | Purpose |
|---|---|
| `requesting-code-review` | Request structured code review before moving on or merging |
| `receiving-code-review` | Evaluate review feedback before applying changes |
| `finishing-a-development-branch` | Close out a finished branch with merge, PR, keep, or discard flows |
| `verification-before-completion` | Verify claims with fresh evidence before saying work is done |
| `writing-clearly-and-concisely` | Improve documentation and other human-facing writing |

## Repository Layout

```text
loom/
├── skills/                  # Skill definitions
│   └── <skill-name>/
│       ├── SKILL.md         # Main skill document
│       ├── REFERENCE.md     # Shared or advanced reference material (optional)
│       ├── CHANGELOG.md     # User-visible changes (optional)
│       ├── agents/          # Parallel agent templates (optional)
│       └── evals/           # Evaluation test cases (optional)
├── docs/
│   ├── standards/           # Standards and style guides
│   ├── design-decisions/    # Design decision records
│   ├── design-tree/         # Design-stage analysis artifacts
│   ├── exec-plans/          # Execution plans (active/completed)
│   ├── reports/             # Time-bound reports and audits
│   └── workflows/           # Workflow documentation
├── scripts/                 # Utility scripts (hooks, generators)
├── mise/                    # Mise task definitions
├── tests/                   # Eval workspaces
├── AGENTS.md                # Agent rules
├── mise.toml                # Task runner configuration
└── LICENSE
```

## Quick Start

Install all skills globally via [skills.sh](https://skills.sh):

```bash
npx skills add freeacger/loom -y -g
```

This installs into `~/.claude/skills/` and `~/.agents/skills/` automatically.

Alternatively, pick individual skill folders from `skills/` and copy them into your local skill directory.

For repository tasks, install the pinned toolchain first:

```bash
mise install
```

This repository pins Python in `mise.toml`. Run Python-dependent commands inside the repo through the `mise` environment instead of relying on the system `python3`.

## Agent Skills Alignment

`loom` keeps `skills.sh` as its distribution path. [Agent Skills](https://agentskills.io/home) is treated as a compatibility target and reference specification layer, not as a replacement install source for this repository.

For the design-tree family, the primary shared state is still `design_state`, and `design_target_type` remains mandatory with allowed values `system`, `workflow`, `methodology`, and `framework`. In this repository, once `design-structure` completes the initial tree's main body, that tree should be persisted under `docs/design-tree/` as `draft` before the workflow continues, with `design-refinement` as the default next step. Promote the document to `ready-for-planning` only after `design-readiness-check` passes.

Phase 1 adds an optional validation command:

```bash
mise run check-skill-spec
```

This command validates every top-level directory under `skills/`.

Notes:

- `check-skill-spec` is a recommended check, not a push gate in phase 1
- if `skills-ref` is missing, the command fails fast and prints the reference doc
- phase 1 does not replace `skills.sh` or auto-install `agentskills`

## Acknowledgments

Some skills originated from or were inspired by [obra/superpowers](https://github.com/obra/superpowers). Those foundations are appreciated, though the skills here have been significantly reworked and extended.

## License

[MIT License](LICENSE).
