---
paths:
  - "**/*.py"
  - "**/*.pyi"
---
# Python Coding Style

> This file extends [common/coding-style.md](../common/coding-style.md) with Python specific content.

## Standards

- Follow **PEP 8** conventions
- Use **type annotations** on all function signatures

## Immutability

Prefer immutable data structures:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    name: str
    email: str

from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float
```

## Formatting

- **black** for code formatting
- **isort** for import sorting
- **ruff** for linting

## Docstrings

Use **Google-style** docstrings for all public classes and functions.

### Structure

```python
def process_items(
    items: list[str],
    max_results: int | None = None,
    include_metadata: bool = False,
) -> list[dict[str, Any]]:
    """Process a list of items and return structured results.

    Processes each item through the pipeline, optionally filtering to a
    maximum number of results and attaching metadata.

    Args:
        items: Raw input items to process.
        max_results: Maximum number of results to return, or None for all.
        include_metadata: Whether to attach processing metadata to each result.

    Returns:
        A list of processed result dictionaries. Each dict contains at least
        'id' and 'value' keys.

    Raises:
        ValueError: If items is empty.
        ProcessingError: If the pipeline fails on any item.

    Examples:
        >>> process_items(["a", "b", "c"], max_results=2)
        [{'id': 'a', 'value': 'processed-a'}, {'id': 'b', 'value': 'processed-b'}]
    """
    if not items:
        raise ValueError("items must not be empty")
    ...
```

### Rules

- **One-line docstrings** for trivial functions:
  ```python
  def get_count(self) -> int:
      """Return the current count."""
      return self._count
  ```

- Use past tense for `Returns:` ("Returns a list of..." not "Return a list")
- `Args:` always first among the metadata sections
- List parameters in the order they appear in the signature
- No docstring for `__init__` unless initialization has non-obvious side effects
- Private/internal functions (starting with `_`) still need docstrings for clarity

### Types in Docstrings

Use plain English type names, not Python type expressions:

| Parameter Type | Write | Don't Write |
|----------------|-------|------------|
| `str` | `str` | `typing.Str` |
| `list[str]` | `list[str]` | `List[str]` (Python 3.9+ native syntax preferred) |
| `dict[str, int]` | `dict[str, int]` | `Dict[str, int]` |
| `int \| None` | `int or None` | `Optional[int]` |
| custom class | the class name | `MyClass` (just write the name) |

## Reference

See skill: `python-patterns` for comprehensive Python idioms and patterns.
