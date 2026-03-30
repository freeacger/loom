# 技能文件中英文替换 设计树

## 问题
`skills/` 目录下有 7 个非 eval 文件包含中文内容，涉及 3 个技能。这些技能作为公开资产发布，应保持 English-only。中文内容包括章节标题、模板标签、示例提示词和完整的 agent 提示词。

## 范围
### 包含
- `skills/design-structure/SKILL.md` — 约 47 行中文标签和模板示例
- `skills/design-decision-audit/SKILL.md` — 约 30 行中文字段名和描述
- `skills/design-decision-audit/agents/module-auditor.md` — 约 50 行，完整中文 agent prompt
- `skills/design-readiness-check/agents/assumption-checker.md` — 约 60 行，完整中文 agent prompt
- `skills/design-readiness-check/agents/failure-checker.md` — 约 60 行，完整中文 agent prompt
- `skills/design-readiness-check/agents/risk-checker.md` — 约 60 行，完整中文 agent prompt
- `skills/design-readiness-check/agents/branch-checker.md` — 约 45 行，完整中文 agent prompt

### 不包含
- `skills/*/evals/` — eval 中的中文提示词允许保留
- `docs/TODO.md` — 不在范围
- `docs/design-decisions/2026-03-30-...md` — 不在范围
- `docs/workflows/skill-development.md` — 不在范围

## 假设
- 替换为纯语言翻译，不改变功能逻辑或工作流步骤
- 英文术语沿用代码库中的现有命名惯例（如 `design_tree`、`open_branches`、`decision_nodes`）
- 模板示例中的中文（如"API 网关"）替换为同等表达力的英文示例
- 无需更新 CHANGELOG——视为 bugfix 级别的语言修正
- AGENTS.md 中的中文规则（代码注释用中文）仍然适用——约束的是代码注释，不约束技能文件

## 设计树

```
design_tree
├── 1. 替换策略
│   ├── 1.1 分类 ✓
│   │   ├── A. 内联标签与标题（如 问题→Problem）
│   │   ├── B. 模板示例（如 API网关 示例）
│   │   └── C. 完整 agent prompt（整文件重写）
│   ├── 1.2 翻译原则 ✓
│   │   ├── 保持结构和编号不变
│   │   ├── 使用行业通用术语
│   │   └── 仅在需要处保留双语括注
│   └── 1.3 验证方法 ✓
│       └── 编辑完成后重新扫描 CJK 字符
├── 2. 执行顺序
│   ├── 2.1 SKILL.md 文件（2 个）✓
│   │   ├── design-structure/SKILL.md
│   │   └── design-decision-audit/SKILL.md
│   └── 2.2 Agent prompt 文件（5 个）✓
│       ├── design-decision-audit/agents/module-auditor.md
│       └── design-readiness-check/agents/（4 个文件）
├── 3. 质量关卡
│   ├── 3.1 非 eval 文件零 CJK ✓
│   ├── 3.2 语义保真度检查 ✓
│   └── 3.3 mise run check 通过 ✓
└── 4. 交付
    └── 4.1 提交并发布 ✓
```

## 开放分支
无——所有分支已执行完毕。

## 决策节点
无——任务为纯翻译，无架构选择。

## 决策
无需额外决策。已完成语言策略（Language Strategy）的补充：design-structure/SKILL.md 现在会根据用户输入语言自动适配输出文件的语言。
