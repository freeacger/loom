# Changelog

## v0.1.0 — Initial version

- Introduces `design-tree-core` as a shared governance core for the design-tree skill family
- Defines admission, eviction, derivation, and anti-bloat rules for shared design-tree behavior
- Adds a runtime-published `REFERENCE.md` so shared rules can ship through GitHub and skills.sh

## v0.2.0 — Breaking contract rollout

- Makes `design_target_type` a required shared `design_state` field
- Defines shared target-type vocabulary: `system`, `workflow`, `methodology`, `framework`
- Moves the family to a pure `design_state` output contract
- Clarifies that default file persistence is not a shared design-tree behavior
- Adds target-type-specific completion standards for design refinement and readiness

## v0.3.0 — Derivation decision standard

- Replaces the old five-question derivation heuristic with a formal gate-based derivation standard
- Requires all hard gates to pass before derivation is allowed
- Requires at least 2 of 3 supporting signals before deriving a new tree
- Explicitly rejects weighted or additive scoring as a shared derivation model
