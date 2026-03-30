# 文档目录规范 (Docs Directory Conventions)

## 目标与原则 (Goals and Principles)

本文档是 `docs/` 目录结构与命名规则的唯一详细来源（single source of truth）。新增文档时，先根据文档性质选择目录，再按命名规则落盘，避免出现同类文档分散、文件名含义模糊的问题。

## 目录用途 (Directory Purposes)

- `docs/workflows/`
  - 存放工作流（workflow）、操作指南（guide）、方法论（methodology）等稳定参考文档
- `docs/standards/`
  - 存放标准（standards）、规范（conventions）、风格指南（style guide）等约束性文档
- `docs/design-decisions/`
  - 存放设计决策记录（design decisions / ADR-like records）
- `docs/design-tree/`
  - 存放设计树（design tree）与设计阶段分析产物
- `docs/reports/`
  - 存放调研报告（report）、审计报告（audit report）、对比分析（comparison analysis）等时效性输出
- `docs/exec-plans/active/`
  - 存放待执行的实施计划（active execution plans）
- `docs/exec-plans/completed/`
  - 存放已完成的实施计划（completed execution plans）

## 命名规则 (Naming Rules)

- 稳定参考文档使用不带日期的 `kebab-case.md`
  - 适用于 workflow、guide、standard、methodology、style guide
- 时效性产物使用 `YYYY-MM-DD-<topic>.md`
  - 适用于 report、design decision、execution plan、阶段性分析
- 文件名必须直接表达内容，不使用模糊名称
  - 禁止新增 `TODO.md`、`workflow.md`、`notes.md` 这类泛名文件

## 落点约定 (Placement Rules)

- 描述“怎么做”的文档优先放 `docs/workflows/`
- 描述“必须遵守什么”的文档优先放 `docs/standards/`
- 描述“为什么这样选”的文档优先放 `docs/design-decisions/`
- 描述“分析过程或阶段性产出”的文档放 `docs/design-tree/` 或 `docs/reports/`
- 如果文档是为某次具体工作生成，且会随时间失效，优先使用带日期的命名

## 维护要求 (Maintenance Rules)

- 重命名或移动 `docs/` 下文档时，必须同步更新仓库内引用
- 新增目录前，先确认现有目录是否已经覆盖该文档类型
- 若规则变更，优先更新本文档，再视需要补充 `AGENTS.md` 中的摘要约束
