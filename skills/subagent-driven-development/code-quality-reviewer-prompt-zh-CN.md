# 代码质量 Reviewer Prompt 模板 (Code Quality Reviewer Prompt Template)

在分发代码质量 reviewer subagent 时使用这个模板。

**Purpose：** 验证实现是否构建得足够好（clean、tested、maintainable）

**只有在 spec compliance review 通过之后，才能分发。**

```
Task tool (loom:code-reviewer):
  Use template at requesting-code-review/code-reviewer.md

  WHAT_WAS_IMPLEMENTED: [from implementer's report]
  PLAN_OR_REQUIREMENTS: Task N from [plan-file]
  BASE_SHA: [commit before task]
  HEAD_SHA: [current commit]
  DESCRIPTION: [task summary]
```

**Code reviewer 返回内容：** Strengths、Issues（Critical/Important/Minor）、Assessment
