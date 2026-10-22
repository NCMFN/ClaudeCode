---
description: Run an accessibility review for a website or web app against WCAG 2.2 AA checks.
---

# A11y Audit Command

Use `/a11y-audit` for a focused accessibility review.

## Review flow

1. Inspect structure and landmarks
2. Test keyboard-only navigation
3. Review labels, forms, and errors
4. Check color contrast and focus states
5. Verify media and alternative text
6. Run axe/Lighthouse review

## Default report format

```markdown
# Accessibility Audit

## Summary
- PASS/FAIL
- Issues found: X

## Critical issues
- keyboard trap in modal
- missing form labels

## Recommended fixes
1. add visible focus ring
2. correct heading hierarchy
3. fix label associations
```

## Related skills

- `web-accessibility`
- `web-design-system`
