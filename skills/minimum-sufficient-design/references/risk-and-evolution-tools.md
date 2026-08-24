# Risk and Evolution Tools

Load this reference only for side effects, retries, unknown outcomes, concurrent writes, data migration, compatibility cutover, expensive commitments, or long-lived architecture qualities.

## Authority Before Projection

Identify the authoritative fact and its owner before designing caches, notifications, summaries, indexes, UI state, or other projections. A projection may be disposable or rebuildable; it must not overwrite authority merely because it is faster or easier to observe.

Use a stable business identity when an operation may be retried or reconciled. Transport attempts are not new business operations.

## Bound Side Effects and Recovery

For automatic side effects, decide all of the following as one recovery contract:

- which errors are retryable and which are terminal;
- which stable identity every attempt reuses;
- a count or time budget derived from the risk and dependency behavior;
- the stop condition for further side effects;
- an authoritative, read-only way to reconcile the result where available;
- an actionable terminal or human-owned state when automation ends.

Do not prescribe a universal retry count, storage design, or operational procedure. The invariant is bounded automation with convergence, not a particular mechanism.

## Preserve Unknown Outcomes

A timeout, lost response, crash, or exhausted retry budget may leave the outcome unknown. Do not collapse unknown into success or failure without authoritative evidence.

After the side-effect budget ends, stop creating effects. A low-cost read-only reconciliation path may continue within its own budget because it does not recreate the operation. Otherwise expose the unknown state for accountable handling.

## Coordinate Concurrent Facts

When multiple writers or resources can affect the same invariant, identify:

- the owner of each write;
- the atomicity boundary actually available;
- the conflict or ordering rule;
- the stable identity and deduplication semantics;
- recovery when only part of the intended outcome is observed.

Do not claim cross-resource atomicity from a local transaction or an in-memory lock.

## Delay Commitments Responsibly

For migrations, compatibility choices, expensive platforms, or hard-to-reverse interfaces, compare acting now with preserving optionality.

Delay a commitment when evidence is missing and waiting keeps safe options open. Do not delay past the point where compatibility, recovery, capacity, or delivery becomes unsafe. The last responsible moment is evidence-sensitive, not an excuse for indefinite postponement.

Prefer reversible steps and explicit cutover criteria. When coexistence adds more risk than it removes, a deliberate hard cut may be the smaller sufficient design.

## Separate Essential and Accidental Complexity

Essential complexity comes from the problem's current invariants, ownership, audit, recovery, or compatibility needs. Accidental complexity is introduced by the chosen representation or machinery without equivalent current benefit.

Place necessary complexity behind the owner that can preserve the invariant. Remove or postpone mechanisms that answer only hypothetical futures. Neither distinction alone determines sufficiency; verification and residual risk still matter.

## Add Fitness Functions Selectively

Use an automated fitness function only when an architecture quality is important over time, can be measured reliably, and is likely to drift. A focused test, metric, or policy check may then preserve the property through change.

Do not turn every judgment into a continuous gate. If measurement is noisy, the property is temporary, or human context is decisive, keep verification at the appropriate manual or release boundary.
