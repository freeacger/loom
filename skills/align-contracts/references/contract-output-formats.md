# Contract Output Formats

Read this reference only when presenting contract changes or a cross-surface conflict.

## Choose the smallest useful view

Use a sentence for one fact, a table for repeated mappings, a small diagram for relationships or sequence, a diff for changes to an existing artifact, and a complete block when the target must be copied or implemented as a whole.

Lead with the status and conclusion. Put the visual beside the claim it explains. Omit empty sections and decorative diagrams.

## Result presentation

Use one localized language for headings and prose. The internal states `ALIGNED`, `BLOCKED`, and `NO_CONTRACT_CHANGE` select the presentation branch; they are not mandatory visible labels.

```markdown
## <Localized aligned heading>

<One-sentence conclusion.>

| <Localized label> | <Localized result> |
|---|---|
| <Scope> | <Named scope> |
| <Carrier> | `<real path>` |
| <Next action> | `to-spec` |
```

Use the table only when at least two facts benefit from repeated alignment. A blocked result uses localized sections for the unresolved issue, impact, and next action. A no-change result uses one localized heading and one short paragraph.

## Surface summary

Summarize applicable surfaces before detailed changes:

| Surface | Current conflict | Target conclusion | Authority |
|---|---|---|---|
| HTTP | Omission is not defined | Omission uses the saved default | API design |
| Proto | Scalar loses presence | Preserve field presence | Proto target diff |
| SQL | Operation has no snapshot | Persist the resolved value | Target DDL |

Use `Not Applicable` only for a surface that was considered and is genuinely outside the scoped change. When the project supplies no evidence or convention, report the evidence gap instead.

## HTTP

Use Markdown tables for endpoints, fields, and errors. Show a compact request or response example only when it removes ambiguity.

| Field | Location | Required | Semantics |
|---|---|---:|---|
| `target` | Body | No | Missing uses the saved default; an empty value is invalid. |

Record method and path, authentication or caller scope when relevant, presence and nullability, defaults and precedence, validation, errors, compatibility, and idempotency. Do not invent exact status codes or field limits when authority is missing.

## gRPC and Proto

Show modifications as a Proto diff with enough surrounding message or service context to make field numbers and ownership clear:

```diff
 message CreateOperationRequest {
   string item_id = 1;
-  string target = 2;
+  optional string target = 2;
 }
```

Keep existing field numbers stable. State presence, compatibility, reserved fields, error mapping, and streaming behavior only when applicable.

When most of a new file is required for implementation, show the complete target Proto instead of a fragmented diff.

## SQL and DDL

First summarize the relational meaning:

| Constraint | Target meaning |
|---|---|
| `UNIQUE (user_id, target_type)` | One saved default per user and type |
| `target_value NOT NULL` | An accepted operation keeps an immutable target snapshot |

Then show complete target DDL for every changed table. Include columns, types, nullability, defaults, primary and unique keys, indexes, and table options only when the governing dialect or project policy establishes them.

```sql
CREATE TABLE user_operation (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    item_id VARCHAR(64) NOT NULL,
    target_value VARCHAR(255) NOT NULL,
    created_at DATETIME(3) NOT NULL,
    updated_at DATETIME(3) NOT NULL,
    PRIMARY KEY (id)
);
```

Separate target DDL from migration execution. State backfill, coexistence, cutover, verification, and rollback obligations when existing data or consumers make them relevant. `ALIGNED` freezes the target design; it does not claim that a migration ran.

## Redis and caches

Prefer a table over repeating prose:

| Logical key | Type | TTL | Authority | Invalidation / failure behavior |
|---|---|---:|---|---|
| `availability:{id}` | String | Project-defined | Database record | Delete after authoritative write; a miss reloads authority. |

Follow project policy on whether the shared physical prefix appears in a feature result. When policy says feature documents use logical keys only, omit the physical prefix entirely. Otherwise name a declared prefix once and show the complete physical key only when the prefix is part of the decision. Never guess an undeclared prefix.

For local caches, also state process scope and restart behavior. A cache is a projection, not a new authority unless an accepted decision says otherwise.

## Events and messages

Use a schema diff or field table, then state the behavioral contract:

| Concern | Contract |
|---|---|
| Identity | Stable business event ID |
| Ordering | Per-entity order, when required |
| Replay | Duplicate delivery reuses the same business identity |
| Compatibility | Additive evolution unless an accepted cutover says otherwise |

Include producer, consumer, delivery guarantee, deduplication, ordering, retry, dead-letter, and schema evolution only when those concerns are applicable.

## Code behavior

Use a focused diff for the seam where authority, precedence, snapshotting, or recovery changes. Code illustrates the target behavior; it does not replace the contract conclusion.

## Blockers

Show a small branch when the unresolved choice changes multiple surfaces:

```text
external result is unknown
          │
    ┌─────┴─────┐
    ▼           ▼
stop recovery   reuse stable request identity
    │           │
unresolved      may recover the accepted result
history         or cause the first effect
```

Follow it with one explicit question, affected surfaces, required authority update, and `next: grill-with-docs`.

## Localization

Keep protocol anchors and enum literals in English. Render headings, explanations, and table labels in the project's language. Prefer domain vocabulary from the project glossary over generic synonyms.
