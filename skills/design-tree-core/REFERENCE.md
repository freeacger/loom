# Design Tree Core Reference

## Purpose

This file defines the minimum shared reference rules for the design-tree skill family.

It exists to support consistent behavior across:
- design-orchestrator
- design-structure
- design-refinement
- design-readiness-check

It is not a template library.
It is not a project knowledge base.
It is not a design document store.

---

## 1. Shared Concepts

### 1.1 Design Tree
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

### 1.2 Parent Tree
A parent tree is the currently authoritative tree for a design problem domain.

It owns:
- the main framing of the problem
- the original stable scope
- routing into derived trees when needed

### 1.3 Derived Tree
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

### 1.4 Open Branch
An open branch is an unresolved area inside a tree that still belongs to that tree's problem domain.

Not every open branch deserves a derived tree.

### 1.5 Stable Decision System
A branch becomes a stable decision system when it:
- repeatedly appears in work
- requires its own routing logic
- has its own inputs and outputs
- has its own completion check
- no longer behaves like a normal branch refinement

### 1.6 Handoff
A handoff is the minimum structured transfer from one tree to another.

A handoff exists to prevent:
- silent scope drift
- duplicated reasoning
- parent/child ambiguity
- hidden assumptions between trees

---

## 2. Derivation Rules

### 2.1 When to Derive a New Tree

Derive a new tree only if all conditions below are true:

1. The parent tree is starting to answer a second distinct core question.
2. The new question appears repeatedly, not as a one-off exception.
3. The branch now behaves like a stable decision system.
4. The new tree can define its own scope and done criteria.
5. Deriving it will make the parent tree smaller and clearer.

If any condition fails, do not derive.

### 2.2 When Not to Derive

Do not derive a new tree when:

- the branch only needs deeper refinement
- the content is mainly examples or explanations
- the issue is project-specific
- the branch is only temporarily large
- the content belongs in a checklist, report, template, or script
- the problem is still clearly part of the parent tree's original core question

### 2.3 Derivation Test

Before deriving, ask:

- Is this still the same problem, just deeper?
- Or is this now a different problem with its own stable decisions?

If it is still the same problem, refine.
If it is a different stable problem, derive.

---

## 3. Parent / Child Handoff Contract

### 3.1 Minimum Handoff Fields

A parent tree handing off to a derived tree should provide:

- parent_tree_name
- derived_tree_name
- reason_for_derivation
- branch_being_extracted
- inherited_constraints
- unresolved_questions
- expected_output
- return_conditions

### 3.2 Parent Responsibilities After Derivation

After a derived tree is created, the parent tree must:

- retain only the branch summary
- link to the derived tree explicitly
- stop expanding the extracted branch inline
- record the handoff status
- define when the child should return a result

The parent must not continue growing a duplicate copy of the child logic.

### 3.3 Child Responsibilities

A derived tree must:

- declare its scope explicitly
- declare what it does not own
- consume the parent handoff as input
- avoid redefining the parent problem
- return results in a form the parent can consume

### 3.4 Return Paths

A derived tree may return one of these outcomes:

- resolved result
- unresolved result with explicit open questions
- recommendation to refine parent assumptions
- recommendation to derive another tree only if derivation rules are satisfied again

---

## 4. Anti-Bloat Governance

### 4.1 Core Rule

Keep trees small enough to preserve routing clarity.

A tree should store stable structure, not accumulated history.

### 4.2 What Belongs in a Tree

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

### 4.3 Growth Controls

When a tree grows, prefer this order:

1. compress wording
2. remove duplication
3. move examples out
4. move project-specific content out
5. derive a new tree only if derivation rules are met

Do not derive a new tree just because the current tree is long.

### 4.4 Eviction Rules

Move content out of a tree when:

- it is only explanatory
- it is only relevant to one project
- it belongs to one downstream workflow
- it is repeated in multiple places
- it no longer changes routing or design decisions

### 4.5 Compaction Trigger

Run a compaction pass when any of these appear:

- repeated caveats
- duplicated branch definitions
- mixed responsibilities
- large sections of examples inside the tree
- parent and child trees both expanding the same branch
- the tree is harder to route from than to read

### 4.6 Anti-Bloat Priority

When choosing between preserving detail and preserving structure, preserve structure.

---

## 5. Use by Other Skills

### design-orchestrator
Use this reference to decide:
- whether to keep routing within the current tree
- whether a new tree should be derived

### design-structure
Use this reference when:
- creating a new derived tree
- defining parent/child boundaries

### design-refinement
Use this reference when:
- deciding whether a branch should stay in refinement
- deciding whether refinement has crossed into derivation territory

### design-readiness-check
Use this reference only to detect:
- mixed responsibilities
- tree drift
- unresolved branch ownership

---

## 6. Maintenance Rule

This reference should change rarely.

New content may be added only if it is:
- shared across multiple design skills
- stable over time
- directly relevant to derivation, handoff, boundaries, or anti-bloat behavior

If content is useful but not core, move it somewhere else.
