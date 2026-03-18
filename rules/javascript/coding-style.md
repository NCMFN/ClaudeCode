---
paths:
  - "**/*.html"
  - "**/*.css"
  - "**/*.js"
---
# Vanilla JavaScript/CSS/HTML Coding Style

> This file extends [common/coding-style.md](../common/coding-style.md) with vanilla HTML/CSS/JavaScript specific content.

## HTML

### Semantic Elements

Use semantic HTML elements to convey meaning and improve accessibility:

```html
<!-- WRONG: div soup -->
<div class="header">
  <div class="nav">...</div>
</div>
<div class="main">
  <div class="article">...</div>
</div>

<!-- CORRECT: semantic structure -->
<header>
  <nav>...</nav>
</header>
<main>
  <article>...</article>
</main>
```

### Accessibility

- Always provide `alt` text for `<img>` elements
- Associate `<label>` with every form input via `for`/`id` or nesting
- Use `aria-*` attributes only when native semantics are insufficient
- Ensure interactive elements are keyboard-reachable

```html
<!-- WRONG: inaccessible form -->
<div onclick="submit()">Submit</div>
<input type="text" />

<!-- CORRECT: accessible form -->
<label for="username">Username</label>
<input type="text" id="username" name="username" />
<button type="submit">Submit</button>
```

### No Inline Styles

- Keep styles in CSS files or `<style>` blocks, not `style=""` attributes
- Exception: dynamically computed values (e.g., animation progress, user-set colors)

---

## CSS

### Custom Properties (CSS Variables)

Use custom properties for theming and repeated values:

```css
/* WRONG: magic values scattered everywhere */
.button { background: #3b82f6; border-radius: 8px; }
.card   { border-radius: 8px; }

/* CORRECT: single source of truth */
:root {
  --color-primary: #3b82f6;
  --radius-md: 8px;
}

.button { background: var(--color-primary); border-radius: var(--radius-md); }
.card   { border-radius: var(--radius-md); }
```

### BEM Naming

Use Block__Element--Modifier for component class names:

```css
/* Block */
.player-card { ... }

/* Element */
.player-card__name { ... }
.player-card__score { ... }

/* Modifier */
.player-card--active { ... }
.player-card--eliminated { ... }
```

### Mobile-First Media Queries

Write base styles for small screens, enhance with `min-width` queries:

```css
/* WRONG: desktop-first (requires overrides for mobile) */
.grid { display: grid; grid-template-columns: repeat(4, 1fr); }
@media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }

/* CORRECT: mobile-first */
.grid { display: grid; grid-template-columns: 1fr; }
@media (min-width: 768px) { .grid { grid-template-columns: repeat(4, 1fr); } }
```

---

## JavaScript

### Variable Declarations

- Use `const` by default; use `let` only when reassignment is needed
- Never use `var`

```javascript
// WRONG
var count = 0;

// CORRECT
const MAX_ROUNDS = 10;
let currentRound = 0;
```

### Modern Syntax

Prefer modern JavaScript features for clarity:

```javascript
// Template literals over concatenation
const greeting = `Hello, ${player.name}!`;

// Optional chaining over manual null checks
const score = game?.players?.[0]?.score ?? 0;

// Destructuring
const { name, bid, score } = player;
const [first, ...rest] = players;
```

### Immutability

Create new objects/arrays rather than mutating existing ones:

```javascript
// WRONG: mutation
function addScore(player, points) {
  player.score += points; // mutates!
  return player;
}

// CORRECT: immutable update
function addScore(player, points) {
  return { ...player, score: player.score + points };
}

// WRONG: array mutation
players.push(newPlayer);

// CORRECT: new array
const updatedPlayers = [...players, newPlayer];
```

### Error Handling

Always handle errors explicitly; never silently swallow them:

```javascript
// WRONG: unhandled rejection
fetch('/api/data').then(res => res.json());

// CORRECT: explicit error handling
async function loadData() {
  try {
    const res = await fetch('/api/data');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Failed to load data:', err);
    showErrorMessage('Could not load data. Please try again.');
  }
}
```

### No Global Namespace Pollution

Encapsulate code in modules or IIFEs; do not attach to `window` unless required:

```javascript
// WRONG: pollutes global scope
var gameState = {};
function calculateScore() { ... }

// CORRECT: ES module
export const gameState = {};
export function calculateScore() { ... }

// OR: IIFE for non-module scripts
const GameApp = (() => {
  const state = {};
  function calculateScore() { ... }
  return { calculateScore };
})();
```

## Console.log

- No `console.log` statements in production code
- Use `console.error` / `console.warn` for real error conditions only
- See hooks for automatic detection
