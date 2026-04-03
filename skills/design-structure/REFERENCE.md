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

## Stable-to-Reference Threshold

The initial design tree first becomes stable enough to reference safely only when all of the following are true:

- `design_target_type` is explicit
- `problem` and `scope` are explicit enough to define what the tree owns and what it excludes
- the tree has stable top-level branches that match the selected target-type skeleton
- each top-level branch has enough content to avoid being a title-only placeholder
- `open_branches` are listed explicitly
- `decision_nodes` are listed explicitly when real choices remain
- no foundational branch is still missing for the chosen target type
- a downstream design skill could read the persisted file without misunderstanding the current design boundary

If these conditions are not met, continue structure work rather than persisting.

## Persistence

`design-structure` primarily produces `design_state`.
This save location and timing contract is repo-local to this repository, not a shared default for the design-tree family.

Persist to `docs/design-tree/<feature-slug>.md` when the tree first reaches the stable-to-reference threshold, and do so before any downstream design handoff.

After saving:

- treat the file as the authoritative persisted design artifact
- mark the document status as `draft`
- keep `design_state` aligned with the saved file
- recommend `design-refinement` as the default next step unless a concrete decision node or readiness gate is clearly the real blocker

## Repo-Local File Naming

Use lowercase kebab-case slugs for all persisted design-tree files.
Treat the filename as part of the repo-local handoff contract, not as a shared design-tree family rule.

### Main Trees

For a root design tree, use:

- `docs/design-tree/<feature-slug>.md`

Choose `<feature-slug>` from the owned problem domain or feature boundary, not from an implementation tactic, meeting name, or vague placeholder.

Good examples:

- `docs/design-tree/api-gateway.md`
- `docs/design-tree/push-delivery-system.md`

Avoid:

- `docs/design-tree/design-v2.md`
- `docs/design-tree/new-thing.md`
- `docs/design-tree/refinement.md`

### Derived Trees

For a derived tree created from a parent tree, use:

- `docs/design-tree/<parent-slug>--<derived-slug>.md`

Choose `<derived-slug>` to name the child-owned subproblem, not a generic continuation marker.

Good examples:

- `docs/design-tree/api-gateway--rate-limiting.md`
- `docs/design-tree/push-delivery-system--retry-policy.md`

Avoid:

- `docs/design-tree/api-gateway--part-2.md`
- `docs/design-tree/api-gateway--refinement.md`
- `docs/design-tree/api-gateway--v2.md`

### Same-Topic Iterations

If the work is ordinary refinement of the same authoritative design lineage, keep the same file path and update the existing file in place.
Do not create `-v2`, `-final`, `-new`, or similar suffixes for normal follow-on refinement.

If a materially different alternative lineage must coexist, create a separate root file using:

- `docs/design-tree/<feature-slug>--alt-<qualifier>.md`

When doing this, add an explicit relationship note in the document body such as `Alternative To` or `Supersedes` so downstream readers do not confuse the two files.

## Document Status

Use these repo-local document states:

- `draft`: the tree has been persisted after first reaching the stable-to-reference threshold, but refinement, decision closure, or readiness gating is still in progress
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

## File Lineage
- Parent Tree: [optional]
- Alternative To: [optional]
- Supersedes: [optional]

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
