---
paths:
  - "**/*.java"
---

# Java 编码风格

> 本文档在 [common/coding-style.md](../common/coding-style.md) 的基础上扩展了 Java 相关的内容。

## 格式

* 使用 **google-java-format** 或 **Checkstyle**（Google 或 Sun 风格）进行强制规范
* 每个文件只包含一个公共顶级类型
* 保持一致的缩进：2 或 4 个空格（与项目标准保持一致）
* 成员顺序：常量、字段、构造函数、公共方法、受保护方法、私有方法

## 不可变性

* 对于值类型，优先使用 `record`（Java 16+）
* 默认将字段标记为 `final` — 仅在必需时使用可变状态
* 从公共 API 返回防御性副本：`List.copyOf()`、`Map.copyOf()`、`Set.copyOf()`
* 写时复制：返回新实例而非修改现有实例

```java
// GOOD — immutable value type
public record OrderSummary(Long id, String customerName, BigDecimal total) {}

// GOOD — final fields, no setters
public class Order {
    private final Long id;
    private final List<LineItem> items;

    public List<LineItem> getItems() {
        return List.copyOf(items);
    }
}
```

## 命名

遵循标准的 Java 约定：

* 类、接口、记录、枚举使用 `PascalCase`
* 方法、字段、参数、局部变量使用 `camelCase`
* `static final` 常量使用 `SCREAMING_SNAKE_CASE`
* 包名：全小写，反向域名（`com.example.app.service`）

## 现代 Java 特性

在能提高代码清晰度的地方使用现代语言特性：

* **记录** 用于 DTO 和值类型（Java 16+）
* **密封类** 用于封闭的类型层次结构（Java 17+）
* 使用 `instanceof` 进行**模式匹配** — 避免显式类型转换（Java 16+）
* **文本块** 用于多行字符串 — SQL、JSON 模板（Java 15+）
* 使用箭头语法的**Switch 表达式**（Java 14+）
* **Switch 中的模式匹配** — 对密封类型进行穷尽处理（Java 21+）

```java
// Pattern matching instanceof
if (shape instanceof Circle c) {
    return Math.PI * c.radius() * c.radius();
}

// Sealed type hierarchy
public sealed interface PaymentMethod permits CreditCard, BankTransfer, Wallet {}

// Switch expression
String label = switch (status) {
    case ACTIVE -> "Active";
    case SUSPENDED -> "Suspended";
    case CLOSED -> "Closed";
};
```

## Optional 的使用

* 从可能没有结果的查找方法返回 `Optional<T>`
* 使用 `map()`、`flatMap()`、`orElseThrow()` — 绝不直接调用 `get()` 而不先检查 `isPresent()`
* 绝不使用 `Optional` 作为字段类型或方法参数

```java
// GOOD
return repository.findById(id)
    .map(ResponseDto::from)
    .orElseThrow(() -> new OrderNotFoundException(id));

// BAD — Optional as parameter
public void process(Optional<String> name) {}
```

## 错误处理

* 对于领域错误，优先使用非受检异常
* 创建继承自 `RuntimeException` 的领域特定异常
* 避免宽泛的 `catch (Exception e)`，除非在顶级处理器中
* 在异常消息中包含上下文信息

```java
public class OrderNotFoundException extends RuntimeException {
    public OrderNotFoundException(Long id) {
        super("Order not found: id=" + id);
    }
}
```

## 流

* 使用流进行转换；保持流水线简短（最多 3-4 个操作）
* 在可读的情况下优先使用方法引用：`.map(Order::getTotal)`
* 避免在流操作中产生副作用
* 对于复杂逻辑，优先使用循环而非难以理解的流式管道

## 参考

完整编码标准及示例请参见技能：`java-coding-standards`。
JPA/Hibernate 实体设计模式请参见技能：`jpa-patterns`。
