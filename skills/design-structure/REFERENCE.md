# Design Structure Reference

## Purpose

This file contains skill-local guidance for `design-structure`.

Keep `SKILL.md` focused on routing, core behavior, and output contract.
Put optional persistence and local templates here.

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

## Optional Persistence

`design-structure` primarily produces `design_state`.

Persist to `docs/design-tree/<feature-name>.md` only when one of these is true:
- the user explicitly asks to save the design
- the current task explicitly requires a design artifact
- the parent-tree handoff explicitly asks for a saved derived tree

If persistence is not required, keep the output in chat and `design_state`.

## Optional File Template

When persistence is required, this is the preferred file shape:

```markdown
# <Feature Name> Design Tree

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
