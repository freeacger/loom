---
name: design-readiness-check
description: Check whether a design is complete enough to move into implementation planning. Use when a design appears mostly done and needs a final readiness review for missing branches, weak assumptions, unresolved risks, failure handling, validation gaps, or non-functional omissions. Trigger before invoking writing-plans or when the user asks whether the current design is ready to implement. Do not use as a general design-document audit for external docs or as a replacement for initial design work.
---

# Design Readiness Check

## Overview

This skill is the quality gate between design work and implementation planning.

Its job is to answer one question clearly: is the current design complete enough to move into `writing-plans`?

It is not a replacement for `design-decision-audit`. That skill audits standalone design or plan documents. This skill checks the readiness of an in-progress design workflow before planning.

## When to Use

Use this skill when:

- the design looks mostly complete
- the next possible step is `writing-plans`
- the user asks whether the design is ready to implement
- the remaining concern is completeness, not discovery

Do not use this skill when:

- the design tree is still missing
- major branches remain vague
- core decisions are still unresolved
- the user is asking for a general audit of an external design document

## Core Responsibilities

Your responsibilities are:

1. Check for empty or weak branches in the design tree.
2. Check for unresolved assumptions and hidden dependencies.
3. Check for missing failure handling, validation strategy, or non-functional requirements.
4. Check whether key risks are documented enough for implementation planning.
5. Return a clear readiness judgment, not a vague summary.

## Readiness Standard

A design is ready for planning only when:

- the main design tree is present
- key branches are refined enough to guide implementation
- major decision nodes are resolved or explicitly deferred with acceptable rationale
- failure paths and validation strategy are not missing
- blocking risks are either mitigated or clearly acknowledged

## Expected Outputs

Produce or update a `design_state` that includes:

- `open_branches`
- `risks`
- `validation`
- `status.ready_for_planning`
- `status.blocking_issues`

Always return an explicit result:

- ready for planning
- not ready for planning

## Diagram Conventions

Present the readiness verdict as a status checklist inside a code block (no language tag):

```
Readiness Check
├── Design tree present          ✓
├── Key branches refined         ✓
├── Decisions resolved           ✗ (storage choice pending)
├── Failure paths documented     ✓
├── Validation strategy defined  ✓
└── Blocking risks mitigated     ✗ (migration cutover risk)

Verdict: NOT READY — 2 blocking issues
```

**Rules:**

- Use `✓` (pass) and `✗` (fail) markers with inline reason for failures
- Max width: 78 characters
- Always include this checklist in the readiness verdict

## Entry and Exit Criteria

Enter when:

- the design is near completion
- the next meaningful step may be implementation planning

Exit when:

- you have issued a clear readiness decision
- you have identified the next route if the design is not ready

## Handoff Rules

- Hand off to `writing-plans` only when the design is clearly ready.
- Hand off to `design-structure` when foundational branches are still missing.
- Hand off to `design-refinement` when important branches exist but are still weak.
- Hand off to `decision-evaluation` when the real blocker is an unresolved decision node.
- Never give a "probably ready" answer. The result must be explicit.
