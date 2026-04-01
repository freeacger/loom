# Design Structure Reference

## Purpose

This file contains skill-local guidance for `design-structure`.

Keep `SKILL.md` focused on routing, core behavior, and output contract.
Put persistence policy and local templates here.

## Target-Type Skeletons

### system

Preferred top-level branches:
- Problem definition
- Scope and boundaries
- Core objects
- Core flows
- Interfaces and data
- Decision points
- Non-functional requirements
- Validation

### workflow

Preferred top-level branches:
- Problem definition
- Scope and boundaries
- Stages
- Inputs and outputs
- Handoffs and responsibilities
- Failure rollback
- Quality gates
- Validation

### methodology

Preferred top-level branches:
- Problem definition
- Scope and boundaries
- Applicability
- Decision rules
- Steps or phases
- Handoff form
- Exit conditions
- Validation

### framework

Preferred top-level branches:
- Problem definition
- Scope and boundaries
- Dimensions
- Modules
- Routing rules
- Handoff forms
- Exit conditions
- Validation

## Main Body Completion Threshold

The initial design tree's main body is complete only when all of the following are true:

- `design_target_type` is explicit
- `problem` and `scope` are explicit enough to define what the tree owns and what it excludes
- the tree has stable top-level branches that match the selected target-type skeleton
- each top-level branch has enough content to avoid being a title-only placeholder
- `open_branches` are listed explicitly
- `decision_nodes` are listed explicitly when real choices remain
- no foundational branch is still missing for the chosen target type

If these conditions are not met, continue structure work rather than persisting.

## Persistence

`design-structure` primarily produces `design_state`.

Persist to `docs/design-tree/<feature-name>.md` as soon as the main body completion threshold is reached.

After saving:

- treat the file as the authoritative persisted design artifact
- mark the document status as `draft`
- keep `design_state` aligned with the saved file
- recommend `design-refinement` as the default next step unless a concrete decision node or readiness gate is clearly the real blocker

## Document Status

Use these repo-local document states:

- `draft`: the tree has been persisted after main body completion, but refinement, decision closure, or readiness gating is still in progress
- `ready-for-planning`: `design-readiness-check` has passed and there are no blocking gaps preventing implementation planning

Transition rules:

- the first persisted version must be `draft`
- stay in `draft` while meaningful `open_branches`, unresolved decision blockers, or readiness failures remain
- promote to `ready-for-planning` only after `design-readiness-check` returns READY

## File Template

When persisting, this is the preferred file shape:

```markdown
# <Feature Name> Design Tree

## Status
`draft | ready-for-planning`

## Design Target Type
`system | workflow | methodology | framework`

## Problem
[confirmed content]

## Scope
### Included
- ...
### Excluded
- ...

## Assumptions
- ...

## Design Tree
[tree diagram]

## Open Branches
- ...

## Decision Nodes
- ...

## Decisions
[filled later by decision-evaluation]
```
