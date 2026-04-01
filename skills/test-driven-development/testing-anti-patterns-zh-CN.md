# 测试反模式 (Testing Anti-Patterns)

**以下场景要加载本参考：** 编写或修改测试、引入 mocks，或你开始想往生产代码里加 test-only 方法时。

## 概览 (Overview)

测试必须验证真实行为，而不是 mock 行为。Mock 的作用是隔离，不是被测试对象本身。

**核心原则：** 测代码做了什么，不测 mocks 做了什么。

**严格遵循 TDD，能自然避免这些反模式。**

## 铁律 (The Iron Laws)

```
1. NEVER test mock behavior
2. NEVER add test-only methods to production classes
3. NEVER mock without understanding dependencies
```

## 反模式 1：测的是 Mock 行为 (Testing Mock Behavior)

### 违规形式 (The violation)

断言某个 `*-mock` 元素存在，本质上只是证明 mock 没坏，并没有证明真实组件行为正确。

### 为什么错 (Why this is wrong)

- 你验证的是 mock，而不是组件
- mock 一存在测试就过，mock 一没了测试就挂
- 对真实行为没有说明力

### 修正方式 (The fix)

- 要么不要 mock，直接测真实组件
- 要么即使 mock，也要测“外层组件在该 mock 存在时的真实行为”

### Gate Function

在对任何 mock 元素断言之前，先问自己：

- 我是在测试真实行为，还是在测 mock 是否存在？

如果是后者，停下。删掉断言，或者取消 mock。

## 反模式 2：往生产代码里加 Test-Only 方法 (Test-Only Methods in Production)

### 违规形式

给生产类加一个实际上只在测试里调用的 `destroy()`、`cleanup()` 之类的方法。

### 为什么错

- 生产类被测试代码污染
- 一旦误在生产中调用，风险很高
- 违反 YAGNI 与职责分离
- 容易混淆资源生命周期和实体生命周期

### 修正方式

- 把清理逻辑移到 test utilities
- 只让生产类暴露真实生产 API

### Gate Function

在给生产类新增任何方法前，先问：

- 这个方法是不是只会在测试里被调用？
- 这个类真的拥有这个资源的生命周期吗？

任意一题回答为“不是”，就不要把方法加进生产类。

## 反模式 3：在不了解依赖时就 Mock (Mocking Without Understanding)

### 违规形式

为了“安全”或“更快”，在不了解真实依赖链的情况下直接 mock 高层方法，结果把测试真正依赖的副作用也一起 mock 掉了。

### 为什么错

- 被 mock 的方法可能带有测试依赖的副作用
- 过度 mock 会破坏真实行为
- 测试可能因为错误原因通过，或神秘失败

### 修正方式

- 先理解真实方法有哪些 side effect
- 如果测试依赖其中某些 side effect，就去 mock 更低层、更慢或更外部的部分
- 只做最小 mock

### Gate Function

在 mock 任何方法前：

1. 先停下，不要急着 mock
2. 问：真实方法有哪些 side effect？
3. 问：测试是否依赖这些 side effect？
4. 问：我真的理解这条依赖链了吗？

如果不确定，就先用真实实现跑一次，再根据观测结果做最小 mock。

## 反模式 4：不完整的 Mock (Incomplete Mocks)

### 违规形式

你只 mock 了眼前测试会用到的字段，而没有镜像真实 API 的完整结构。

### 为什么错

- Partial mocks 会隐藏结构性假设
- 下游代码可能依赖你没 mock 的字段
- 测试能过，集成时却会炸
- 会制造虚假的安全感

**铁规则：** 如果你要 mock 数据结构，就必须尽量完整地镜像真实结构，而不是只写当前断言会用到的字段。

### 修正方式

- 先查真实 API 响应结构
- 把系统可能消费到的字段都补齐
- 让 mock 与真实 schema 保持一致

## 反模式 5：把集成测试当成事后补充 (Integration Tests as Afterthought)

### 违规形式

实现完了、代码写完了、但没有任何测试，然后说“Ready for testing”。

### 为什么错

- 测试本来就是实现的一部分，不是可选补充
- 真正的 TDD 会提前把这件事卡住
- 没有测试就不能说“完成”

### 修正方式

回到 TDD：

1. 先写失败测试
2. 实现让它通过
3. 再重构
4. 然后才谈完成

## 当 Mocks 变得过于复杂时 (When Mocks Become Too Complex)

警报信号：

- mock setup 比测试逻辑还长
- 为了让测试通过你在 mock 一切
- mocks 缺少真实组件应该有的方法
- 只要 mock 一改，测试就全部碎掉

这时要反问：

- 我们真的需要 mock 吗？
- 用真实组件写集成测试，会不会反而更简单？

## TDD 如何预防这些反模式 (TDD Prevents These Anti-Patterns)

TDD 的价值在于：

1. **先写测试**：迫使你先想清楚自己到底在测什么
2. **先看见失败**：证明测试测的是现实行为，而不是 mocks
3. **最小实现**：降低 test-only 方法潜入生产代码的概率
4. **先跑真实依赖**：你会更清楚测试真正需要什么，之后再决定是否 mock

如果你最终测的是 mock 行为，通常说明你在还没看见真实失败前，就过早引入了 mock。

## 快速参考 (Quick Reference)

| 反模式（Anti-Pattern） | 修正方式（Fix） |
|--------------|-----|
| 对 mock 元素断言 | 测真实组件，或取消 mock |
| 在生产代码加 test-only 方法 | 移到 test utilities |
| 不理解依赖就 mock | 先理解依赖，再做最小 mock |
| 不完整 mock | 尽量完整镜像真实 API |
| 把测试当事后补充 | 用 TDD：测试先行 |
| mock 复杂到离谱 | 考虑直接写集成测试 |

## 红旗信号 (Red Flags)

- 断言里出现 `*-mock` 的 test ID
- 某个方法只在测试文件中被调用
- mock setup 占测试代码的一半以上
- 移除 mock 后测试就完全失效
- 你说不清为什么需要这个 mock
- “先 mock 起来更安全”

## 底线 (The Bottom Line)

**Mocks 是隔离工具，不是被测对象。**

如果 TDD 过程暴露出你测的是 mock 行为，那就已经走偏了。

修法只有两个方向：

- 改成测试真实行为
- 或重新质疑：你为什么要 mock？
