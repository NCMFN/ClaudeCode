---
paths:
  - "**/*.cpp"
  - "**/*.hpp"
  - "**/*.cc"
  - "**/*.hh"
  - "**/*.cxx"
  - "**/*.h"
  - "**/CMakeLists.txt"
---

# C++ 模式

> 本文档扩展了 [common/patterns.md](../common/patterns.md) 中与 C++ 相关的内容。

## RAII (资源获取即初始化)

将资源生命周期与对象生命周期绑定：

```cpp
class FileHandle {
public:
    explicit FileHandle(const std::string& path) : file_(std::fopen(path.c_str(), "r")) {}
    ~FileHandle() { if (file_) std::fclose(file_); }
    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;
private:
    std::FILE* file_;
};
```

## 三五法则/零法则

* **零法则**：优先使用无需自定义析构函数、拷贝/移动构造函数或赋值运算符的类
* **三五法则**：如果定义了析构函数、拷贝构造函数、拷贝赋值运算符、移动构造函数或移动赋值运算符中的任何一个，则应定义全部五个

## 值语义

* 小型/平凡类型按值传递
* 大型类型通过 `const&` 传递
* 按值返回（依赖 RVO/NRVO）
* 对于接收后即被消耗的参数，使用移动语义

## 错误处理

* 对于异常情况，使用异常
* 对于可能不存在的值，使用 `std::optional`
* 对于可预期的失败，使用 `std::expected`（C++23）或结果类型

## 参考

有关全面的 C++ 模式和反模式，请参阅技能：`cpp-coding-standards`。
