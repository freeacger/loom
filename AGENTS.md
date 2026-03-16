@docs/workflows/skill-development.md

## Rules

- **Single source of truth**: `skills/<name>/SKILL.md` is canonical. Never edit `~/.claude/skills/`, `~/.agents/skills/`, or any other install path directly.
- **Eval from repo path**: When running skill-creator evals, always point at `skills/<name>`, not the install path.
- **Publish before pull**: Push to GitHub first (skills.sh auto-discovers), then run `npx skills add` to update install paths.
- **Commit before publishing**: Never publish uncommitted changes.
