---
name: design-structure
description: Build the initial design structure from a vague or partially formed idea. Use when the task lacks a clear design tree, scope boundaries, core objects, key flows, or explicit decision points. Trigger when the user has an idea, feature request, or system goal that needs to be turned into a structured design skeleton before deeper refinement. Do not use when the design tree already exists and the main need is to deepen or validate it.
---

# Design Structure

## Overview

This skill turns a vague idea into an initial design tree through a two-phase workflow:

1. **Interactive confirmation** — progressively confirm `design_target_type`, problem, scope, and assumptions with the user
2. **Design tree generation** — produce the design tree based on confirmed inputs

Its primary output is `design_state`.
Saving a file is optional and only happens when the task explicitly requires persistence.

## When to Use

Use this skill when:

- the user has an idea but not a design
- the task lacks scope, boundaries, core objects, or key flows
- there is no clear design tree yet
- the current design conversation is still at the "what are we even designing?" stage
- an existing tree is missing `design_target_type` and needs that field to be made explicit

Do not use this skill when:

- a workable design tree already exists
- the main need is deeper decomposition of existing branches
- the main need is to compare options for one explicit decision node
- the main need is to decide whether the design is ready for planning
- the current tree only needs deeper refinement rather than a true derived tree
- the task is a report, note, summary, or documentation rewrite
- the task is a simple linear SOP with no real design-state boundary

## Language Strategy

Match the design file language to the user's instruction language.

Use this priority order:
1. An explicit output-language request from the user
2. The dominant natural language of the user's current instruction
3. The dominant natural language of the most recent user instructions in the same task
4. English if the signal is weak or ambiguous

Rules:
- Keep the chat response, interactive Q&A, and the design file in the same language
- Translate section headings into the chosen language
- Keep file paths, code identifiers, template placeholders (e.g., `{{...}}`), and literal config keys unchanged
- Do not mix languages unless the user explicitly asks for bilingual output
- Interactive Q&A in Phase 1 must also match the chosen language

Default heading examples:

If the output language is English:
- `Problem`
- `Scope`
- `Included` / `Excluded`
- `Assumptions`
- `Design Tree`
- `Open Branches`
- `Decision Nodes`
- `Decisions`
- `External Dependencies`

## Workflow

### Phase 1: Interactive Confirmation

Confirm the foundation before generating the design tree. Proceed in order:

1. **Design target type** — confirm one of `system`, `workflow`, `methodology`, `framework`
2. **Problem** — confirm the core problem and success metrics
3. **Scope** — confirm what is included and excluded
4. **Assumptions** — confirm implicit assumptions being made

After each confirmation, update the shared `design_state`. Do not repeat confirmed content in subsequent conversation.

Skip a section only if the user explicitly provides it upfront (e.g., "the problem is X and the scope is Y" — confirm both in one round).

### Phase 2: Design Tree Generation

Based on confirmed inputs, generate the design tree using the branch skeleton that matches `design_target_type`.

Use `../design-tree-core/REFERENCE.md` for shared type definitions and `REFERENCE.md` for preferred local branch skeletons.

If a branch is not relevant, say so explicitly instead of silently omitting it.

In conversation, show only:
- the tree diagram
- decision nodes that need user action
- open branch names
- next step recommendation

## Derived Tree Creation

This skill may also be used to create a derived tree when a parent tree has already identified a new stable problem domain.

Use the shared derivation and handoff rules in `../design-tree-core/REFERENCE.md` as the source of truth.

When creating a derived tree, do all of the following:

1. Name the parent tree and the derived tree explicitly.
2. State the reason for derivation.
3. Define what the derived tree owns.
4. Define what the derived tree does not own.
5. Record the minimum parent/child handoff:
   - branch being extracted
   - inherited constraints
   - unresolved questions
   - expected output
   - return conditions

Do not copy the parent tree into the derived tree.
Do not use derivation as a way to dump overflow detail.

## Interactive Q&A

### Intent-Driven Strategy

Use whatever interactive question tool is available in the current environment. Do not hardcode tool names — describe the interaction intent and constraints; the model selects the right tool based on its environment.

**Constraints (cross-CLI compatible):**
- 1–3 questions per prompt
- ≤ 4 options per question
- Structured text (question + optional choices)

**Fallback:** If no dedicated question tool is available, use natural language prompts (see format templates below).

### Question Types and Formats

#### Confirmation — state understanding, ask to verify

```
## Problem

Core problem: Build an internal API gateway for unified routing, authentication, and rate limiting.
Success metrics: P99 latency < 50ms, availability > 99.9%

↑ Is this correct? Anything to amend?
```

#### Scope — checklist with include/exclude markers

```
## Scope

My assessment:

Included ✓
- Request routing
- Authentication and authorization
- Rate limiting
- Request logging

Excluded ✗
- Service discovery
- Load balancing

↑ Any adjustments?
```

#### Decision — table with star ratings, best option first, max 4 options

```
## Pending Decision: Auth Mode

| Option | Rating | Pros | Cons |
|--------|--------|------|------|
| JWT (stateless) | ★★★ | Scales horizontally, no server state | Revocation is complex, token size |
| Session (stateful) | ★★ | Instant revocation, mature pattern | Requires shared storage, limited scaling |
| API Key | ★ | Simple to implement | Low security, not suitable for user-level auth |

↑ Which one? Or a different idea?
```

#### Supplement — direct question with relaxed prompt

```
## Supplementary Info

Expected daily request volume?

↑ Please fill in (a rough range is fine if uncertain)
```

**Rules for all types:**
- One question type per message
- End every question with `↑` marker to signal "your turn"
- After user confirms, do not repeat the confirmed content (it is already in the file)

## Persistence

Persistence is optional.

Use `REFERENCE.md` for the local save contract.
Do not assume file output unless the task explicitly requires it.

## Design Tree Requirement

Create an initial design tree that:

- makes `design_target_type` explicit
- uses the correct branch skeleton for that target type
- identifies open branches
- identifies explicit decision nodes
- captures assumptions rather than relying on them silently
- keeps the output as `design_state` first, artifact second

If a branch is not relevant, say so explicitly instead of silently omitting it.

## Core Responsibilities

Your responsibilities are:

1. Clarify the real goal of the design through interactive confirmation.
2. Make `design_target_type` explicit before building the tree.
3. Capture scope, non-goals, and constraints.
4. Build an initial design tree with first-level and, where useful, second-level branches.
5. Identify open branches that still need refinement.
6. Identify explicit decision nodes that should later go to `decision-evaluation`.
7. Record assumptions instead of silently relying on them.
8. Flag nodes that depend on unverified external tools, APIs, libraries, or services. Perform a lightweight feasibility check (web search or doc lookup) at the time of flagging. If the dependency is clearly infeasible, mark `✗` immediately; if confirmed feasible with open questions, mark `[RESEARCH]` with initial findings; if fully confirmed, mark `✓`.
9. Persist the design only when the task explicitly requires it.
10. If acting on a parent-tree handoff, create a derived tree with explicit parent/child boundaries rather than repeating the parent tree inline.

## Expected Outputs

### Required Output

Produce or update a `design_state` that includes:

- `design_target_type`
- `problem`
- `scope`
- `design_tree`
- `open_branches`
- `decision_nodes`
- `external_dependencies`
- `status`

If the tree being created is a derived tree, also include:

- parent/child ownership
- derivation reason
- parent/child handoff

### Conversation Output (concise)

- Phase 1: one question at a time (see Question Types)
- Phase 2: tree diagram + decision node summaries + open branch names + next step

You are not expected to fully close every branch.

## Diagram Conventions

Render the design tree as a character tree diagram inside a code block (no language tag).

**Format:**

```
design_tree
├── 1. Problem definition
│   ├── 1.1 Core problem
│   └── 1.2 Success metrics ✓
├── 2. Core flows [OPEN]
│   ├── 2.1 Happy path
│   └── 2.2 Error path
├── 3. Interfaces and data
│   └── 3.1 API contract [DRAFT]
├── 4. External integrations
│   └── 4.1 Payment SDK [RESEARCH]
└── 5. Decision points
    └── 5.1 Storage choice [DECISION]
```

**Character rules:**

- Branches: `├──` (middle), `└──` (last)
- Continuation: `│   ` (non-last parent), `    ` (last parent, 4 spaces)
- Numbering: `1.`, `1.1` — required at first two levels
- Max width: 78 characters

**Status markers:**

| Marker | Meaning |
|--------|---------|
| `[OPEN]` | Unresolved, needs refinement or decision |
| `[DECISION]` | Decision node with multiple real options |
| `[DRAFT]` | Tentative, may change |
| `[RESEARCH]` | Depends on an external tool, API, library, or service that has passed initial feasibility check but needs deeper validation |
| `✓` | Complete / verified |
| `✗` | Rejected / out of scope |

**When to render:** Always include a tree diagram when the design tree has 3+ branches. Omit only if the design is trivially small (1-2 branches).

## Entry and Exit Criteria

Enter when:

- there is no meaningful design tree yet
- the request is still mostly unstructured

Exit when:

- the design tree exists with enough structure for follow-on work
- the main remaining work is branch refinement or explicit decision analysis

## Handoff Rules

- Hand off to `design-refinement` when the tree exists but branches are still too shallow.
- Hand off to `decision-evaluation` when there is a concrete decision node with real options.
- Hand back to `design-orchestrator` if the design state changed enough that routing should be re-evaluated.
- Do not continue past Phase 1 if `design_target_type` is still unresolved.
- Do not force the conversation into option comparison before the design tree is formed.
- Do not default to saving a file unless the task explicitly requires persistence.
