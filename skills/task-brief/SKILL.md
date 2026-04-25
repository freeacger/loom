---
name: task-brief
description: "Use this skill to turn a raw user request into a structured, model-agnostic task brief before execution, and — when the brief survives confirmation — to be the sole entry point that creates a task directory at `.agents/tasks/<task-id>/`. Invoke whenever the request is complex, multi-step, cross-domain, ambiguous, or will be handed off to another model or agent. Also trigger when the user says things like 'help me figure out what I need', 'I'm not sure how to ask this', 'I want to do X but I don't know where to start', 'take this and make it clearer', or when the task mixes multiple goals or domains. Do NOT trigger for simple one-line requests with clear intent (e.g., 'fix the typo on line 42', 'rename this variable')."
---

# Task Brief

## Overview

Turn a raw natural-language request into a structured task brief that another executor can use without reading the original message.

**This skill is a task specification normalizer.** Its job is to surface the real goal, capture the completion standard, and make critical constraints explicit. It does not do design-stage routing, task decomposition, implementation planning, or execution.

The value is straightforward: a good brief reduces misunderstanding, prevents wasted work on the wrong problem, and makes handoff cleaner for another model, agent, or human.

`task-brief` is also the **sole creation entry point** for `.agents/tasks/<task-id>/`. Once a brief is confirmed and the task is non-trivial enough to warrant persistence, this skill creates the task directory and writes the first journal entry. See "Creating a Task Directory" below.

---

## Core Responsibilities

`task-brief` should only:

1. Restate the real user goal, not just the surface wording.
2. Define the success criteria in observable terms.
3. Capture the deliverables the task is expected to produce.
4. Surface constraints that materially change execution.
5. Record short assumptions when the user has left gaps.
6. Ask at most one clarifying question when one critical unknown remains.
7. Make one lightweight judgment about whether the task needs design work.
8. After user confirmation, when persistence is warranted, create `.agents/tasks/<task-id>/` with a frozen `brief.md` and the first `task_created` journal entry.

`task-brief` should not:

- route the task between design skills
- decompose the task into sub-tasks
- draw dependency diagrams
- write implementation steps
- propose migration sequencing
- default to codebase investigation just to sharpen the brief

If the real task is root-cause investigation, use `systematic-debugging` instead of turning `task-brief` into a debugging workflow.

---

## When to Use

**Trigger on:**

- requests with multiple sub-goals or unclear priority order
- requests that span domains (for example data + UI + API)
- requests where the stated problem may not be the real problem
- requests that will likely be handed off to another executor
- requests where missing context would force high-impact assumptions
- requests where the user explicitly asks for help clarifying the task itself

**Do NOT trigger on:**

- single, unambiguous actions ("delete this function", "run the tests")
- requests where the intent is already clear and the execution path is obvious
- follow-up messages that only refine an existing task in progress
- requests that explicitly ask for a design tree or design-stage decomposition

If in doubt, ask this question: can an executor start correctly from the brief alone? If yes, the brief is probably sufficient.

---

## Complexity Tiers

Classify the request into one of these tiers before writing the brief.

| Tier | Signal | Response |
|------|--------|----------|
| **Direct** | Single goal, clear scope, no critical missing information | Write a concise brief. Usually no design stage needed. |
| **Clarify** | One critical unknown remains, or the stated goal may be inaccurate | Write the brief first, ask exactly one clarifying question, and keep the rest minimal. |
| **Structured** | Multiple goals, cross-domain context, or a handoff-friendly brief is needed | Write the full brief, but stop at the brief. Do not decompose or route inside this skill. |

**Clarify** has three common sub-cases:

- *Missing parameter*: you know the goal, but one detail is missing.
- *Ambiguous intent*: the goal could reasonably mean two substantially different things.
- *Inaccurate goal*: the user stated a solution, symptom, or oddly scoped target instead of the underlying goal.

For inaccurate goals, detect these signals:

1. **Solution-as-goal**: the user names a technique ("add Redis caching") rather than the problem it solves.
2. **Symptom-as-goal**: the user names an error state ("fix timeout errors") rather than the desired outcome.
3. **Scope anomaly**: the stated scope looks unnaturally narrow or broad for the problem.

When one of those signals appears:

- rewrite the `User Goal` around the best-guess underlying intent
- mark that guess as an assumption
- ask one clarifying question that confirms the real target

Do not default to codebase search just to sharpen the question. If the task is actually debugging, route to `systematic-debugging`.

---

## Output: Task Brief

The task brief uses a **two-tier visual structure** when rendered to the user. The protocol field names (`User Goal`, `Success Criteria`, `Clarifying Question`, `Deliverables`, `Constraints`, `Assumptions`) are stable anchors — keep their wording exactly. Visual layout is render-only.

### Render Rules

- **No outer code block.** Render the brief as plain markdown so headings, bold, and quote blocks display naturally.
- **Upper tier (the TL;DR)** — what the executor needs to grasp in five seconds:
  - `User Goal` rendered as a quote block with the verb-led sentence(s) bolded:
    > **State the real intent in 1-2 sentences. Start with a verb.**
  - `Deliverables` as a short bulleted list.
  - `Clarifying Question` (only when one is needed) prefixed with `❓` for visual salience.
- **Divider** (`---`) separates the upper tier from the lower tier.
- **Lower tier (the rest)** — context an executor consults as they work:
  - `Success Criteria` as bulleted observable checks.
  - `Constraints` as a flat bulleted list. Do not force `Scope` / `Format` / `Risk` / `Other` sub-categories; only break out a sub-label when the constraint is heterogeneous enough to need it.
  - `Assumptions` as a short bulleted list when the user left gaps.
  - **Recommended next** as one natural-language sentence stating whether to proceed directly, enter the design stage (with a brief reason), or pause for clarification.
- **Skip empty fields entirely.** Do not render `Assumptions:` with "(none)" — omit the heading.
- **Do not render `Task Type` by default.** It exists in the protocol as an anchor but adds little to the user view; surface it only when the executor genuinely needs to disambiguate.

### Bilingual rendering

Keep the field names canonical. In Chinese responses, render bilingual labels with Chinese first and the English literal in parentheses, e.g., `**完成标准 (Success Criteria):**`. In English responses, render English only. Do not hardcode bilingual headings into examples below — they are reference templates, not the rendered output.

### Reference template (canonical anchors)

```
> **<User Goal — verb-led, 1–2 sentences>**

**Deliverables:**
- <concrete artifact 1>
- <concrete artifact 2>

**❓ Clarifying Question:** <one question, only when one critical unknown remains>

---

**Success Criteria:**
- <observable signal 1>
- <observable signal 2>

**Constraints:**
- <constraint that materially changes execution>

**Assumptions:**
- <inference filling a user-left gap>

**Recommended next:** <one sentence — proceed directly | enter design stage (reason) | pause for clarification>
```

---

## Compression Rules

These rules govern how to convert a raw message into the brief.

**Keep:**

- the underlying goal
- constraints that eliminate whole categories of solutions
- domain context that changes the execution path

**Remove:**

- filler phrases
- repeated restatements of the same goal
- reasoning the executor does not need to act

**Convert (vague -> actionable):**

- "make it better" -> identify the dimension: performance, readability, UX, security
- "something's wrong" -> specify observed vs. expected behavior
- "soon" / "quickly" -> ask for a concrete deadline only if it affects approach
- "the usual format" -> infer from context or mark it as an assumption
- "add Redis to the API" -> ask what problem the user is trying to solve

**When intent is ambiguous:**

- if two substantially different interpretations are plausible, surface both explicitly
- ask one question that forces the choice
- defer deliverables that depend on that choice rather than guessing

**Don't over-correct:**

- preserve the user's framing when it carries real intent
- do not invent goals or constraints the user did not imply
- if uncertain whether a detail matters, keep it and mark it as an assumption

---

## Creating a Task Directory

After the brief stabilizes, decide whether to create a task directory at `.agents/tasks/<task-id>/`. This is the **sole creation entry point** for the task tree — other skills append journal entries but do not create the directory.

### When to propose creation

Propose creation when **any** of the following holds:

- the task is multi-step (more than one major action)
- the task will produce a persistent artifact (design tree, plan, code branch, report)
- the brief recommends entering the design stage
- the user signals follow-up will continue across sessions

Do **not** propose creation when:

- the task is a single trivial action (rename, typo fix, run a known command)
- the user explicitly says they don't want a task record
- the work is already attached to an existing task — append to that task's journal instead

### Confirmation gate

After writing the brief, ask the user explicitly: "Should I create a task record at `.agents/tasks/<task-id>/`? Suggested slug: `<slug>`." Do not create silently.

### Slug strategy (Hybrid)

- Propose a slug derived from the `User Goal`: ASCII kebab-case, ≤ 6 words, ≤ 60 characters.
- If the user supplies their own slug, use the user's slug verbatim.
- The user's slug always wins over the proposal — do not auto-edit it for "kebab-case correctness" if it's already legible.

### Task ID format

`YYYY-MM-DD-<slug>-<rand>` where `<rand>` is two lowercase hex characters from `random.randint(0, 255)`. Re-roll on directory collision. Never reuse a deleted id's rand.

### Atomic creation steps

When the user confirms:

1. Create directory `.agents/tasks/<task-id>/` plus `artifacts/` subdirectory.
2. Write `brief.md` with the brief content (the canonical anchored fields, no rendering decoration).
3. Write the first journal entry to `journal.md`:
   ```
   ## <ISO8601> — task-brief
   task_created: brief.md
   slug derived from "<short reason>"
   ```
4. Update `.agents/tasks/.current` to point at the new task id.

These four steps are a single conceptual unit — if any fails, undo the partial state before reporting back.

After creation, `brief.md` is **frozen**. Goal drift goes into journal entries with a `refined:` key. Do not edit `brief.md` again.

See `task-journal` for the convention these entries follow.

---

## Examples

### Example 1 — Direct

**User input:**
> "Extract all TODO comments from the codebase and output them as a markdown list grouped by file."

**Rendered brief:**

> **Collect every TODO comment across the codebase and produce a readable markdown list grouped by file.**

**Deliverables:**
- Markdown list of TODO comments grouped by file, each entry with file path and line number

---

**Success Criteria:**
- Output groups TODO entries by file
- Each entry includes a line number
- Output covers the entire repository

**Constraints:**
- Output format: markdown
- Scope: entire repository

**Assumptions:**
- "TODO" matches the literal strings `TODO` or `TODO:`

**Recommended next:** Proceed directly with execution.

### Example 2 — Clarify

**User input:**
> "I need to migrate our auth system to JWT. Can you help me figure out what needs to change?"

**Rendered brief:**

> **Identify what needs to change to migrate the current authentication system to JWT-based auth, before scoping the migration itself.**

**Deliverables:**
- Auth migration change brief covering affected components and migration target

**❓ Clarifying Question:** What does the current auth system use now — session cookies, a third-party identity provider, API keys, or something else?

---

**Success Criteria:**
- Affected auth components are identified
- Migration target is concrete enough to begin design or impact analysis

**Constraints:**
- Scope is limited to authentication-related behavior
- Do not assume a stateless-token migration path if the current system is session-based or third-party managed

**Assumptions:**
- "JWT" means standard stateless tokens rather than JWE

**Recommended next:** Enter design stage. Reason: migration target depends on the current auth model and cross-cuts session handling and identity providers.

### Example 3 — Structured

**User input:**
> "Build me a dashboard that shows real-time sales data pulled from our Postgres DB, with a chart for daily revenue and a table for top 10 products. It should update every 30 seconds and be shareable via a link."

**Rendered brief:**

> **Build a shareable dashboard that displays live sales data from Postgres, including a daily revenue chart and a top-products table that refresh every 30 seconds.**

**Deliverables:**
- Live sales dashboard with daily revenue chart and top-10 products table
- Shareable URL for accessing the dashboard

**❓ Clarifying Question:** Does "shareable via a link" mean publicly accessible without auth, or accessible only to authenticated users?

---

**Success Criteria:**
- Dashboard shows daily revenue and top-10 products from live data
- Dashboard refreshes every 30 seconds
- Dashboard is reachable through a stable URL

**Constraints:**
- Browser-based UI only
- No database writes from the dashboard
- No credential exposure in client-side code

**Assumptions:**
- Postgres already exposes the fields needed for revenue aggregation and top-product ranking

**Recommended next:** Enter design stage. Reason: cross-domain scope (data layer, refresh strategy, access model) and unresolved access-control question.

### Example 4 — Ambiguous Intent

**User input:**
> "Our API docs are a mess - can you help fix them?"

**Rendered brief:**

> **Improve the API documentation, but disambiguate between two materially different outcomes before any work begins: rewriting the documentation content vs. changing the documentation tooling or site structure.**

**Deliverables:**
- Deferred until the direction is confirmed

**❓ Clarifying Question:** Is the real problem the documentation content, or the tooling and presentation layer?

---

**Success Criteria:**
- Intended direction is confirmed before work starts

**Constraints:**
- Scope is limited to public API documentation
- External developer experience may be affected by public doc changes

**Assumptions:**
- "API docs" refers to developer-facing HTTP API documentation rather than internal notes

**Recommended next:** Pause for clarification. Reason: the two interpretations would lead to very different scopes and skill paths.

### Example 5 — Inaccurate Goal

**User input:**
> "Add Redis caching to our API endpoints."

**Rendered brief:**

> **Reduce API latency or backend load. Redis caching is the user's proposed technique, but the underlying goal is performance — the actual bottleneck has not been confirmed.**

**Deliverables:**
- Performance-problem brief that names the actual bottleneck

**❓ Clarifying Question:** What performance problem are you seeing right now — slow endpoints, high database load, or something else?

---

**Success Criteria:**
- Real performance problem is identified
- Task target is reframed around the actual bottleneck rather than a preselected technique

**Constraints:**
- Scope is limited to API behavior
- Do not assume caching is appropriate before the bottleneck is known

**Assumptions:**
- The user wants better performance but has not confirmed where the bottleneck is

**Recommended next:** Pause for clarification. Reason: solution-as-goal — committing to Redis without the bottleneck is high-risk.

---

## Acceptance Criteria

A good task brief passes these checks:

1. **Standalone**: an executor can start correctly from the brief alone, or knows the one question that must be answered first.
2. **Intent-preserving**: the `User Goal` captures what the user actually wants, not just what they said.
3. **Constraint-complete**: missing any included constraint would materially risk wrong-path execution.
4. **Non-padded**: the brief stays short when the task is simple. Empty fields are omitted entirely.
5. **Actionable deliverables**: each deliverable is a concrete artifact or outcome.
6. **Goal-honest**: the brief reframes solution-as-goal and symptom-as-goal requests honestly.
7. **Scope-clean**: the brief does not drift into design routing, decomposition, or implementation planning.
8. **Single-question discipline**: when clarification is needed, the brief asks one focused question, not a questionnaire.
9. **Creation discipline**: a task directory is created only after the user confirms, with a slug they accepted or supplied.

A brief is **not useful** if:

- it restates the user's message in different words without adding clarity
- it introduces goals or constraints the user did not imply
- it turns a simple request into a long clarification session
- it drifts into design trees, sub-task decomposition, or implementation plans
- it creates a task directory silently or against the user's wishes
