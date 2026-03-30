---
name: design-orchestrator
description: Coordinate design-stage work across specialized design skills. Use when a task needs structured design before implementation, including design decomposition, design clarification, decision routing, or readiness checks. Trigger whenever the user wants to turn an idea into an implementation-ready design, refine a partially formed design, or determine the next design step. Do not use for direct execution, implementation planning, or single-step coding tasks.
---

# Design Orchestrator

## Overview

This skill is the entrypoint for design-stage work.

It does not do the deep design work itself. Its job is to inspect the current design state, choose the right next design skill, and keep the workflow moving until the design is ready for `writing-plans`.

## When to Use

Use this skill when:

- the task needs design before implementation
- the user wants to turn an idea into an implementation-ready design
- the design exists, but the next step is unclear
- the task needs routing between design decomposition, decision analysis, and readiness review

Do not use this skill when:

- the user is asking for direct execution
- the task is already in implementation planning
- the task is a single-step coding or editing request

## Shared Design State

Assume the design workflow passes around a shared `design_state` with these logical fields:

- `problem`
- `scope`
- `design_tree`
- `open_branches`
- `decision_nodes`
- `decisions`
- `risks`
- `validation`
- `status`

You do not need a strict schema validator. You do need stable reasoning over these fields.

## Core Responsibilities

Your responsibilities are:

1. Determine whether the task is actually in the design stage.
2. Inspect the current `design_state` and identify the most useful next skill.
3. Route the task to exactly one next design skill.
4. Re-evaluate after each handoff until the design either becomes ready for planning or the user stops.
5. Prevent premature transition into `writing-plans`.

## Routing Rules

Route to `design-structure` when:

- there is no real design tree yet
- the task is still a vague idea or feature request
- scope, boundaries, core objects, or key flows are still missing

Route to `design-refinement` when:

- a design tree exists
- major branches are still shallow, vague, or unresolved
- the main need is deeper decomposition, edge-case coverage, or failure-path clarification

Route to `decision-evaluation` when:

- there is a bounded decision node with real alternatives
- the task has become a concrete choice such as architecture, auth model, state handling, storage, sync, or coordination style

Route to `design-readiness-check` when:

- the design appears mostly complete
- the remaining question is whether it is safe to move into implementation planning

## Entry and Exit Criteria

Enter when:

- the task needs design-stage coordination
- the user has not asked to skip design

Exit when:

- `design-readiness-check` returns that the design is ready for planning
- the user explicitly stops the design workflow
- the task turns out not to require design-stage work after all

## Handoff Rules

- Never expand a branch in depth yourself if a specialized design skill should do it.
- Never compare options broadly if the real next step is to structure or refine the design.
- If a downstream skill changes the design materially, re-check routing instead of assuming the next step.
- Only send the task to `writing-plans` after `design-readiness-check` has clearly passed.
- If a downstream skill cannot be invoked in the current context, still name it explicitly as the next step and stop. Do not execute its responsibilities inline as a substitute.
