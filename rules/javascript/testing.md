---
paths:
  - "**/*.html"
  - "**/*.css"
  - "**/*.js"
---
# Vanilla JavaScript Testing

> This file extends [common/testing.md](../common/testing.md) with vanilla HTML/CSS/JavaScript specific content.

## Unit Testing

Use **Vitest** (preferred) or **Jest** for testing pure JavaScript functions. Pure logic (scoring, state transforms, data parsing) should be extracted and unit-tested independently of the DOM.

### Setup

```bash
npm init -y
npm install -D vitest @vitest/coverage-v8
```

```json
// package.json
{
  "scripts": {
    "test": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}
```

### Example: Testing Pure Functions

```javascript
// scores.js — pure logic, no DOM
export function calculateScore(bid, actual, bonus = 0) {
  if (bid === actual) return 10 + actual + bonus;
  return -Math.abs(bid - actual) * 2;
}

// scores.test.js
import { describe, it, expect } from 'vitest';
import { calculateScore } from './scores.js';

describe('calculateScore', () => {
  it('awards 10 + tricks when bid matches', () => {
    expect(calculateScore(3, 3)).toBe(13);
  });

  it('penalizes missed bids', () => {
    expect(calculateScore(3, 1)).toBe(-4);
  });

  it('includes bonus in successful bids', () => {
    expect(calculateScore(2, 2, 5)).toBe(19);
  });
});
```

## DOM Testing

Use **jsdom** (via Vitest's `environment: 'jsdom'`) to test DOM interactions without a browser:

```javascript
// vitest.config.js
import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: { environment: 'jsdom' },
});
```

```javascript
// render.test.js
import { describe, it, expect, beforeEach } from 'vitest';
import { renderPlayer } from './render.js';

describe('renderPlayer', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="container"></div>';
  });

  it('renders player name and score', () => {
    document.getElementById('container').innerHTML =
      renderPlayer({ id: '1', name: 'Alice', score: 42 });
    expect(document.querySelector('.player-card__name').textContent).toBe('Alice');
    expect(document.querySelector('.player-card__score').textContent).toBe('42');
  });
});
```

## E2E Testing

Use **Playwright** for end-to-end browser testing of critical user flows:

```bash
npm install -D @playwright/test
npx playwright install
```

```javascript
// tests/game.spec.js
import { test, expect } from '@playwright/test';

test('player can place a bid and see score update', async ({ page }) => {
  await page.goto('/');
  await page.click('#start-game');
  await page.fill('#bid-input', '3');
  await page.click('#submit-bid');
  await expect(page.locator('.player-card__score')).toContainText('3');
});
```

## Coverage

- Minimum **80% coverage** on pure JS logic files
- DOM rendering functions: covered by DOM tests
- E2E covers critical happy paths only

## Agent Support

- **tdd-guide** — Enforces write-tests-first workflow
- **e2e-runner** — Playwright E2E testing specialist
