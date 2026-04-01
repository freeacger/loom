# Design Tree Core Reference

## Purpose

This file defines the minimum shared reference rules for the design-tree skill family.

It exists to support consistent behavior across:
- design-orchestrator
- design-structure
- design-refinement
- design-readiness-check
- decision-evaluation

It is not a template library.
It is not a project knowledge base.
It is not a design document store.

---

## 1. Shared Design State

### 1.1 Required Fields

All design-tree skills reason over a shared `design_state` with these required logical fields:

- `problem`
- `scope`
- `design_tree`
- `open_branches`
- `decision_nodes`
- `external_dependencies`
- `decisions`
- `risks`
- `validation`
- `status`
- `design_target_type`

The family does not require a strict schema validator.
It does require stable treatment of these fields as required design-stage state.

### 1.2 Required Target Type

`design_target_type` is a mandatory field of `design_state`.
It is not optional. It is not a defaultable field. It is not a post-hoc annotation.

Allowed values:
- `system`
- `workflow`
- `methodology`
- `framework`

If a design-state input is missing `design_target_type`, every design-tree skill must treat the state as invalid.
No design-tree skill may silently infer, assume, default, or derive a `design_target_type` value from context, problem description, or any other field.

Required remediation paths when `design_target_type` is absent:
1. **Stop and reject**: treat the state as incomplete and refuse to proceed.
2. **Route to the step that can set it explicitly**: hand back to the user, the orchestrator, or the entry skill that is responsible for establishing the initial design state.

A skill may ask the user to provide the type explicitly.
A skill may not choose the type on the user's behalf without an explicit user decision.

### 1.3 Shared Output Contract

The primary output of design-tree skills is `design_state`.

The family does not share a default persistence contract.
Saving a design file is a skill-local or repo-local adapter behavior, not a shared design-tree rule.

### 1.4 Design Tree

A design tree is a structured representation of a stable design problem space.
It should capture:
- scope
- major branches
- decision nodes
- open branches
- handoff points
- readiness state

A design tree is not:
- a task board
- a report
- a writing outline
- a collection of examples
- a project log

### 1.5 Parent Tree

A parent tree is the currently authoritative tree for a design problem domain.

It owns:
- the main framing of the problem
- the original stable scope
- routing into derived trees when needed

### 1.6 Derived Tree

A derived tree is a new tree created when a branch has evolved into a separate stable decision system.

A derived tree must:
- answer a different core question from the parent tree
- have its own boundary
- have its own completion criteria
- consume a defined handoff from the parent tree

A derived tree must not:
- duplicate the full parent tree
- act as a dumping ground for overflow detail
- redefine the parent tree's scope silently

### 1.7 Open Branch

An open branch is an unresolved area inside a tree that still belongs to that tree's problem domain.

Not every open branch deserves a derived tree.

### 1.8 Stable Decision System

A branch becomes a stable decision system when it:
- repeatedly appears in work
- requires its own routing logic
- has its own inputs and outputs
- has its own completion check
- no longer behaves like a normal branch refinement

### 1.9 Handoff

A handoff is the minimum structured transfer from one tree to another.

A handoff exists to prevent:
- silent scope drift
- duplicated reasoning
- parent/child ambiguity
- hidden assumptions between trees

---

## 2. Target Type Classification

### 2.1 system

Use `system` when the design is primarily about components, interfaces, data flow, runtime boundaries, or failure behavior between parts of a built system.

Typical questions:
- What are the core objects or services?
- How do adjacent parts interact?
- What fails, where, and how is it validated?

### 2.2 workflow

Use `workflow` when the design is primarily about ordered phases, stage handoffs, operator roles, rollback paths, or quality gates.

Typical questions:
- What are the stages?
- What enters and exits each stage?
- Who or what owns each handoff?

### 2.3 methodology

Use `methodology` when the design is primarily about a repeatable method, decision process, stop condition, or judgment framework for doing work.

Typical questions:
- When does this method apply?
- What rules govern progress?
- When should the user stop or escalate?

### 2.4 framework

Use `framework` when the design is primarily about dimensions, routing rules, classification rules, or coordination contracts that other work operates inside.

Typical questions:
- What dimensions structure the problem?
- How is work routed?
- What are the handoff forms and exit rules?

### 2.5 Classification Rule

If multiple interpretations are plausible, choose the type that best matches the design's primary core question.
Do not force a workflow or methodology design into `system` just because it can be described with components.

---

## 3. Type-Specific Completion Standards

### 3.1 system

A branch is implementation-ready only when its leaf nodes can answer:

1. What it is responsible for
2. What it is not responsible for
3. How it interacts with adjacent parts
4. What failure looks like
5. How it will be validated

### 3.2 workflow

A branch is implementation-ready only when its leaf nodes can answer:

1. What the stage is trying to achieve
2. What inputs enter and outputs leave
3. Who or what owns the stage
4. What rollback or retry path exists
5. What quality gate closes the stage

### 3.3 methodology

A branch is implementation-ready only when its leaf nodes can answer:

1. When the method applies
2. When it does not apply
3. What decision rules guide progress
4. What handoff form it produces
5. What exit or stop condition ends the method

### 3.4 framework

A branch is implementation-ready only when its leaf nodes can answer:

1. What dimension or module it defines
2. What it explicitly does not own
3. What routing or classification rule it applies
4. What handoff form it expects
5. What exit condition or completion rule closes it

---

## 4. Derivation Rules

### 4.1 When to Derive a New Tree

Derive a new tree only if all conditions below are true:

1. The parent tree is starting to answer a second distinct core question.
2. The new question appears repeatedly, not as a one-off exception.
3. The branch now behaves like a stable decision system.
4. The new tree can define its own scope and done criteria.
5. Deriving it will make the parent tree smaller and clearer.

If any condition fails, do not derive.

### 4.2 When Not to Derive

Do not derive a new tree when:

- the branch only needs deeper refinement
- the content is mainly examples or explanations
- the issue is project-specific
- the branch is only temporarily large
- the content belongs in a checklist, report, template, or script
- the problem is still clearly part of the parent tree's original core question

### 4.3 Derivation Test

Before deriving, ask:

- Is this still the same problem, just deeper?
- Or is this now a different problem with its own stable decisions?

If it is still the same problem, refine.
If it is a different stable problem, derive.

---

## 5. Parent / Child Handoff Contract

### 5.1 Minimum Handoff Fields

A parent tree handing off to a derived tree should provide:

- `parent_tree_name`
- `derived_tree_name`
- `reason_for_derivation`
- `branch_being_extracted`
- `inherited_constraints`
- `unresolved_questions`
- `expected_output`
- `return_conditions`

### 5.2 Parent Responsibilities After Derivation

After a derived tree is created, the parent tree must:

- retain only the branch summary
- link to the derived tree explicitly
- stop expanding the extracted branch inline
- record the handoff status
- define when the child should return a result

The parent must not continue growing a duplicate copy of the child logic.

### 5.3 Child Responsibilities

A derived tree must:

- declare its scope explicitly
- declare what it does not own
- consume the parent handoff as input
- avoid redefining the parent problem
- return results in a form the parent can consume

### 5.4 Return Paths

A derived tree may return one of these outcomes:

- resolved result
- unresolved result with explicit open questions
- recommendation to refine parent assumptions
- recommendation to derive another tree only if derivation rules are satisfied again

---

## 6. Anti-Bloat Governance

### 6.1 Core Rule

Keep trees small enough to preserve routing clarity.

A tree should store stable structure, not accumulated history.

### 6.2 What Belongs in a Tree

Allowed:
- stable boundaries
- major branches
- decision points
- handoff rules
- completion criteria
- open branches that still belong to the tree

Not allowed:
- long examples
- repeated restatements
- project-specific conclusions
- temporary execution notes
- release instructions
- template bodies
- FAQ accumulation
- repeated caveats that belong elsewhere
- persistence adapters that only matter to one repo

### 6.3 Growth Controls

When a tree grows, prefer this order:

1. compress wording
2. remove duplication
3. move examples out
4. move project-specific content out
5. derive a new tree only if derivation rules are met

Do not derive a new tree just because the current tree is long.

### 6.4 Eviction Rules

Move content out of a tree when:

- it is only explanatory
- it is only relevant to one project
- it belongs to one downstream workflow
- it is repeated in multiple places
- it no longer changes routing or design decisions

### 6.5 Compaction Trigger

Run a compaction pass when any of these appear:

- repeated caveats
- duplicated branch definitions
- mixed responsibilities
- large sections of examples inside the tree
- parent and child trees both expanding the same branch
- the tree is harder to route from than to read

### 6.6 Anti-Bloat Priority

When choosing between preserving detail and preserving structure, preserve structure.

---

## 7. Use by Other Skills

### design-orchestrator
Use this reference to decide:
- whether a design-state input is complete enough to route
- whether to keep routing within the current tree
- whether a new tree should be derived

### design-structure
Use this reference when:
- confirming `design_target_type`
- choosing the initial branch skeleton
- creating a new derived tree
- defining parent/child boundaries

### design-refinement
Use this reference when:
- deciding whether a branch should stay in refinement
- deciding whether refinement has crossed into derivation territory
- applying the correct completion standard for the current target type

### design-readiness-check
Use this reference only to detect:
- missing required state
- mixed responsibilities
- tree drift
- unresolved branch ownership
- type-specific readiness gaps

### decision-evaluation
Use this reference when:
- confirming that a bounded decision belongs to the current target type
- feeding the chosen option back into the correct design-state shape
