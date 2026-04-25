# Changelog

## v0.1.0 — Initial Release

- Replaces the retired `task-state-management` skill with an append-only journal convention.
- Defines the data layout: `<repo>/.agents/tasks/<task-id>/{brief.md, journal.md, artifacts/}` with a flat layout (no `active/`/`completed/` partitions) and a `.current` pointer for active task id propagation.
- Establishes the task id format `YYYY-MM-DD-<slug>-<rand>` with a 2-character hex random suffix.
- Defines the journal entry format `## <ISO8601> — <skill>` followed by `key: value` lines and an optional ≤ 15-line body.
- Reserves five core keys: `saved`, `decision`, `readiness` (`ready`/`not-ready`), `blocker`, `done`.
- Records brief immutability after the first journal entry; goal drift is captured as a `refined:` entry instead.
- Defines completion semantics: only code tasks get `done:` entries; the directory is never moved or archived.
- Publishes a tier table for which skills append (A/B/C) and which never do (D).
- Bundles two stdlib-only helpers under `scripts/`:
  - `journal.py append|read` — convenience helper for appending and reading entries.
  - `lint_tasks.py` — drift checker that reports `error` (corrupt heading, missing/empty reserved key value, malformed `readiness:` value, unparseable timestamp, missing `brief.md`) and `warn` (body > 15 lines, post-`done` reopen, missing `journal.md`); supports `--strict`.
- Documents seven explicit upgrade signals and a meta-gate requiring any "add the state machine back" PR to cite an observed signal.
