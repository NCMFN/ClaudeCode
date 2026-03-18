---
name: vanilla-web
description: Patterns and best practices for vanilla HTML, CSS, and JavaScript applications — no frameworks required. Covers project structure, CSS architecture, state management, DOM manipulation, localStorage, fetch API, and testing setup.
origin: ECC
---

# Vanilla Web Development

Patterns for building maintainable, performant apps with pure HTML, CSS, and JavaScript — no build tools or frameworks required.

## When to Activate

- Building or maintaining a vanilla HTML/CSS/JS single-page application
- Refactoring a monolithic HTML file into modular structure
- Adding state management, DOM rendering, or localStorage patterns
- Setting up testing for a no-framework JS project
- Reviewing CSS architecture or HTML semantics

---

## Project Structure

Recommended layout for a non-trivial vanilla web app:

```
project/
├── index.html          # Entry point — HTML structure only
├── styles/
│   ├── base.css        # Reset, custom properties, typography
│   ├── layout.css      # Grid, flexbox, containers
│   └── components.css  # BEM component styles
├── scripts/
│   ├── state.js        # State object and pure update functions
│   ├── render.js       # DOM rendering functions
│   ├── api.js          # fetch wrappers
│   ├── storage.js      # localStorage helpers
│   └── main.js         # Entry point — wires everything together
├── assets/
│   └── icons/
└── tests/
    ├── state.test.js
    └── render.test.js
```

For simpler apps, a single `index.html` with `<style>` and `<script>` blocks is fine — extract to files when any section exceeds ~300 lines.

---

## CSS Architecture

### Custom Properties for Theming

Define all design tokens in `:root` for a single source of truth:

```css
:root {
  /* Colors */
  --color-primary: #3b82f6;
  --color-primary-dark: #2563eb;
  --color-surface: #1e293b;
  --color-on-surface: #f1f5f9;
  --color-error: #ef4444;

  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 2rem;

  /* Typography */
  --font-sans: system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.25rem;

  /* Shape */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
}
```

### BEM Component Example

```css
/* Block */
.player-card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-md);
}

/* Elements */
.player-card__name {
  font-size: var(--text-lg);
  font-weight: 600;
}

.player-card__score {
  font-variant-numeric: tabular-nums;
  color: var(--color-primary);
}

/* Modifiers */
.player-card--active {
  border: 2px solid var(--color-primary);
}

.player-card--eliminated {
  opacity: 0.4;
  pointer-events: none;
}
```

### Responsive Grid

```css
.player-grid {
  display: grid;
  grid-template-columns: 1fr;          /* mobile: 1 column */
  gap: var(--space-md);
}

@media (min-width: 640px) {
  .player-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1024px) {
  .player-grid { grid-template-columns: repeat(4, 1fr); }
}
```

---

## State Management

Single state object + pure render functions — the simplest pattern that scales:

```javascript
// state.js
let _state = {
  players: [],
  round: 0,
  phase: 'setup', // 'setup' | 'bidding' | 'scoring' | 'finished'
  scores: {},
};

export function getState() { return _state; }

export function setState(updater) {
  _state = typeof updater === 'function'
    ? updater(_state)
    : { ..._state, ...updater };
  // Notify subscribers
  _listeners.forEach(fn => fn(_state));
}

const _listeners = new Set();
export function subscribe(fn) {
  _listeners.add(fn);
  return () => _listeners.delete(fn); // returns unsubscribe
}
```

```javascript
// main.js
import { subscribe } from './state.js';
import { render } from './render.js';

// Re-render whenever state changes
subscribe(render);
```

---

## DOM Rendering

### Efficient Rendering with Template Strings

```javascript
// render.js
export function renderScoreboard(players, scores) {
  const container = document.getElementById('scoreboard');

  // Build HTML string — one innerHTML assignment to minimize reflows
  container.innerHTML = players
    .map(player => renderPlayerCard(player, scores[player.id] ?? 0))
    .join('');
}

function renderPlayerCard(player, score) {
  return `
    <div class="player-card ${score < 0 ? 'player-card--negative' : ''}"
         data-player-id="${player.id}">
      <span class="player-card__name">${escapeHtml(player.name)}</span>
      <span class="player-card__score">${score}</span>
    </div>
  `;
}

function escapeHtml(str) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  return String(str).replace(/[&<>"']/g, c => map[c]);
}
```

### Event Delegation

```javascript
// One listener handles all player card clicks — works for dynamically added cards
document.getElementById('scoreboard').addEventListener('click', (e) => {
  const card = e.target.closest('[data-player-id]');
  if (!card) return;
  selectPlayer(card.dataset.playerId);
});
```

---

## LocalStorage

```javascript
// storage.js
const PREFIX = 'oh-hell:';

export function save(key, value) {
  try {
    localStorage.setItem(PREFIX + key, JSON.stringify(value));
  } catch (err) {
    console.error(`[storage] Could not save "${key}":`, err);
  }
}

export function load(key, fallback = null) {
  try {
    const raw = localStorage.getItem(PREFIX + key);
    return raw !== null ? JSON.parse(raw) : fallback;
  } catch (err) {
    console.error(`[storage] Could not load "${key}":`, err);
    return fallback;
  }
}

export function remove(key) {
  localStorage.removeItem(PREFIX + key);
}
```

---

## Fetch API

```javascript
// api.js
async function request(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });

  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status}: ${body}`);
  }

  const contentType = res.headers.get('content-type') ?? '';
  return contentType.includes('application/json') ? res.json() : res.text();
}

export const api = {
  get:    (url)         => request(url),
  post:   (url, data)   => request(url, { method: 'POST',   body: JSON.stringify(data) }),
  put:    (url, data)   => request(url, { method: 'PUT',    body: JSON.stringify(data) }),
  delete: (url)         => request(url, { method: 'DELETE' }),
};
```

---

## Performance

### Debounce for Input Handlers

```javascript
function debounce(fn, ms) {
  let id;
  return (...args) => { clearTimeout(id); id = setTimeout(() => fn(...args), ms); };
}

searchInput.addEventListener('input', debounce(e => filterPlayers(e.target.value), 250));
```

### IntersectionObserver for Lazy Loading

```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      observer.unobserve(img);
    }
  });
});

document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img));
```

---

## Testing Setup (Vitest)

Minimal setup for testing pure functions:

```bash
npm init -y
npm install -D vitest @vitest/coverage-v8
```

```json
// package.json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "coverage": "vitest run --coverage"
  }
}
```

```javascript
// vitest.config.js
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom', // for DOM tests
    coverage: {
      provider: 'v8',
      thresholds: { lines: 80, functions: 80, branches: 80 },
    },
  },
});
```

## How to Run Without a Build Tool

Open directly in browser (no server needed for basic apps):

```bash
open index.html       # macOS
xdg-open index.html  # Linux
```

Or use a zero-config dev server for fetch calls and ES modules:

```bash
npx serve .           # static file server on http://localhost:3000
# or
npx vite              # fast dev server with HMR
```
