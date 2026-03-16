@docs/workflows/skill-development.md

## Rules

- **Single source of truth**: `skills/<name>/SKILL.md` is canonical. Never edit `~/.claude/skills/`, `~/.agents/skills/`, or any other install path directly.
- **Eval from repo path**: When running skill-creator evals, always point at `skills/<name>`, not the installed path.
- **Keep install paths in sync**: After editing `skills/<name>/SKILL.md`, sync to both `~/.claude/skills/<name>` and `~/.agents/skills/<name>`.
- **Commit before publishing**: Push to GitHub first; skills.sh auto-discovers from the repo.
