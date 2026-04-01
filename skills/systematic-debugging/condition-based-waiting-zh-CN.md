# 基于条件的等待 (Condition-Based Waiting)

## 概览 (Overview)

脆弱测试（flaky tests）常常用任意延迟来猜时序，例如 `setTimeout`、`sleep`。这会制造 race condition：快机器上能过，CI 或高负载时就失败。

**核心原则：** 等待你真正关心的条件，而不是猜测“它大概要多久”。

## 何时使用 (When to Use)

**适用场景：**

- 测试里有任意延迟（`setTimeout`、`sleep`、`time.sleep()`）
- 测试很 flaky
- 测试并行跑时容易 timeout
- 需要等待异步操作完成

**不适用场景：**

- 你正在测试真正的时序行为，例如 debounce 或 throttle
- 即使使用任意 timeout，也必须说明 WHY

## 核心模式 (Core Pattern)

```typescript
// ❌ BEFORE: Guessing at timing
await new Promise(r => setTimeout(r, 50));
const result = getResult();
expect(result).toBeDefined();

// ✅ AFTER: Waiting for condition
await waitFor(() => getResult() !== undefined);
const result = getResult();
expect(result).toBeDefined();
```

## 常见模式速查 (Quick Patterns)

| 场景（Scenario） | 模式（Pattern） |
|----------|---------|
| Wait for event | `waitFor(() => events.find(e => e.type === 'DONE'))` |
| Wait for state | `waitFor(() => machine.state === 'ready')` |
| Wait for count | `waitFor(() => items.length >= 5)` |
| Wait for file | `waitFor(() => fs.existsSync(path))` |
| Complex condition | `waitFor(() => obj.ready && obj.value > 10)` |

## 实现示例 (Implementation)

通用轮询函数：

```typescript
async function waitFor<T>(
  condition: () => T | undefined | null | false,
  description: string,
  timeoutMs = 5000
): Promise<T> {
  const startTime = Date.now();

  while (true) {
    const result = condition();
    if (result) return result;

    if (Date.now() - startTime > timeoutMs) {
      throw new Error(`Timeout waiting for ${description} after ${timeoutMs}ms`);
    }

    await new Promise(r => setTimeout(r, 10)); // Poll every 10ms
  }
}
```

完整实现与领域特定 helper（例如 `waitForEvent`、`waitForEventCount`、`waitForEventMatch`）见本目录下的 `condition-based-waiting-example.ts`。

## 常见错误 (Common Mistakes)

**❌ 轮询过快：** `setTimeout(check, 1)` → 浪费 CPU  
**✅ 修正：** 每 10ms 轮询一次

**❌ 不设 timeout：** 条件永远不满足时会死循环  
**✅ 修正：** 始终带 timeout 和清晰错误信息

**❌ 使用陈旧数据：** 在循环外缓存状态  
**✅ 修正：** 在循环里重新读取最新状态

## 什么时候任意 Timeout 才是对的 (When Arbitrary Timeout IS Correct)

```typescript
// Tool ticks every 100ms - need 2 ticks to verify partial output
await waitForEvent(manager, 'TOOL_STARTED'); // First: wait for condition
await new Promise(r => setTimeout(r, 200));   // Then: wait for timed behavior
// 200ms = 2 ticks at 100ms intervals - documented and justified
```

要求：

1. 先等待触发条件出现
2. timeout 依据已知时序，而不是拍脑袋
3. 注释里说明 WHY

## 实际效果 (Real-World Impact)

来自 2025-10-03 的一次调试会话：

- 修复了 3 个文件中的 15 个 flaky tests
- 通过率从 60% 提升到 100%
- 执行时间缩短约 40%
- race condition 消失
