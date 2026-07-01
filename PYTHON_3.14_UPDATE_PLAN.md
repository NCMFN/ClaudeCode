# Python 3.14 Update Plan for ECC Vendored Snapshot

**Status:** Pre-implementation scan  
**Target:** Python 3.14.6 (latest stable, June 2026)  
**Out of Scope:** Python 3.15 (pre-release/alpha, planned October 2026)  
**Branch:** ecc-sync-v2.0.0  

---

## 📋 Python-Related Files Identified

### 1. **Skills** (5 primary)
```
skills/python-patterns/SKILL.md
skills/python-testing/SKILL.md
skills/django-patterns/SKILL.md
skills/pytorch-patterns/SKILL.md
skills/fastapi-patterns/SKILL.md          (implicit, check if present)
```

### 2. **Agents**
```
agents/python-reviewer.md
agents/django-build-resolver.md
.kiro/agents/python-reviewer.md           (alternate format)
```

### 3. **Commands**
```
commands/python-review.md
```

### 4. **Configuration Files**
```
pyproject.toml                            (root LLM abstraction layer)
skills/skill-comply/pyproject.toml
```

### 5. **Rules** (check for)
```
rules/python/                             (directory scan needed)
rules/python/*.md                         (PEP 8, style, etc.)
```

### 6. **Documentation**
```
docs/ja-JP/skills/python-patterns/SKILL.md
docs/ja-JP/skills/python-testing/SKILL.md
docs/es/skills/python-patterns/SKILL.md
docs/tr/skills/python-patterns/SKILL.md
.codebuddy/README.md                      (may reference Python install)
.opencode/plugins/ecc-hooks.ts            (TypeScript but calls Python)
```

### 7. **Install/CI** (check contents)
```
install.sh
install.ps1
scripts/setup-package-manager.js
scripts/ci/scan-supply-chain-iocs.js
```

---

## 🔍 Current Python Version Assumptions

### **pyproject.toml** (Root)
```toml
requires-python = ">=3.11"

[tool.ruff]
target-version = "py311"

[tool.mypy]
python_version = "3.11"

classifiers = [
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
```

**Status:** Pins to 3.11–3.12. **Needs update to 3.14.**

### **skills/skill-comply/pyproject.toml**
```toml
requires-python = ">=3.11"
```

**Status:** Same as root. **Needs update.**

### **Skills Content** (python-patterns, python-testing, etc.)
- ✅ Uses modern type hints (`list[str]` not `List[str]` - requires 3.9+)
- ✅ Uses `|` union syntax (requires 3.10+)
- ✅ Uses `match` statements (requires 3.10+)
- ⚠️ References `from typing import Optional, Union` for Python 3.8 compatibility — still present but noted as legacy
- ❌ **Does NOT mention** PEP 649/749 deferred evaluation (new in 3.13–3.14)
- ❌ **Does NOT mention** `concurrent.interpreters` (new in 3.13, stable in 3.14)
- ❌ **Does NOT mention** PEP 768 external debugger interface (new in 3.14)

### **agents/python-reviewer.md**
- ✅ Diagnostic commands reference ruff, mypy, black (all 3.14-compatible)
- ⚠️ No version matrix beyond basic Python 3.5+ features
- ❌ No mention of 3.14-specific features to check for

---

## 📊 Version Support Matrix (Current)

| Feature | Minimum | Current Skills | Update Needed |
|---------|---------|-----------------|-----------------|
| Type hints (PEP 484) | 3.5 | ✅ Documented | No |
| f-strings | 3.6 | ✅ Documented | No |
| Walrus operator `:=` | 3.8 | ✅ Mentioned | No |
| Positional-only params | 3.8 | ✅ Mentioned | No |
| Union with `\|` | 3.10 | ✅ Used in examples | No |
| Match statements | 3.10 | ✅ Used in examples | No |
| **PEP 649 deferred annotations** | **3.13** | ❌ **Not mentioned** | **YES** |
| **PEP 749 deferred builtin classes** | **3.13** | ❌ **Not mentioned** | **YES** |
| **concurrent.interpreters** | **3.13** | ❌ **Not mentioned** | **YES** |
| **PEP 768 external debugger** | **3.14** | ❌ **Not mentioned** | **YES** |
| Type parameter syntax `[]` | 3.12 | ⚠️ Minimal coverage | Expand |
| `.whl` universal wheels | 3.14+ | ⚠️ Not covered | Add |

---

## 🎯 Scope & Changes Required

### **Phase 1: Version Pin Updates** (Simple find/replace)

**Files to update:**
- `pyproject.toml` (2 occurrences: `requires-python`, classifiers)
- `skills/skill-comply/pyproject.toml` (1 occurrence)
- `commands/python-review.md` (version table in "Python Version Compatibility")
- `.opencode/package.json` (@types/node, TypeScript versions may reference Python)

**Change pattern:**
```diff
- requires-python = ">=3.11"
+ requires-python = ">=3.11"  # 3.14 recommended, 3.11–3.13 supported

- target-version = "py311"
+ target-version = "py314"

- python_version = "3.11"
+ python_version = "3.14"

- "Programming Language :: Python :: 3.11",
- "Programming Language :: Python :: 3.12",
+ "Programming Language :: Python :: 3.11",
+ "Programming Language :: Python :: 3.12",
+ "Programming Language :: Python :: 3.13",
+ "Programming Language :: Python :: 3.14",
```

---

### **Phase 2: PEP 649/749 Deferred Evaluation Guidance**

**Where:** `skills/python-patterns/SKILL.md` (Type Hints section)

**Add new section after "Type Aliases and TypeVar":**

```markdown
### Deferred Evaluation of Annotations (Python 3.13+, PEP 649/749)

Python 3.13 introduced automatic deferred evaluation of annotations via PEP 649, 
and Python 3.14 stabilizes this with PEP 749. **This eliminates the need for 
`from __future__ import annotations` in most cases.**

#### Before Python 3.13 (Forward References Required)

```python
from __future__ import annotations

class User:
    def get_related(self) -> Related:  # Forward reference works with deferred import
        pass

class Related:
    pass
```

#### Python 3.14+ (Automatic Deferred Evaluation)

```python
# No need for __future__ import — annotations are deferred by default
class User:
    def get_related(self) -> Related:  # Works directly
        pass

class Related:
    pass
```

**Impact:**
- Simpler code — no `from __future__ import annotations` boilerplate
- Faster startup time — annotations not evaluated at definition
- Better type checker integration — mypy/pyright understand deferred eval natively

**Recommendation:**
- If targeting Python 3.14+: Remove `from __future__ import annotations`
- If supporting Python 3.11–3.13: Keep `from __future__ import annotations` for forward refs
- Use tool configs (e.g., `[tool.mypy] python_version = "3.14"`) to opt into 3.14 semantics
```

---

### **Phase 3: concurrent.interpreters (Subinterpreters)**

**Where:** `skills/python-patterns/SKILL.md` (new "Concurrency & Parallelism" section)

**Add after Generators section:**

```markdown
### Subinterpreters (Python 3.13+, PEP 734)

Python 3.13 stabilized the `concurrent.interpreters` module, enabling true 
parallelism without the GIL by using isolated subinterpreters.

#### Use Case: CPU-Bound Parallelism Without GIL

```python
# Before Python 3.13: GIL contention with threading
import threading
import time

def cpu_bound_task(n):
    total = 0
    for i in range(n):
        total += i ** 2
    return total

# Slow due to GIL:
threads = [
    threading.Thread(target=cpu_bound_task, args=(10_000_000,))
    for _ in range(4)
]
for t in threads:
    t.start()
for t in threads:
    t.join()

# Python 3.13+: Use subinterpreters for true parallelism
from concurrent.interpreters import create_interpreter, run

code = """
def cpu_bound(n):
    return sum(i ** 2 for i in range(n))
result = cpu_bound(10_000_000)
"""

interp = create_interpreter()
result = run(interp, code)
print(result)
```

**Key Differences from threading:**
- **No GIL contention** — each subinterpreter has its own GIL
- **Isolated state** — no shared mutable objects (data must be pickled)
- **Ideal for:** Compute-heavy workloads, batch processing
- **Overhead:** More than threading but justified for long-running CPU tasks

#### When to Use Subinterpreters

| Scenario | Recommendation |
|----------|-----------------|
| I/O-bound (network, file, DB) | Use `asyncio` or threading (lower overhead) |
| CPU-bound (math, ML, image processing) | Use `concurrent.interpreters` (avoids GIL) |
| Long-lived worker tasks | Use `multiprocessing` (established, stable) |
| Real-time collaboration (shared state) | Use `multiprocessing.Manager` or message queues |

```

---

### **Phase 4: PEP 768 External Debugger Interface**

**Where:** `skills/python-patterns/SKILL.md` (new "Debugging & Introspection" section) OR mentioned in `agents/python-reviewer.md`

**Add:**

```markdown
### External Debugger Protocol (Python 3.14+, PEP 768)

Python 3.14 introduces `sys.monitoring.debugger_status()` and structured 
debugging interface, making it safer to use external debuggers without 
breaking Python internals.

#### Safe Debugging Pattern

```python
import sys
import sys.monitoring

# Check debugger status (Python 3.14+)
if hasattr(sys.monitoring, 'debugger_status'):
    status = sys.monitoring.debugger_status()
    print(f"Debugger active: {status.debugger_enabled}")

# Alternative: Traditional approach (Python 3.11–3.13)
if sys.gettrace() is not None:
    print("Debugger or tracer is active")
```

**Use in Production Code:**
```python
# Avoid expensive operations if debugger is attached
def expensive_computation():
    if sys.gettrace() is None:
        # Safe to run without debugger overhead
        return compute()
    else:
        # Debugger attached — use fast approximation
        return compute_fast_approximation()
```

**Relevance to ECC:**
- Tools like Claude Code, Cursor, OpenCode may use external debuggers
- Agents can optimize behavior based on `debugger_status()`
- Improved observability for development workflows

```

---

### **Phase 5: Update Tool Recommendations**

**Where:** `agents/python-reviewer.md` and `commands/python-review.md`

**Update diagnostic commands section:**

```bash
# Add Python 3.14 target versions
ruff check . --select E,F,I,N,W,UP                    # Upgrade checks
ruff check . --target-version py314                   # Python 3.14 specific
mypy . --python-version 3.14                          # Type check for 3.14
pyright . --pythonversion 3.14                        # Pyright for 3.14

# Additional 3.14 checks
python -m py_compile .                                # Syntax check
python -m compileall -q .                             # Compile all .py files
python --version                                      # Confirm 3.14 installed
```

**Update tool version matrix:**

| Tool | Version | Target Python | Notes |
|------|---------|----------------|-------|
| ruff | 0.8.0+ | py314 | Fast linter |
| mypy | 1.14.0+ | 3.14 | PEP 649/749 aware |
| pyright | 1.1.400+ | 3.14 | Full 3.14 support |
| black | 24.8.0+ | 3.14 | AST-based formatter |
| pytest | 8.0.0+ | 3.14 | Testing framework |
| pyinstaller | 6.8.0+ | 3.14 | Binary packaging |

---

### **Phase 6: Update Example Configurations**

**Where:** `examples/`, `mcp-configs/` (if present)

**Create/update `examples/pyproject-3.14.toml`:**

```toml
[project]
name = "my-app"
version = "1.0.0"
description = "Python 3.14 compatible app"
requires-python = ">=3.11"  # Support 3.11–3.14

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
]

dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=7.1.0",
    "mypy>=1.14.0",
    "ruff>=0.8.0",
    "black>=24.8.0",
    "pyright>=1.1.400",
]

[tool.mypy]
python_version = "3.14"
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true

[tool.ruff]
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "RUF"]
ignore = ["E501"]  # Line too long (handled by black)

[tool.black]
line-length = 88
target-version = ["py314"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
python_files = ["test_*.py", "*_test.py"]
```

---

## 🧪 Test Coverage

**Files to validate after updates:**

```bash
# Syntax validation
python -m compileall -q skills/python-*/
python -m compileall -q agents/
python -m compileall -q rules/python/

# Type checking (if applicable)
mypy skills/python-patterns/ --python-version 3.14

# Example code blocks validation (extract and check)
# For each .md file: parse code blocks, save as .py, run mypy

# Lint config validation
python -c "import toml; toml.load('pyproject.toml')"
```

---

## 📝 Breaking Changes & Migration Notes

### **For Users Upgrading to This Snapshot**

#### If using Python < 3.11
- **Action Required:** Upgrade to Python 3.11+. Python 3.10 EOL: 2023-10-02.
- **Guidance:** Install via `python.org` or `pyenv`: `pyenv install 3.14.6`

#### If using `from __future__ import annotations` (current pattern)
- **Old Pattern (still works):**
  ```python
  from __future__ import annotations
  class User:
      def method(self) -> Future:  # Works in 3.11–3.13
          pass
  ```
- **New Pattern (3.14+, optional):**
  ```python
  # No import needed in 3.14+
  class User:
      def method(self) -> Future:  # Works without import in 3.14
          pass
  ```
- **Recommendation:** Keep the import for cross-version compatibility (3.11–3.14)

#### If using `threading` for CPU-bound work
- **Consider:** `concurrent.interpreters` (Python 3.13+) for true parallelism
- **Example:** See skills/python-patterns/SKILL.md § Subinterpreters

---

## ✅ Checklist (Pre-Implementation)

- [ ] Confirm Python 3.14.6 is the latest stable (verify docs.python.org)
- [ ] Confirm Python 3.15 is pre-release/alpha (check release schedule)
- [ ] Audit all `.md` files for hardcoded version strings (3.11, 3.12, etc.)
- [ ] Check for CLI commands with explicit `python3.11` references
- [ ] Review CI/CD `.yml` files (if present) for test matrix
- [ ] Identify any Cython/C extension guidance needing 3.14 marker
- [ ] Validate all example code blocks parse with `ast.parse()`
- [ ] Test ruff/mypy with `target-version = "py314"`
- [ ] Create GitHub issue for 3.15 pre-release watch (for future update)
- [ ] Prepare PR description with before/after version comparisons

---

## 🔗 References

- **Python 3.14 Release Notes:** https://docs.python.org/3/whatsnew/3.14.html
- **PEP 649:** https://peps.python.org/pep-0649/
- **PEP 749:** https://peps.python.org/pep-0749/
- **PEP 768:** https://peps.python.org/pep-0768/
- **PEP 734 (Subinterpreters):** https://peps.python.org/pep-0734/
- **Ruff 3.14 Support:** https://github.com/astral-sh/ruff/releases
- **Mypy 3.14 Support:** https://github.com/python/mypy/releases

---

## 🎬 Next Steps

1. **Review this plan** with stakeholder (Nicholas)
2. **Proceed to Phase 1** (version pin updates) if approved
3. **Run validation tests** after each phase
4. **Create PR** with summary of all changes
5. **Monitor for Python 3.15 alpha/beta releases** (plan for future sync)

---

**Status:** ✅ Ready for implementation  
**Scope Compliance:** ✅ Python 3.14 only (3.15 intentionally excluded)  
**Estimated Effort:** 2–3 hours (mostly search/replace + new section content)
