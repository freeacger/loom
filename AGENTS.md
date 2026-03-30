## Rules

- **Single source of truth**: `skills/<name>/SKILL.md` is canonical. Never edit `~/.claude/skills/`, `~/.agents/skills/`, or any other install path directly.
- **Eval from repo path**: When running skill-creator evals, always point at `skills/<name>`, not the install path.
- **Publish before pull**: Push to GitHub first (skills.sh auto-discovers), then run `mise run pull` to update install paths.
- **Never run `npx skills add` directly in this repo** — the CLI replaces `skills/` directories with symlinks. Always use `mise run pull`.
- **Commit before publishing**: Never publish uncommitted changes.

## Skill Development Workflow
@docs/workflows/skill-development.md