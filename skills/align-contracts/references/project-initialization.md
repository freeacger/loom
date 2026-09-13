# Project Initialization

Read this reference only when `docs/agents/align-contracts.md` is absent or incomplete.

## Establish the carrier once

Inspect the project's existing instructions, documentation layout, and contract authorities before proposing a policy. Reuse the project's language and established document locations.

Ask permission before creating `docs/agents/align-contracts.md`. The request should show the proposed path and the minimal choices that will be recorded.

The policy needs only:

```markdown
# <Localized Align Contracts Policy Title>

## Result carrier

Where an alignment result is stored. This may be a dedicated feature document,
an existing design or ADR, or another project-recognized location.

## Authority map

Which sources govern domain decisions and each contract surface. State how a
cross-contract result relates to native sources such as OpenAPI, Proto, schema,
or migration definitions.

## Current and target state

How documents distinguish current implementation from the target design that
downstream specification work should implement.

## Localization and rendering

The document language and any project-specific names, prefixes, table formats,
or code-block conventions.

## Downstream handoff

What downstream workflow reads and what `ALIGNED` permits next.
```

Keep cleanup automation, lifecycle governance, exhaustive surface catalogs, and speculative templates outside initialization.

## Repair an incomplete policy

Treat the policy as incomplete when any of the five concerns above is absent or too ambiguous to govern the current scope. Missing project evidence is not `Not Applicable`: that label requires evidence that a surface is genuinely outside the change.

Show a localized Markdown patch containing only the missing decisions. Name conflicts the missing authority must resolve, and leave their semantics undecided. Ask permission before editing the project policy, return `BLOCKED`, and use `next: approve-project-adapter`. After approval, apply the patch and start a fresh alignment pass against the completed policy.

If permission is declined, ask whether the current conversation is explicitly recognized as the temporary carrier for this run. Continue only when the project or user recognizes a carrier; otherwise return `BLOCKED` with `next: choose-contract-carrier`.
