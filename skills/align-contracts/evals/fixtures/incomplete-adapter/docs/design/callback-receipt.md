# 候选设计：Callback Receipt

外部回调可能省略 `receipt_id`。

HTTP 候选合同允许省略该字段，并由服务端生成身份：

```http
POST /v1/callback-receipts
Content-Type: application/json

{}
```

Proto 候选合同要求调用方提供该字段，并拒绝字段缺失：

```proto
message CreateCallbackReceiptRequest {
  string receipt_id = 1;
}
```

没有文档说明哪一个候选合同具有决定权。项目也没有提供该功能的数据库、缓存、migration 或下游工作流约定。
