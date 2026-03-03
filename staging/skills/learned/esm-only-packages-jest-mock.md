---
name: esm-only-packages-jest-mock
description: "Fix ESM-only npm packages (type:module) that break Jest with 'Unexpected token export'"
user-invocable: false
origin: auto-extracted
---

# ESM-Only Packages in Jest: Use moduleNameMapper, Not transformIgnorePatterns

**Extracted:** 2026-02-28
**Context:** Next.js projects using Jest (via `next/jest`) that import modern ESM-only packages

## Problem

Modern packages (rehype-*, unified, nanoid@4+, etc.) ship as pure ESM (`"type": "module"` in package.json, `export` syntax in index.js). Jest runs in CommonJS by default and fails with:

```
SyntaxError: Unexpected token 'export'
/node_modules/rehype-sanitize/index.js
export {defaultSchema} from 'hast-util-sanitize'
```

## Why `transformIgnorePatterns` Fails

The intuitive fix — adding the package to the `transformIgnorePatterns` exception list — often fails in Next.js projects because:

1. `next/jest`'s `createJestConfig` is async and may override custom patterns
2. Transitive ESM dependencies (e.g. `hast-util-sanitize`) must *also* be included
3. The exception list grows unboundedly as the package's dep tree is ESM

## Solution: `moduleNameMapper` + CJS Mock

Create a hand-written CJS mock and redirect the import in Jest config:

**`src/__mocks__/rehype-sanitize.js`**
```js
// Jest mock: rehype-sanitize is ESM-only, incompatible with Jest's CJS transform.
// No-op passthrough plugin for test environment.
const rehypeSanitize = () => () => {}
module.exports = rehypeSanitize
module.exports.default = rehypeSanitize
module.exports.defaultSchema = {}
```

**`jest.config.js`**
```js
moduleNameMapper: {
  '^@/(.*)$': '<rootDir>/src/$1',
  '^rehype-sanitize$': '<rootDir>/src/__mocks__/rehype-sanitize.js',
},
```

## Identifying ESM-Only Packages

```bash
cat node_modules/<pkg>/package.json | grep '"type"'
# "type": "module" → ESM-only, needs mock
head -3 node_modules/<pkg>/index.js
# "export {" or "export default" → ESM-only
```

## When to Use

- Jest fails with `SyntaxError: Unexpected token 'export'` on a node_modules file
- The package has `"type": "module"` in its package.json
- Adding to `transformIgnorePatterns` doesn't fix it or requires too many transitive additions

## Mock Quality Notes

- For **plugins** (rehype-*, remark-*): mock as `() => () => {}` (no-op transform)
- For **utilities** (e.g. nanoid): mock as `() => 'mock-id'` or similar stub
- For **packages that must work correctly in tests**: prefer `transformIgnorePatterns` with the full transitive dep list instead
