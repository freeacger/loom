# Evaluation Fixture: Saved default and immutable operation target

For this self-contained evaluation, this fixture is the recognized source of current evidence and the final response is the recognized target-design carrier.

## Change request

The existing create-operation API requires a delivery target. Add a saved default so newer callers may omit the target. Existing callers that provide a target must behave unchanged.

## Accepted decisions

- A user may save one default per target type.
- Different users may use the same target; a target is not proof of account ownership.
- An explicitly supplied target takes precedence.
- A missing target uses the saved default required by the selected item.
- An explicit empty target and a missing default both preserve the existing `TARGET_REQUIRED` failure.
- Saving an empty value is invalid and is not deletion.
- Operation details return the target accepted when the operation was submitted, even if the saved default or item configuration changes later.

```go
type ItemConfig struct {
	ID                 string
	RequiredTargetType string
}
```

## Current and candidate HTTP

```http
POST /v1/operations
Content-Type: application/json

{
  "item_id": "item-001",
  "target": "reader@example.test"
}
```

```http
PUT /v1/profile/default-target
Content-Type: application/json

{
  "type": "email",
  "value": "reader@example.test"
}
```

## Candidate Proto

```proto
message CreateOperationRequest {
  string item_id = 1;
  string target = 2;
}

message Operation {
  string operation_id = 1;
  string target = 2;
}
```

## Candidate DDL

```sql
CREATE TABLE user_default_target (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    target_type VARCHAR(32) NOT NULL,
    target_value VARCHAR(255) NOT NULL,
    created_at DATETIME(3) NOT NULL,
    updated_at DATETIME(3) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_target_value (target_value)
);

CREATE TABLE user_operation (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    item_id VARCHAR(64) NOT NULL,
    created_at DATETIME(3) NOT NULL,
    updated_at DATETIME(3) NOT NULL,
    PRIMARY KEY (id)
);
```

## Current read behavior

```go
func (s *OperationService) GetOperationTarget(
	ctx context.Context,
	operation *Operation,
) (string, error) {
	return s.defaultTargetRepo.GetByUserAndType(
		ctx,
		operation.UserID,
		s.itemConfig.RequiredTargetType(operation.ItemID),
	)
}
```

## Migration evidence

Every existing operation has exactly one authoritative row in `operation_target_audit`, keyed by operation ID, containing the originally accepted target. The migration may backfill `user_operation.target_value` from that source before enforcing `NOT NULL`. No existing operation lacks an audit row.
