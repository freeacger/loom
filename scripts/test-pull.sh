#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
fixture_dir=$(mktemp -d)
trap 'rm -rf "$fixture_dir"' EXIT

mkdir -p "$fixture_dir/bin" "$fixture_dir/home"
cat > "$fixture_dir/bin/npx" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$@" > "$CAPTURE_PATH"
EOF
chmod +x "$fixture_dir/bin/npx"

CAPTURE_PATH="$fixture_dir/args" HOME="$fixture_dir/home" PATH="$fixture_dir/bin:$PATH" \
  bash "$repo_root/mise/tasks/pull" > /dev/null

expected=$(cat <<'EOF'
skills
add
freeacger/loom
-y
-g
-a
codex
-a
claude-code
EOF
)
actual=$(cat "$fixture_dir/args")

if [ "$actual" != "$expected" ]; then
  printf 'expected explicit Codex and Claude Code targets, got:\n%s\n' "$actual" >&2
  exit 1
fi

echo "✓ pull targets Codex and Claude Code explicitly"
