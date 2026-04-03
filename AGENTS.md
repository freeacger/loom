## Rules

- **Single source of truth**: `skills/<name>/SKILL.md` is canonical. Never edit `~/.claude/skills/`, `~/.agents/skills/`, or any other install path directly.
- **Eval from repo path**: When running skill-creator evals, always point at `skills/<name>`, not the install path.
- **Publish before pull**: Push to GitHub first (skills.sh auto-discovers), then run `mise run pull` to update install paths.
- **Never run `npx skills add` directly in this repo** — the CLI replaces `skills/` directories with symlinks. Always use `mise run pull`.
- **Commit before publishing**: Never publish uncommitted changes.
- **Separate protocol from presentation**: Keep `skills/<name>/SKILL.md` field names and enum literals canonical for protocol stability. Do not hardcode bilingual headings into the canonical English template. If bilingual labels improve Chinese responses, treat them as a rendering rule for Chinese output and preserve the English literals as protocol anchors.

## Docs Conventions

- `docs/README.md` is the source of truth for docs directory layout and naming.
- Workflow, guide, standard, and methodology documents use stable `kebab-case.md` names without dates.
- Time-bound artifacts such as reports, design decisions, and execution plans use `YYYY-MM-DD-<topic>.md`.
- Do not create vague names such as `TODO.md` or `workflow.md` under `docs/`.

## Skill Development Workflow
@docs/workflows/skill-development.md
