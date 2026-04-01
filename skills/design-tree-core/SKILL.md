---
name: design-tree-core
description: Internal/shared core rules for design-tree skills. Use only when maintaining the design-tree system itself or when another design skill needs shared governance rules for derivation, handoff, boundaries, or anti-bloat controls. Do not trigger for ordinary user design requests, and do not use as a replacement for design-orchestrator, design-structure, or design-refinement.
---

# Design Tree Core

## Overview

This skill is the shared governance core for the design-tree skill family.

It is not a general design skill.
It is not a user-facing entrypoint for normal design work.
It exists to provide stable shared rules that other design skills can rely on.

Its job is to define and protect the minimum shared rules for:

- design-tree derivation
- parent/child tree boundaries
- handoff contracts
- anti-bloat governance
- shared design-tree vocabulary

## When to Use

Use this skill only when:

- maintaining or revising the design-tree skill system itself
- deciding whether a new design tree should be derived
- checking whether shared design-tree rules belong in a common core
- aligning multiple design skills on shared boundary or handoff rules
- preventing design-tree drift, duplication, or bloat

Do not use this skill when:

- the user needs normal design routing
- the task is to create an initial design tree
- the task is to refine an existing design tree
- the task is to evaluate a bounded design decision
- the task is to check whether a design is ready for planning
- the task is to write a design doc, report, note, or plan
- the task is to store project-specific conclusions, examples, or temporary guidance

## Core Responsibility

This skill owns only rules that are all of the following:

1. Shared across at least two design-tree skills
2. Stable over time
3. Directly relevant to design-tree boundaries, routing, derivation, handoff, or anti-bloat governance
4. Too central to leave implicit
5. Too shared to belong to only one skill

If a rule fails any of those tests, it does not belong here.

## Forbidden Content

The following content must not be added to this skill or its references:

- project-specific conclusions
- one-off discussion outcomes
- long examples or case studies
- detailed templates
- release workflow details
- single-skill-specific rules
- content-production rules for reports, notes, or plans
- FAQ-style patch accumulation
- explanatory expansions that do not change shared design-tree behavior

If content is useful but not core, move it elsewhere.

## Admission Rule

New content may enter this skill only if it satisfies all checks below:

1. It affects more than one design-tree skill.
2. It is a stable rule, not a local workaround.
3. It changes or protects shared boundaries, routing, derivation, handoff, or anti-bloat behavior.
4. Omitting it would cause shared drift or inconsistent decisions.
5. It cannot be placed more naturally in:
   - a specific design skill
   - a reference file for one skill
   - an eval
   - an example
   - a design doc
   - a report
   - a checklist
   - a script

If any check fails, reject the addition.

## Eviction Rule

Content must be moved out of this skill when any of the following becomes true:

- it is only used by one skill
- it becomes project-specific
- it is mainly explanatory rather than behavioral
- it is better represented as an example, template, checklist, or script
- it increases size without increasing shared governance value

Do not keep content here just because it was historically added.

## Derivation Scope

This skill may define shared rules for when a design tree should be derived into a new tree.

It must not define the full operating logic of any derived tree.
Once a derived tree has its own stable responsibility, that logic belongs in the derived tree, not here.

## Output Contract

When this skill is used, the output should be limited to one or more of:

- shared rule clarification
- derivation decision criteria
- handoff contract clarification
- anti-bloat governance guidance
- keep / move / derive recommendations for design-tree content

It should not produce a normal design tree as output.

## Maintenance Rule

Keep this skill small and rigid.

- Prefer the shortest rule that preserves shared behavior.
- Prefer moving detail out over expanding this file.
- Prefer reference files over inline accumulation.
- Prefer deletion over historical clutter.

This skill is healthy only if it remains smaller and more stable than the skills that depend on it.

## Relationship to Other Skills

- `design-orchestrator` may use this skill when deciding whether to derive a new tree.
- `design-structure` may use this skill when creating a derived tree.
- `design-refinement` may use this skill when a branch appears to be evolving into a separate stable decision system.
- `design-readiness-check` may use this skill only to detect tree-structure drift or mixed responsibilities.

This skill must not take over their normal responsibilities.

## Reference Files

Detailed shared rules should live in companion reference files such as:

- `REFERENCE.md`
- `CHANGELOG.md`

Keep `SKILL.md` as the strict entry contract, not the full knowledge base.
