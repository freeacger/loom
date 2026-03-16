# TODO

## 技能触发率优化 (Skill Triggering Rate)

**问题：** brainstorming 在 Claude Code 中触发不稳定，在 Codex 中可以稳定触发。

**根因分析：**
- 根本原因：`using-superpowers` 在 Claude Code 中未被稳定触发，导致技能守卫失效
- Claude 对泛化指令（如 `"Use when starting any conversation"`）的遵守不如 Codex 字面

**建议方案：**
使用 skill-creator 插件的 `improve_description.py` 脚本，对 `using-superpowers` 和 `brainstorming` 的 description 做自动优化，提升触发准确率。

**参考：**
- skill-creator 脚本路径：`~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/improve_description.py`
- 相关讨论：2026-03-16 brainstorming 技能改进会话
