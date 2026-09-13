# 合同对齐规则

## 结果载体

席位保留的结果写入 `docs/contract-freeze/seat-hold.md`。该文档保存跨合同结论，不替代各原生合同文件。

## 权威映射

| 关注点 | 语义权威 | 原生表示 |
|---|---|---|
| 领域术语和业务不变量 | `CONTEXT.md` 与已接受设计 | 项目设计文档 |
| HTTP | 已接受设计 | OpenAPI 目标变更 |
| gRPC | 已接受设计 | Proto 目标变更 |
| 持久化 | 已接受设计 | PostgreSQL migration |
| 缓存 | 数据库事实 | Redis 投影约定 |

## 当前态与目标态

对齐文档必须标明候选表示和目标合同。`ALIGNED` 只证明目标设计一致，不表示代码或 migration 已完成。

## 本地化与呈现

- 标题、说明和表头使用简体中文。
- 面向人的结果不附加英文状态标签；字段名、枚举值和工作流名称等技术标识保持原文。
- 使用 PostgreSQL 16 DDL；不得采用 MySQL 专用语法。
- Redis 公共物理前缀为 `theater:{environment}:`，功能文档只写逻辑 Key。

## 下游交接

对齐成功后使用 `next: to-spec`。
