#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

cd "$repo_root"

if ! command -v skills-ref >/dev/null 2>&1; then
  echo "✗ 未找到 skills-ref。"
  echo "  请先安装 Agent Skills 参考校验器后再运行此命令。"
  echo "  参考文档：https://agentskills.io/specification"
  exit 1
fi

targets=(
  "skills/design-decision-audit"
  "skills/task-brief"
)

fail=0

echo "→ 运行 Agent Skills 规范校验（试点目录）..."
for target in "${targets[@]}"; do
  echo "  → $target"
  if skills-ref validate "$target"; then
    echo "    ✓ 通过"
  else
    echo "    ✗ 失败"
    fail=1
  fi
done

if [ "$fail" -ne 0 ]; then
  echo "✗ Agent Skills 规范校验未通过"
  exit 1
fi

echo "✓ Agent Skills 规范校验通过"
