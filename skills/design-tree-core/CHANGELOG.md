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
