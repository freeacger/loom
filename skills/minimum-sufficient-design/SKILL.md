---
name: minimum-sufficient-design
description: "Do not use for mechanical implementation of a frozen contract, obvious one-line fixes, formatting-only changes, restating accepted decisions, or running defined verification. Use when a technical approach requires engineering judgment or design trade-offs: designing, comparing, reviewing, or reopening choices about invariants, authoritative facts, retries, unknown outcomes, compatibility, migration, irreversible commitments, underdesign, or overdesign."
---

# Minimum Sufficient Design

## Purpose

Judge whether a technical proposal carries the least evidence-backed complexity needed for its current scope.

Use risk as the scale, invariants as the floor, and feedback as calibration. Protect what cannot be traded, trade what can be traded, reject what lacks evidence, and recommend what fits now.

This skill is an engineering-judgment layer, not a delivery workflow, router, checklist, approval gate, or replacement for another skill. The active workflow owns the process. Project instructions, frozen contracts, and accepted decisions take precedence.

MVP defines what is in the current product scope. This skill judges the minimum guarantees required to support that scope; it does not redefine the MVP.

## Build the Shared Problem Model

Before comparing approaches, retrieve only the evidence that can change the decision:

- current project instructions and explicit user constraints;
- frozen contracts and accepted decisions;
- domain language and authoritative context;
- relevant implementation, tests, and authorized runtime facts.

Do not scan without a boundary. Distinguish current constraints, domain language, current implementation, and historical context. If documents and code disagree, expose the conflict instead of silently choosing one. A professional recommendation can name the preferable target owner, but it does not close an authority gap; until current governance identifies which source governs, label current authority unresolved.

Classify gaps by who can close them:

- **Evidence gap:** what is true is unknown. Advance safe, authorized verification; otherwise state the gap, its decision impact, and the smallest needed input or authority.
- **Alignment gap:** participants may mean different problems, scopes, terms, constraints, or success conditions. Align only differences that could change the recommendation.
- **Engineering judgment:** compare the evidence and recommend an approach. Do not push this responsibility back to the user.
- **Authority decision:** product preference, risk acceptance, resource commitment, or another choice whose consequences belong to an accountable owner. Ask that owner to decide.

The shared problem model is ready when the decision frame is understood. Agreement on one solution is not required.

## Judge Sufficiency and Minimality

Use these meanings together:

- **Sufficient:** non-tradeable constraints in the current scope are protected; material credible risks are reduced, explicitly accepted by the proper authority, or exposed as blockers; and decisive claims have verification at the same evidence level.
- **Minimal:** every important mechanism answers current value, a constraint, or a credible risk; a simpler way to provide the same guarantees has been considered; and no known lower-total-cost option is equally sufficient.
- **Underdesigned:** a necessary constraint, authoritative owner, failure convergence path, risk treatment, or verification capability is missing.
- **Overdesigned:** added capability, abstraction, state, automation, or hard-to-reverse commitment lacks current evidence, while a known simpler sufficient option exists.
- **Unresolved:** an evidence, alignment, or authority gap could still change the judgment.

Underdesign and overdesign can coexist. Minimal does not mean the fewest lines, modules, tables, services, or mechanisms. Necessary complexity is acceptable when it protects an invariant, makes ownership explicit, enables recovery, or supports verification.

## Shape the Trade-off Space

Separate:

1. non-tradeable constraints;
2. tradeable qualities;
3. credible risks;
4. future ideas without current evidence.

Explore two or three materially different paths only when there is a real trade-off, high impact, a new interface or persistence boundary, or a hard-to-reverse commitment. Do not manufacture alternatives for simple, low-risk work.

Compare only dimensions that can change the choice, such as current value, invariant protection, risk reduction, total complexity, reversibility, operating burden, and verification cost.

Creativity means finding a hidden assumption, a third path, a materially different mechanism, or a better framing. It is not a quota of options.

Allow evidence-backed complexity. Reject a stronger-looking mechanism when it does not prove or reduce the target risk.

## Recommend and Verify

Make a professional recommendation when the evidence supports one. State:

- the recommended approach and decisive reasons;
- what it protects and what it deliberately leaves out;
- costs, credible risks, and unresolved items;
- a meaningful alternative only when it could still be chosen;
- verification matched to each decisive claim.

Do not use a lower evidence layer to claim a higher-layer result. Static checks, focused tests, integration behavior, deployed state, and real-world outcomes prove different things.

Stop when the current scope supports an explainable, verifiable recommendation and no known decision-critical uncertainty could change it. If new evidence invalidates an assumption, revise or reverse only the affected judgment; do not defend the earlier recommendation for consistency's sake.

## Handle Existing Decisions

When an accepted decision, frozen contract, domain context, conflicting source, or possible override is present, read [references/alignment-and-authority.md](references/alignment-and-authority.md). Do not read it for an ordinary design with no authority or alignment issue.

If a proposal conflicts with a current decision, pause the affected branch. Identify the existing decision, the proposed change, the conflict, and the consequences. Recommend one of: preserve it, grant a bounded exception, or explicitly supersede it.

After an authorized supersession, the authoritative record must be updated before calling the design frozen or handing it to implementation. If updating it is outside authority, leave that obligation explicit.

## Apply Conditional Risk Tools

When the problem includes side effects, retries, unknown outcomes, concurrent writes, data migration, compatibility cutover, retention or delayed-recovery limits, expensive commitments, or long-lived architecture qualities, read [references/risk-and-evolution-tools.md](references/risk-and-evolution-tools.md). A durable delivery system or platform is a long-lived architecture commitment. Do not read this reference when those conditions are absent.

The core rules remain valid without this reference: preserve authority, bound automatic effects, keep unknown distinct from success or failure, and match evidence to claims.

## Use Theory and Examples Sparingly

Read [references/theory.md](references/theory.md) only when the user asks for theoretical grounding or a maintainer is changing the core definition.

Read [references/output-examples.md](references/output-examples.md) only when evaluating this skill, when the output mode is unclear, or when the user asks for examples.

Do not read either reference during an ordinary judgment merely because it exists.

## Collaborate Without Taking Over

Respect an explicitly invoked workflow or specialist skill. Provide engineering judgment without copying its procedure, terminology, state, or output contract. Select other capabilities only from currently visible metadata; do not invent skill names or maintain a compatibility table here.

If the user chooses a non-recommended but permissible option, respect the choice and record its costs and remaining risks. Still correct factual errors and surface conflicts with non-tradeable constraints.

In discussion, present only information that affects the trade-off. When asked for a judgment, freeze, or handoff, lead with the recommendation, decisive reasons, benefits, costs, credible risks, unknowns, necessary alternatives, and verification. Do not expose raw internal exploration or force a fixed template, word count, or section count.
