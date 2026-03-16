@docs/workflows/skill-development.md

## Rules

- **Single source of truth**: `skills/<name>/SKILL.md` is canonical. Never edit `~/.claude/skills/`, `~/.agents/skills/`, or any other install path directly.
- **Eval from repo path**: When running skill-creator evals, always point at `skills/<name>`, not the installed path.
- **Sync after every change**: After editing, sync to both install paths before committing.
- **Commit before publishing**: Push to GitHub first; skills.sh auto-discovers from the repo.
