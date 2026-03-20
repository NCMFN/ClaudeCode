---
name: typescript-patterns
description: TypeScript best practices, type safety, generics, async patterns, and project configuration for Claude Code and Codex.
---

# TypeScript Patterns

## When to Use
- Working with TypeScript projects
- Adding type safety to JavaScript code
- Configuring tsconfig.json
- Using generics, utility types, or advanced type features

## How It Works
1. Apply strict TypeScript configuration
2. Use proper type annotations and inference
3. Leverage generics for reusable components
4. Handle async/await with proper error types

## Key Patterns

### Strict Configuration
Always enable strict mode in tsconfig.json: strict, noUncheckedIndexedAccess, exactOptionalPropertyTypes.

### Type-Safe Error Handling
Use discriminated unions for error types instead of throwing. Return Result types for fallible operations.

### Generic Constraints
Constrain generics with extends to ensure type safety while maintaining flexibility.

### Async Patterns
Use async/await with typed catch blocks. Prefer Promise.allSettled over Promise.all for parallel operations that can partially fail.

### Utility Types
Use Pick, Omit, Partial, Required, Record for type transformations instead of manual type definitions.

## Examples
- Use zod for runtime validation that generates TypeScript types
- Prefer const assertions for literal types
- Use satisfies operator for type checking without widening
