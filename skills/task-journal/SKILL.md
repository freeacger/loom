---
name: task-journal
description: "Append-only task record convention for Loom. Use when reading or writing per-task records under `.agents/tasks/<task-id>/`, when another skill needs to log a lifecycle milestone (saved, decision, readiness, blocker, done), when the user asks about an existing task's status or progress, or when checking task records for drift via the linter. Do NOT trigger for creating new tasks (that is `task-brief`'s job), for general docs/planning unrelated to a task directory, or for historical questions about the retired `task-state-management` system."
---

# Task Journal

## Overview

This skill is a **convention reference**, not a tool. It defines how every task in this repository records its life as an append-only journal of plain markdown. There is no slash command, no CLI, and no central writer process — every skill that touches a task appends entries directly to the same `journal.md` file.

The job of this skill is to give other skills (and humans reading the file) a stable contract about:

- where task records live,
- what an entry looks like,
- which keys are reserved,
- what the linter enforces,
- what completion means,
- and what signals justify upgrading away from this design.

Truth lives in the file system + git + memory. The convention exists to keep that truth readable.

---

## When to Use

**Use this skill when:**

- a skill is at a lifecycle milestone and needs to append to `journal.md` (see Tier table)
- the user asks about an existing task's status, progress, or recent activity
- the user wants to check task records for drift (run the linter)
- you are about to mark a task done (write a `done:` entry; do not move the directory)

**Do NOT use this skill when:**

- the user wants to create a new task — that is `task-brief`'s job
- the user is asking a historical question about `task-state-management` (the retired state machine)
- the request is about general docs, design, or planning that has no task directory
- the request is a one-off action that does not warrant a task at all (e.g., "rename this variable")

---

## Data Layout

```
<repo>/.agents/tasks/
├── .current                       # single-line pointer: <task-id>
└── <task-id>/
    ├── brief.md                   # immutable after first journal entry
    ├── journal.md                 # append-only log
    └── artifacts/                 # private to this task; long bodies go here
```

- **Location**: `<repo>/.agents/tasks/`. Flat — no `active/` or `completed/` partitions.
- **Git tracking**: default off. `.gitignore` includes `.agents/tasks/`. The user may `git add` an individual file deliberately.
- **`.current` pointer**: optional single-file pointer with the active task id (no newline required, trailing newlines tolerated). Written by `task-brief` on creation. Other skills may read it as a fallback when no task id was passed explicitly.

### Task ID Format

```
YYYY-MM-DD-<slug>-<rand>
```

- `YYYY-MM-DD`: ISO date of creation.
- `<slug>`: ASCII kebab-case, ≤ 6 words, ≤ 60 characters. Proposed by `task-brief` from the user goal; the user may override.
- `<rand>`: 2 lowercase hex characters (`00`–`ff`), generated via `random.randint(0, 255)` then formatted as `%02x`. Re-roll on directory collision. Never reused after deletion (collisions are rare and easy to detect).

Example: `2026-04-26-task-journal-redesign-a3`.

---

## Brief Immutability

`brief.md` is **frozen the moment the first journal entry is written.**

- Before the first entry: the brief may be overwritten freely (the "uncommitted brief" window).
- After the first entry: do not edit `brief.md`. Record any goal drift, scope change, or refinement as a new journal entry, e.g.:
  ```markdown
  ## 2026-04-26T11:20:00+08:00 — task-brief
  refined: goal narrowed to logging-only path
  scope was widening to cover dashboards; user confirmed pulling that out
  ```

This rule exists so the brief stays a stable reference point. The journal is where evolution lives.

---

## Journal Entry Format

Each entry is a level-2 markdown heading followed by one or more `key: value` lines and an optional short body.

```markdown
## <ISO8601-timestamp> — <skill-name>
<key>: <value>
[<additional key>: <value>]
[free-form markdown body, ≤ 15 lines]
```

Rules:

- **Heading** must start with `## `, then an ISO 8601 timestamp (date+time, with timezone or `Z`), then ` — ` (em dash, space-padded), then the skill name.
- **At least one** `key: value` line is required immediately under the heading.
- Keys are lowercase ASCII, may contain hyphens and underscores. Values are free text on the same line.
- **Body** is optional, ≤ 15 lines. If you need more, write to `artifacts/` and reference it in the body.
- Entries are appended only. Never rewrite existing entries.
- Entries should be separated by a blank line for readability (the linter does not require it).

### Reserved Core Keys

These five keys are **reserved and linted**. Use them when their meaning fits — do not invent synonyms.

| Key | Meaning | Typical writer |
|---|---|---|
| `saved` | A persistent artifact was written or updated. Value names what was saved. | `design-structure`, `writing-plans`, `executing-plans` |
| `decision` | A bounded design decision was made. Value names the decision; body may carry rationale. | `decision-evaluation`, `design-decision-audit` |
| `readiness` | Readiness status of the design or plan. Value is `ready` or `not-ready`; body explains gaps. | `design-readiness-check` |
| `blocker` | A blocker was raised. Value is a short label; body describes what is blocked and why. | any skill |
| `done` | The task reached its completion state. Value names the result (`merged`, `shipped`, `cancelled`, …). | `finishing-a-development-branch`, user-initiated close |

Other keys (`refined`, `note`, `handoff`, `link`, …) are free-form. The linter does not check them.

---

## Completion Semantics

Only **code tasks** have a real notion of completion (Option 2 from the design):

- **Primary path**: `finishing-a-development-branch` appends `done: <result>` after a successful merge/ship.
- **Fallback**: the user states the task is done; the next skill (often `task-brief`) appends the `done:` entry.

**Non-code tasks** never get a `done:` entry. Activity is judged by the timestamp of the last entry; the linter may flag long-stale tasks as a soft hint.

**Do not migrate the directory** when a task is done. The task stays under `.agents/tasks/<task-id>/`. The presence of a `done:` entry is the marker.

**Reopen** is just appending a new entry after a `done:` entry. The linter detects this pattern and emits a warning so the human notices it.

---

## Skill Tiers

This is the contract for which skills should append to journal and which should not. Cross-reference each skill's own SKILL.md "Journal Integration" section for exact entry shape.

| Tier | Skills | Behavior |
|---|---|---|
| **A — creates tasks** | `task-brief` (only on user confirmation) | Sole entry point that creates `.agents/tasks/<id>/`. Writes `brief.md` and the first journal entry (`task_created: …`). |
| **B — appends on milestones** | `design-structure`, `design-refinement`, `design-decision-audit`, `decision-evaluation`, `design-readiness-check`, `writing-plans`, `executing-plans`, `subagent-driven-development`, `verification-before-completion`, `finishing-a-development-branch` | Append entries at meaningful lifecycle moments (saved, decision, readiness, done). |
| **C — appends conditionally** | `bug-investigation`, `systematic-debugging`, `requesting-code-review` | Append only when a task id is in scope. |
| **D — never appends** | `design-orchestrator`, `dispatching-parallel-agents`, `using-git-worktrees`, `test-driven-development`, `writing-clearly-and-concisely`, `receiving-code-review` | Methodology / routing / meta layer. They do not own task state. |

---

## Task ID Propagation Between Skills

Pick the first that applies:

1. **Explicit parameter** — the caller (user or upstream skill) names the task id directly. **Preferred.**
2. **`.current` pointer** — read `<repo>/.agents/tasks/.current`; if it names an existing directory, treat that as the active task.
3. **Otherwise** — do not guess. Ask the user, or skip the journal append for this turn.

Do **not** introduce ambient state, environment variables, daemons, or file locks for this purpose.

---

## Helper Script: `journal.py`

`scripts/journal.py` is a thin Python helper for skills that prefer a function call over hand-writing markdown. It is optional — appending markdown directly is equally valid.

```bash
python3 ${SKILL_DIR}/scripts/journal.py append \
  --tasks-dir .agents/tasks \
  --task-id <task-id> \
  --skill <skill-name> \
  --kv saved=design-tree.md \
  --body "expanded core branches"
```

```bash
python3 ${SKILL_DIR}/scripts/journal.py read \
  --tasks-dir .agents/tasks \
  --task-id <task-id> \
  [--last N]
```

`SKILL_DIR` resolves to wherever this skill is installed (`~/.claude/skills/task-journal` or the repo `skills/task-journal`). Both paths work.

The helper is stdlib-only, ~100 lines, and never blocks. It does not validate keys (that is the linter's job).

---

## Linter: `lint_tasks.py`

`scripts/lint_tasks.py` walks `.agents/tasks/` and reports drift. Severity rules:

- **error** — corrupt heading, missing `key: value` line, malformed reserved-key value, unparseable timestamp, missing `brief.md`. Returns exit code 1.
- **warn** — body > 15 lines, entry written after a `done:` entry without a clear reopen marker, task with no entry for > 30 days, unknown skill name (heuristic only). Returns exit code 0 if no errors.

The linter never blocks LLM real-time writes. Whether the loom repo's pre-push hook calls it is a separate decision and not part of this contract.

```bash
python3 ${SKILL_DIR}/scripts/lint_tasks.py --tasks-dir .agents/tasks
```

Flags:

- `--tasks-dir <path>`: required; path to the tasks root.
- `--strict`: treat warnings as errors (exit 1 on any warning).
- `--task-id <id>`: lint a single task instead of the whole tree.

---

## Anti-Patterns

These are the failure modes the design explicitly rejects. Avoid them.

- **Do not edit `brief.md` after the first journal entry.** Record changes as a `refined:` entry.
- **Do not move task directories on completion.** A `done:` entry is the marker.
- **Do not use journal as RPC between skills.** The journal is write-many, read-rarely. If skill B needs a value from skill A, pass it as a parameter or read the underlying artifact (plan file, design tree, etc.), not by parsing journal entries.
- **Do not invent synonyms for reserved keys.** If `saved`, `decision`, `readiness`, `blocker`, `done` fit, use them.
- **Do not embed long bodies in the journal.** > 15 lines goes to `artifacts/`.
- **Do not rewrite or delete past entries.** Append a correction entry instead.
- **Do not introduce ambient state** (env vars, daemons, locks). Pass the task id explicitly or use `.current`.

---

## Upgrade Signals

This design intentionally stays small. Each of the failure scenarios below has a documented signal and a documented upgrade direction. See the ADR `docs/design-decisions/2026-04-26-task-journal-replaces-task-state-management.md` for the canonical list.

| Failure scenario | Signal | Upgrade direction |
|---|---|---|
| Concurrent writers from multiple agents | interleaved or lost entries observed | file lock or single-writer protocol |
| Frequent cross-task index queries | > 50 tasks and weekly "which tasks reference X?" needs | index file or SQLite |
| Single task with very long journal | > 200 lines or reading feels slow | rolling archive (`journal-2026-Q1.md`) |
| Frequent status grep queries | same grep ≥ 5×/week | structured summary command |
| Real second-person collaboration | a second human starts using it | switch to git-tracked + add an ownership field |
| Actual journal corruption | ≥ 1 corruption incident in practice | backup / checkpoint mechanism |
| Stable automated invocation needs | recurring CI/hook integration demands | thin CLI, one command at a time |

**Meta-gate.** Any PR that proposes "add the state machine back" must:

1. point to one of the seven scenarios above,
2. cite the number of times the signal has fired, and
3. limit the upgrade to a single failure scenario.

Otherwise the PR is rejected. This rule exists because the previous design (`task-state-management`) was built without observed failures.

---

## Examples

### Tier B append (design-structure has just saved a design tree)

```markdown
## 2026-04-26T10:42:11+08:00 — design-structure
saved: docs/design-tree/2026-04-26-task-journal-redesign.md
expanded the core branches; pending refinement on linter contract
```

### Tier C conditional append (systematic-debugging on a tracked task)

```markdown
## 2026-04-26T14:05:00+08:00 — systematic-debugging
note: reproduced the lost-entry case under concurrent appends
linked artifact: artifacts/concurrent-append-trace.md
```

### Reserved decision key

```markdown
## 2026-04-26T15:30:00+08:00 — decision-evaluation
decision: stdlib-only helper, no third-party deps
considered ruamel.yaml for richer parsing; rejected for footprint and YAGNI
```

### Done marker (does not move directory)

```markdown
## 2026-04-26T18:12:00+08:00 — finishing-a-development-branch
done: merged
PR #142 merged into main; cleanup branch deleted
```
