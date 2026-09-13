# Evaluation Fixture: Replay recovery with an unresolved authority decision

For this self-contained evaluation, this fixture is the recognized source of current evidence and the final response may report conclusions, but it cannot become an aligned target carrier while the stated decision remains open.

## Change under review

A verified partner event creates a local fulfillment record and requests an allocation from an external ledger.

## Accepted decisions

- Replaying the same signed event is the only recovery trigger.
- There is no worker, scheduler, periodic scan, or automatic retry outside event handling.
- Every replay revalidates the event and current business facts.
- The ledger call may time out after the ledger accepted the request.
- The ledger deduplicates by a caller-supplied `request_id` and returns the same success for an accepted duplicate.
- A ledger entry is located by `(entry_id, entry_created_at)`; neither value alone is sufficient.
- Legacy rows without a stable ledger request identity must not be replayed automatically.

## Unresolved decision

When a previous ledger result is unknown but current business validation now fails, authority has not decided whether processing must stop or whether the original `request_id` may still be submitted to recover a possibly accepted result. Either answer changes recovery behavior and persistence conclusions.

## Candidate handler

```go
func (s *Service) HandleAccepted(ctx context.Context, event Event) error {
	record, err := s.repo.InsertIfAbsent(ctx, event.ID)
	if err != nil {
		return err
	}

	requestID := uuid.NewString()
	entry, err := s.ledger.Allocate(ctx, requestID, event.Amount)
	if err != nil {
		return err
	}

	return s.repo.MarkCompleted(ctx, record.ID, entry.ID)
}
```
On replay, `InsertIfAbsent` returns a duplicate-record error and processing stops.

## Candidate Proto

```proto
message AllocateRequest {
  string request_id = 1;
  int64 amount = 2;
}

message AllocateResponse {
  string entry_id = 1;
  int64 entry_created_at_unix = 2;
}
```

## Candidate DDL inherited from an earlier worker design

```sql
CREATE TABLE partner_fulfillment (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    partner_event_id VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL,
    ledger_entry_id VARCHAR(128) NULL,
    retry_count INT UNSIGNED NOT NULL DEFAULT 0,
    next_retry_at DATETIME(3) NULL,
    last_error VARCHAR(512) NULL,
    created_at DATETIME(3) NOT NULL,
    updated_at DATETIME(3) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_partner_event_id (partner_event_id),
    KEY idx_retry_scan (status, next_retry_at)
);
```
