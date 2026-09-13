# Evaluation Fixture: Internal helper refactor

For this self-contained evaluation, the final response is the recognized result carrier.

Rename the private helper `normalizeTarget` to `canonicalizeTarget` and move it from `handler_helpers.go` to `target_helpers.go`.

The helper remains package-private. Its implementation, inputs, outputs, validation behavior, errors, call sites, request and response types, persistent data, caches, concurrency, and runtime configuration do not change. Existing behavior tests remain unchanged.

```diff
-func normalizeTarget(value string) (string, error) {
+func canonicalizeTarget(value string) (string, error) {
   normalized := strings.TrimSpace(value)
   if normalized == "" {
     return "", ErrTargetRequired
   }
   return normalized, nil
 }
```
