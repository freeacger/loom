---
name: design-refinement
description: Refine an existing design tree until key branches become implementation-ready. Use when the high-level structure already exists but important branches remain vague, shallow, or unresolved. Trigger when the user needs deeper decomposition, edge-case coverage, failure-path clarification, interface detail, or validation criteria for a partially designed system. Do not use to create the initial design skeleton from scratch or to compare options for a single explicit decision node.
---

# Design Refinement

## Overview

This skill deepens an existing design tree.

Its job is to take major branches that are still vague and push them toward implementable leaf nodes. It should make the design more specific, more bounded, and harder to misread during implementation.

## When to Use

Use this skill when:

- the design tree already exists
- the design is still too high-level to guide implementation planning
- important branches lack interfaces, boundaries, failure behavior, or validation detail
- the user asks to make the design more concrete, more detailed, or more complete

Do not use this skill when:

- there is no design tree yet
- the main problem is a single bounded decision with multiple options
- the main question is whether the current design is ready for planning
- `design_target_type` is missing from the current design state
- the task is really a report, note, or SOP draft

## Required Input

Do not continue refinement without an explicit `design_target_type`.

If the design state is missing that field:

- stop refinement
- do not silently assume `system`
- hand back to `design-orchestrator` or `design-structure` so the type can be set explicitly

## Leaf Node Standard

Use the target-type-specific completion standard from `../design-tree-core/REFERENCE.md`.

In summary:

- `system`: responsibility, non-responsibility, adjacent interaction, failure, validation
- `workflow`: stage goal, input/output, owner, rollback, quality gate
- `methodology`: applicability, non-applicability, decision rules, handoff form, exit condition
- `framework`: dimension or module, non-ownership, routing rule, handoff form, completion rule

If those answers are still missing for the current target type, the branch is not done.

## Refinement vs Derivation Boundary

Refinement should continue only while a branch remains part of the current tree's original core question.

Use the shared derivation rules in `../design-tree-core/REFERENCE.md` as the source of truth.

Stop refining inline when a branch begins to show all of the following:

- it is answering a second distinct core question
- it requires repeated local routing decisions of its own
- it needs its own scope boundary
- it needs its own completion check
- continuing inline refinement would make the parent tree harder to route

When those conditions appear:

- do not keep expanding the branch inline
- surface the branch as a candidate for derivation
- hand back to `design-orchestrator` or `design-structure` for explicit derived-tree creation

## Core Responsibilities

Your responsibilities are:

1. Walk unresolved design branches one at a time.
2. Prioritize high-risk, high-dependency, or high-ambiguity branches first.
3. Expand branches into concrete sub-branches and leaf nodes using the current `design_target_type`.
4. Surface hidden assumptions and edge cases.
5. Add failure-path and validation detail where missing.
6. Explicitly mark newly discovered decision nodes instead of pretending they are settled.
7. Resolve `[RESEARCH]` nodes by performing deep validation of external dependencies (API compatibility, version constraints, integration patterns, error handling, rate limits). Replace `[RESEARCH]` with `✓` when validated, `✗` when rejected, or `[DECISION]` if alternatives need evaluation. If validation cannot be completed in the current context, document what was learned and retain `[RESEARCH]`.

## Expected Outputs

Produce or update a `design_state` that includes:

- `design_target_type`
- refined `design_tree` branches
- updated `open_branches`
- `confirmed_assumptions`
- `risks`
- `validation`
- updated `external_dependencies` if any [RESEARCH] nodes were resolved
- new `decision_nodes` if discovered

## Diagram Conventions

Use character diagrams inside code blocks (no language tag) to visualize component interactions, failure paths, and state transitions.

### Sequence Diagrams

Use when a leaf node describes "how it interacts with adjacent parts" and involves 3+ components.

```
Client          API Server      Auth Service     DB
  │                │                │             │
  │── request ────→│                │             │
  │                │── verify ────→│             │
  │                │←── ok ────────│             │
  │                │── insert ─────────────────→│
  │←── response ───│                │             │
```

**Rules:**

- Three-column maximum; split into two diagrams if more participants
- Lifelines use `│`; messages use `──→` (right) or `←──` (left)
- Labels sit on the arrow line: `── label ──→`
- Participant names ≤20 chars, left-aligned at top
- Omit ACK returns unless they carry meaningful data

### Data Flow Diagrams

Use when showing data pipelines or transformation chains.

```
Source
    │
    ▼
Transform ──── enrich ────→ Enrichment
    │                            │
    ▼                            ▼
Sink A                     Cache Store
```

- Components as plain text (no brackets)
- Vertical: `│` and `▼`; horizontal: `──→`; return: `◄────`

### State Machine Diagrams

Use when a component has 3+ states with transitions.

```
┌──────────┐     approve     ┌───────────┐
│ Pending  │───────────────→│ Approved  │
└──────────┘                 └───────────┘
     │                            │
     │ timeout               │ start
     ▼                            ▼
┌──────────┐             ┌──────────┐     ok     ┌───────────┐
│ Expired  │             │ Running  │───────────→│ Succeeded │
└──────────┘             └──────────┘             └───────────┘
```

- State boxes use `┌ ┐ └ ┘ ─ │`
- Transitions: `──→` with label above/below
- Terminal states can include `✓` or `✗`

### When to Add Diagrams

- Sequence: 3+ components exchanging messages
- Data flow: pipeline with 3+ stages or branching paths
- State machine: a component has 3+ states with transitions
- Do NOT add a diagram for 2-node linear flows — use a numbered list instead
- Max width: 78 characters

## Entry and Exit Criteria

Enter when:

- a design tree already exists
- important branches remain vague or incomplete

Exit when:

- key branches have been refined to implementation-ready leaves
- the remaining work is mainly decision evaluation or readiness checking

## Handoff Rules

- Hand off to `decision-evaluation` when you surface a clear decision node with multiple real options.
- Hand off to `design-readiness-check` when key branches are closed and the main question becomes readiness.
- Hand back to `design-structure` if the design tree itself is missing a foundational branch.
- Hand back to `design-orchestrator` or `design-structure` immediately if `design_target_type` is missing.
- Do not invent fake option comparisons just to make progress.
- Do not use refinement to absorb a branch that should become a derived tree.
- Do not force workflow, methodology, or framework branches into system-shaped leaves.

---

## Journal Integration

When operating on a task tracked under `.agents/tasks/<task-id>/`, append a journal entry at this skill's milestone.

- **Trigger:** after a refinement pass updates the persisted design tree
- **Reserved key(s):** `saved` (re-save) and optionally `note` for what was refined
- **Entry shape:**
  ```
  ## <ISO8601-timestamp> — design-refinement
  saved: docs/design-tree/<file>.md
  [optional ≤ 15-line body; longer content goes to artifacts/]
  ```

Resolve the task id from the explicit caller argument or `.agents/tasks/.current`. If neither resolves, skip the append; do not guess.

See `task-journal` for the full convention.
