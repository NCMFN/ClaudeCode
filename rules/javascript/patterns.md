---
paths:
  - "**/*.html"
  - "**/*.css"
  - "**/*.js"
---
# Vanilla JavaScript Patterns

> This file extends [common/patterns.md](../common/patterns.md) with vanilla HTML/CSS/JavaScript specific content.

## State Management

Use a single source-of-truth state object and pure render functions. Never scatter state across DOM attributes.

```javascript
// Single state object
let state = {
  players: [],
  currentRound: 0,
  scores: {},
};

// Pure state update — returns new state, never mutates
function updateScore(state, playerId, points) {
  return {
    ...state,
    scores: {
      ...state.scores,
      [playerId]: (state.scores[playerId] ?? 0) + points,
    },
  };
}

// Render reacts to state
function render(state) {
  document.getElementById('round').textContent = state.currentRound;
  renderScoreboard(state.players, state.scores);
}

// Usage
state = updateScore(state, 'player1', 10);
render(state);
```

## DOM Manipulation

### Query Selectors

Cache DOM references; don't query on every render:

```javascript
// WRONG: queries DOM on every call
function updateName() {
  document.querySelector('#player-name').textContent = name;
}

// CORRECT: cache reference
const playerNameEl = document.getElementById('player-name');
function updateName(name) {
  playerNameEl.textContent = name;
}
```

### Event Delegation

Attach one listener to a parent rather than many listeners on children:

```javascript
// WRONG: listener per item (breaks on dynamic content)
document.querySelectorAll('.player-card').forEach(card => {
  card.addEventListener('click', handleCardClick);
});

// CORRECT: single delegated listener
document.getElementById('player-list').addEventListener('click', (e) => {
  const card = e.target.closest('.player-card');
  if (!card) return;
  handleCardClick(card.dataset.playerId);
});
```

### Template Strings for Rendering

Use template literals to build HTML; sanitize user content:

```javascript
function renderPlayer(player) {
  return `
    <div class="player-card" data-player-id="${player.id}">
      <span class="player-card__name">${escapeHtml(player.name)}</span>
      <span class="player-card__score">${player.score}</span>
    </div>
  `;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Batch render to minimize reflows
container.innerHTML = players.map(renderPlayer).join('');
```

## LocalStorage

Wrap localStorage reads with try-catch; storage can be disabled or quota-exceeded:

```javascript
function saveState(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (err) {
    console.error('Could not save to localStorage:', err);
  }
}

function loadState(key, fallback = null) {
  try {
    const raw = localStorage.getItem(key);
    return raw !== null ? JSON.parse(raw) : fallback;
  } catch (err) {
    console.error('Could not read from localStorage:', err);
    return fallback;
  }
}
```

## Fetch / API Calls

Centralize HTTP calls; always handle non-2xx responses:

```javascript
async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

// Usage
async function loadPlayers() {
  try {
    return await apiFetch('/api/players');
  } catch (err) {
    showError('Failed to load players.');
    return [];
  }
}
```

## Event Handler Naming

Use named functions for handlers so they can be properly removed:

```javascript
// WRONG: anonymous — cannot be removed
button.addEventListener('click', () => handleSubmit());

// CORRECT: named reference
function onSubmitClick() { handleSubmit(); }
button.addEventListener('click', onSubmitClick);

// Can now clean up
button.removeEventListener('click', onSubmitClick);
```

## Debounce / Throttle

Limit frequency of expensive operations triggered by user input:

```javascript
function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

const handleSearch = debounce((query) => {
  filterPlayers(query);
}, 300);

searchInput.addEventListener('input', (e) => handleSearch(e.target.value));
```
