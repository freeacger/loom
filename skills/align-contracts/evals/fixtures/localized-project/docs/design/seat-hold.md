# 已接受设计：席位保留

## 共享语义

- `POST /v1/seat-holds` 创建一条席位保留。
- 请求字段为 `show_id`、`seat_id` 和 `request_id`，均为必填非空字符串。
- 相同 `request_id` 的重试返回首次请求创建的同一条席位保留；即使后续请求携带不同的 `show_id` 或 `seat_id`，也忽略后续载荷，不创建新记录、不改写既有记录。
- 同一演出席位同时最多存在一条 `ACTIVE` 记录。
- 新 `request_id` 请求仍被未到期 `ACTIVE` 记录占用的同一演出席位时，返回业务错误 `SEAT_UNAVAILABLE`，不得返回既有记录；具体 HTTP 状态码、gRPC code 和错误载荷由后续规格定义。
- 席位保留在创建后 120 秒到期；数据库记录是权威。
- 创建席位保留的事务先按 `(show_id, seat_id)` 获取 PostgreSQL 事务级 advisory lock，再将 `expires_at <= CURRENT_TIMESTAMP` 的既有 `ACTIVE` 记录更新为 `EXPIRED`，最后插入新记录；读取时同样不得把已到达 `expires_at` 的记录视为有效。
- Redis 逻辑 Key 为 `seat-hold:{hold_id}`，类型为 String，TTL 不得晚于数据库中的 `expires_at`，缓存未命中时读取数据库。

## 候选 Proto

```proto
message CreateSeatHoldRequest {
  string show_id = 1;
  string seat_id = 2;
  string request_id = 3;
}

message SeatHold {
  string hold_id = 1;
  string status = 2;
  int64 expires_at_unix = 3;
}
```

## 目标 PostgreSQL DDL

```sql
CREATE TABLE seat_hold (
    hold_id UUID PRIMARY KEY,
    show_id TEXT NOT NULL,
    seat_id TEXT NOT NULL,
    request_id TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'RELEASED', 'EXPIRED')),
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX uk_seat_hold_active
    ON seat_hold (show_id, seat_id)
    WHERE status = 'ACTIVE';
```
