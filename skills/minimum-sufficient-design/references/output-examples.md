# Output Examples

Load this reference only while evaluating the skill, when the output mode is unclear, or when the user asks for examples. These are patterns, not fixed templates or predetermined answers.

## Discussion

> The current scope needs a timely hint, but correctness already comes from an authoritative read. A disposable hint plus read-time recalculation is sufficient unless the latency requirement proves that repair path too slow. A durable event pipeline would add delivery, retry, backlog, and operating obligations without protecting a new invariant.

Why it works: it identifies authority, a current guarantee, the simpler sufficient path, and the evidence that could reopen the choice.

## Judgment

> Recommend preserving two facts: the obligation and each recovery attempt. The second record is necessary complexity because the remote result can be unknown and later reconciliation must be auditable. A single aggregate would be smaller in count but underdesigned for ownership and recovery. Verify the local atomic command separately from remote convergence and operator handling.

Why it works: it does not equate minimality with fewer tables or records, and it keeps evidence layers separate.

## Decision Conflict

> This proposal conflicts with the accepted decision that one component owns the canonical state. Pause only the new write path. My recommendation is to preserve the decision and make the new component publish a disposable projection. If the ownership rule must change, explicitly supersede it and define migration, coexistence, and recovery before implementation handoff.

Why it works: it exposes the conflict and offers preserve, exception, or supersession semantics without silently rewriting authority.

## Handoff

> **Recommendation:** use the existing read-repair path and a bounded invalidation hint.
>
> **Decisive reasons:** it protects the same correctness invariant, avoids a new durable delivery system, and remains reversible.
>
> **Costs and residual risk:** the first read after a lost hint may be stale until the next repair trigger; the acceptable delay is an authority decision.
>
> **Verification:** prove reconstruction from authoritative facts, hint loss tolerance, and the user-visible delay at the required environment level.

Why it works: it leads with the conclusion and records only decision-relevant reasons, risks, authority, and verification.
