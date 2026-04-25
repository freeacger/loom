# Changelog

## v0.5.0 — Two-Tier Rendering and Task Directory Creation

- Replaces the `Output: Task Brief` section with explicit render rules: no outer code block, two-tier visual layout (TL;DR upper / context lower) separated by a `---` divider, `User Goal` as a quote-block bolded sentence, `❓` prefix on `Clarifying Question`
- Drops default rendering of `Task Type` (kept in protocol as a stable anchor)
- Replaces literal `Needs Design: yes/no` with a natural-language `Recommended next:` sentence (proceed / enter design stage with reason / pause for clarification)
- Flattens `Constraints` to a flat bulleted list; `Scope` / `Format` / `Risk` / `Other` sub-categories are no longer required
- Empty fields are omitted entirely rather than rendered with placeholders
- Adopts the role of **sole creation entry point** for `.agents/tasks/<task-id>/`: defines when to propose creation, the confirmation gate, the Hybrid slug strategy (proposed-from-goal, user override wins), and the atomic creation steps that pair `brief.md` with the first `task_created:` journal entry
- Updates all five examples to the new rendering
- Adds 4 new behavior cases (12–15) covering rendering, confirmation gate, slug hybrid, and atomic creation; existing trigger / anti-trigger cases preserved as regression coverage

## v0.4.0 - Scope Contraction

- Removes `Execution Mode`, including `structured-handoff` and `decompose`
- Removes `Core Questions`, `Sub-Tasks`, and DAG output guidance
- Adds `Clarifying Question` and `Needs Design` to the brief protocol
- Reorders the output for faster scanning
- Clarifies rendering rules: English canonical template, bilingual headings only for Chinese responses
- Removes default codebase-search guidance from the skill boundary
- Updates examples and evals to match the narrowed task-brief scope

## v0.3.0 — Diagram Conventions

- Adds character DAG diagram rules for decompose mode (3+ sub-tasks with dependencies)
- DAG uses `[brackets]` for components, `──→` for arrows, max width 78 chars

## v0.2.0 — Goal Validation

- Adds "Inaccurate goal" as a third Tier 2 sub-case alongside "Missing parameter" and "Ambiguous intent"
- Detects three goal inaccuracy signals: solution-as-goal, symptom-as-goal, scope anomaly
- Adds Example 5 demonstrating solution-as-goal detection and reframing
- Adds goal-honest acceptance criterion (criterion 6)
- Adds goal validation conversion rule to Compression Rules
- Updates Tier 2 signal description in complexity tiers table
- Adds 2 new evals covering solution-as-goal and symptom-as-goal scenarios
- Adds guidance to search codebase before writing brief when goal validation signals fire

## v0.1.0 — Initial version

- Initial skill draft
- Defines 3-tier complexity model (direct / clarify / structured)
- Establishes model-agnostic Task Brief output protocol (8 fields)
- Includes 3 worked examples across complexity tiers
- Defines compression rules and execution mode decision table
