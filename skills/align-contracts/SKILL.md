---
name: align-contracts
description: Align an existing target design across its applicable contract surfaces. Use only when the user explicitly invokes align-contracts or a specification workflow requests contract preflight before planning; do not trigger during ordinary design discussion, implementation, or review.
compatibility: Requires the user-invoked grill-with-docs companion skill when alignment exposes a new design decision.
---

# Align Contracts

## Purpose

Treat the artifacts for one change as representations of one target design. Make their shared semantics agree, persist the result in a project-recognized carrier, and state whether downstream specification work can proceed.

This is a consistency closure over an existing design. New business decisions belong to `grill-with-docs`; implementation belongs downstream.

## Result Protocol

Classify the result internally into exactly one state:

- `ALIGNED`: every applicable target contract is mutually consistent, decision-complete, and recorded in a project-recognized carrier.
- `BLOCKED`: a missing fact, permission, prerequisite, or new design decision can still change the target contracts.
- `NO_CONTRACT_CHANGE`: the scoped work changes no contract surface and needs no contract artifact.

`ALIGNED` describes target-design readiness. It does not claim that code, migrations, tests, deployment, or acceptance are complete.

## Run the Alignment

### 1. Bound the change

Require one named feature, change, or contract scope. Keep current implementation, historical context, and target design distinct.

Read project instructions and locate `docs/agents/align-contracts.md`. Before relying on it, verify that it establishes the result carrier, authority relationships, current-versus-target distinction, localization or rendering rules, and downstream handoff. When the policy is absent or incomplete, read [Project Initialization](references/project-initialization.md) and follow its permission-gated create-or-repair path before continuing.

Find the governing decisions, candidate contracts, and only the implementation evidence needed for this scope. The user names the change; the agent finds the relevant files.

Complete this step when the target scope and the recognized carrier for its result are explicit.

### 2. Build one semantic model

Extract the semantics that every applicable surface must preserve:

- authority and ownership;
- identity, uniqueness, and cardinality;
- missing, empty, default, and precedence behavior;
- lifecycle, mutability, and snapshot boundaries;
- idempotency, concurrency, partial success, and recovery;
- compatibility, migration, and cutover;
- verification obligations.

Map only actual surfaces such as HTTP, RPC, schema, cache, event, file format, runtime state, or business code. Mark an inspected but irrelevant surface `Not Applicable`; do not manufacture a surface to fill a template.

Complete this step when each applicable surface can be compared against the same shared semantics.

### 3. Close what the evidence already decides

Resolve gaps according to ownership:

- **Evidence gap:** inspect the bounded code or documents. Ask at most one batched clarification round when the answer already exists but its source, scope, or authority is unavailable.
- **Representation gap:** when accepted evidence is sufficient, correct the target contract and its recognized carrier under the active mutation rules. Preserve an existing representation when it can express the accepted semantics; changing a wire type, encoding, dialect, or compatibility shape requires direct authority rather than inference from another surface.
- **Decision gap:** stop. A user answer would create or change contract semantics, so return `BLOCKED` with a portable handoff to the required `grill-with-docs` companion.

The clarification round may locate evidence, confirm an already-made decision, or request write permission. It must not become a reduced design interview. If clarification does not close the evidence gap, remain `BLOCKED`.

A decision handoff names the exact question, why it changes the contracts, affected surfaces, governing documents to update, and `return_to: align-contracts`. Because `grill-with-docs` is user-invoked, instruct the user to invoke it explicitly. If it is unavailable, report the missing prerequisite rather than performing a fallback interview.

After the decision is recorded, start a fresh alignment pass and re-read the updated authority.

### 4. Persist and verify the target contracts

Write the aligned target design to the carrier selected by project policy. Preserve the native authority of existing artifacts: the carrier may contain exact target changes and cross-contract invariants without claiming that implementation files already match them.

Re-read the stored result and compare every applicable surface again. `ALIGNED` requires no unresolved blocker and no stale or contradictory target representation.

When showing contract changes or a cross-surface conflict, read [Contract Output Formats](references/contract-output-formats.md). Skip that reference for a simple `NO_CONTRACT_CHANGE` result.

## Report the Result

Treat the state and result fields as a semantic checklist, not a YAML template. Write the visible result in one project-appropriate language; do not repeat an internal state literal beside its localized heading.

Lead with a localized outcome heading and one sentence that stands on its own. Add a compact table or sections only when they improve scanning:

- `ALIGNED`: identify the real result carrier, summarize material conclusions, and name `to-spec` when it is the requested downstream step.
- `BLOCKED`: show the unresolved question or missing prerequisite, affected surfaces, and one concrete resolver action. Avoid a generic “resolve blocker.”
- `NO_CONTRACT_CHANGE`: normally use only the outcome heading and one short reason. Omit self-referential authority, empty changes, and a no-op next step; create no contract artifact.

Render scope, authority, changes, blocker, and next action only when each adds information. Technical identifiers, code, and workflow names stay unchanged; explanatory prose and labels use the selected language.

## Completion Criteria

Finish only when exactly one status is justified:

- `ALIGNED`: the target design is stored, every applicable surface agrees, and downstream work has a stable authority to read.
- `BLOCKED`: the remaining gap and its owner are explicit, with the smallest actionable handoff.
- `NO_CONTRACT_CHANGE`: bounded evidence shows that external behavior, persistent facts, coordination state, and runtime contracts are unchanged.
