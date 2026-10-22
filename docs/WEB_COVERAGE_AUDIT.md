# Web Coverage Audit

## Scope and repo conventions

This repository is an agent-harness and skills library, not a website framework. The current conventions are consistent across the codebase:

- `agents/` contains specialist agents as markdown files with YAML frontmatter (`name`, `description`, `tools`, `model`).
- `skills/` contains workflow modules under one directory per skill, each with a `SKILL.md` file.
- `commands/` contains slash-command markdown files that operationalize workflows.
- `hooks/`, `rules/`, `schemas/`, `scripts/`, and `manifests/` provide automation, validation, and compatibility layers.
- Validation is Node-based and registered in `package.json` with `npm test`, `npm run lint`, and `npm run harness:audit`.
- The repo favors reuse and compatibility over a single monolithic framework. The root `AGENTS.md` states the canonical surface is `skills/`, while `commands/` remains compatibility shims.

This means the correct extension pattern is to add new skills and starter templates under the existing layout, not to invent a separate web app framework or a parallel top-level website directory.

## Current web-related assets

### Core repo assets already relevant to web work

- `skills/frontend-patterns/` — general frontend guidance and component patterns.
- `skills/backend-patterns/` — API/backend patterns for application architecture.
- `skills/design-system/` — design-system guidance and tokens.
- `skills/api-design/` — REST and API design guidance.
- `skills/deployment-patterns/` — Docker, hosting, and production deployment practices.
- `skills/security-review/` — security checks and vulnerability review workflow.
- `skills/e2e-testing/` — browser/test automation patterns.
- `skills/django-patterns/`, `django-security`, `django-tdd`, `django-verification`
- `skills/laravel-patterns/`, `laravel-security`, `laravel-tdd`, `laravel-verification`
- `skills/nextjs-turbopack/`
- `skills/nuxt4-patterns/`
- `skills/frontend-slides/` — presentation/front-end UX output workflow.
- `skills/postgres-patterns/`
- `skills/docker-patterns/`
- `skills/documentation-lookup/`

### Agents that are already useful for web delivery

- `agents/code-reviewer.md`
- `agents/security-reviewer.md`
- `agents/performance-optimizer.md`
- `agents/e2e-runner`-style patterns described in `AGENTS.md` and commands such as `commands/e2e.md`
- `agents/doc-updater.md` and related documentation workflow patterns

### Commands and validation already present

- `commands/e2e.md` — end-to-end testing workflows
- `commands/plan.md` — planning flow
- `commands/build-fix.md` — build and fix workflows
- `commands/quality-gate.md`
- `commands/verify.md`
- `commands/pm2.md`, `commands/deploy`-style patterns exist only in a general sense, but there is no dedicated production website deployment command set.

### What is missing specifically for the requested objective

The repo does not yet provide a website-production workflow with:

- one skill per website type
- one skill per stack from the required matrix
- a complete command set for `/new-site`, `/plan-site`, `/add-feature`, `/design-system`, `/a11y-audit`, `/seo-audit`, `/perf-audit`, `/security-audit`, `/test-site`, `/deploy`, `/launch-checklist`, `/handoff-docs`
- reusable starters for each major web stack and site type
- cross-cutting skills for accessibility, SEO, payments, CMS, analytics, i18n, devops, and maintenance
- agent definitions for web-architect, frontend-engineer, backend-engineer, ui-ux-designer, accessibility-auditor, seo-specialist, security-reviewer (web), performance-engineer, devops-deployer, qa/e2e-tester, content-strategist
- a single orchestration playbook covering discovery → design → build → secure → optimize → deploy → handoff

## Gap analysis against the requested coverage matrix

### A. Website types

| Website type | Status | Notes |
|---|---|---|
| Static/marketing sites, landing pages, portfolios, personal blogs | Partial | General frontend patterns exist, but no dedicated intake + starter workflow for marketing or portfolio builds |
| Documentation sites and knowledge bases | Partial | General docs guidance exists; no dedicated docs/site template or content-driven starter |
| Content sites/blogs with headless/file-based CMS | Missing | No CMS-first skill or starter for Markdown/Headless CMS content architecture |
| Business/corporate sites, nonprofit, church/community/association sites | Missing | No playbook for multi-page marketing + forms + trust-building workflows |
| E-commerce (catalog, cart, checkout, payments, inventory, orders) | Missing | No skill or starter for ecommerce lifecycle, payments, or order flows |
| SaaS web apps (auth, billing/subscriptions, multi-tenancy, dashboards, RBAC) | Missing | No app-type skill covering login, billing, tenant design, and product dashboards |
| Admin panels and internal tools | Partial | General backend/frontend patterns exist, but no admin-specific workflow or starter |
| Marketplaces and directories | Missing | No listing/search/review marketplace pattern |
| Booking/reservation/scheduling sites | Missing | No booking flow, calendar, availability, or payment cadence model |
| Social/community platforms, forums, membership sites | Missing | No community/forum or membership architecture playbook |
| LMS/e-learning, event/ticketing, real-estate, job boards, news/media | Missing | Domain-specific flows absent |
| Progressive Web Apps and offline-first apps | Missing | No PWA/offline-first skill, manifest/service-worker patterns, or starter |
| Real-time apps (chat, collaboration, live dashboards) | Missing | No WebSocket/SSE real-time workflow |
| AI-powered sites (chat UIs, RAG search, content generation, streaming responses) | Partial | There are general AI and content skills, but no web-specific AI app skill or starter |
| Data dashboards and analytics sites | Partial | Generic frontend + e2e/testing patterns exist, but no analytics-site workflow |
| Multilingual / multi-region sites | Missing | No i18n/RTL/SEO framework skill or release workflow |

### B. Stack coverage

| Stack / framework | Status | Notes |
|---|---|---|
| Plain HTML/CSS/JS | Partial | Generic frontend guidance exists; no concise starter package and validation flow |
| React | Partial | Frontend patterns exist; no complete website starter with rules and checks |
| Next.js (App Router, RSC, server actions) | Partial | `nextjs-turbopack` exists, but no complete starter + production conventions |
| Vite | Missing | No Vite starter workflow or stack-specific instructions |
| Vue/Nuxt | Partial | `nuxt4-patterns` exists; no complete project starter and web site delivery workflow |
| Svelte/SvelteKit | Missing | No skill or starter |
| Astro | Missing | No skill or starter |
| Remix | Missing | No skill or starter |
| Angular | Missing | No skill or starter |
| Solid | Missing | No skill or starter |
| WordPress | Missing | Should be covered as a handoff/implementation playbook, not necessarily a full framework starter |
| Shopify (Liquid/Hydrogen) | Missing | Same as above: likely a handoff skill without a deep repo starter |
| Webflow handoff | Missing | Should be included as a delivery playbook |
| Node (Express/Fastify/Nest) | Partial | Generic backend patterns exist; no complete site-specific backend starter |
| Python (Django/FastAPI/Flask) | Partial | Strong patterns exist for Django; others are not systematically covered |
| PHP (Laravel) | Partial | Strong Laravel coverage exists; needs project starter + web app flows |
| Go | Partial | General Go patterns exist, but not a website-specific stack template |
| Ruby on Rails | Missing | No Rails skill or template |
| Databases: PostgreSQL, MySQL, SQLite, MongoDB, Redis | Partial | Database skills exist but not site- and app-type-specific design flows |
| ORMs/query builders | Partial | Some patterns exist; no one-stop web stack field guide |
| BaaS: Supabase, Firebase, Appwrite | Missing | No integrated web app starter or auth/data patterns for BaaS |
| Styling: Tailwind, CSS Modules, shadcn/ui, design tokens | Partial | `design-system` exists; no default website UI starter package |
| APIs: REST, GraphQL, tRPC, WebSockets, SSE, webhooks | Partial | `api-design` exists, but not website-ready patterns and examples across all API modes |

### C. Cross-cutting capabilities required by the brief

| Capability | Status | Notes |
|---|---|---|
| Discovery and requirements | Partial | Planning skills exist; no structured web-specific intake and IA templates |
| Design systems | Partial | `design-system/` exists, but no website-specific token and component starter |
| Accessibility | Partial | Security and QA patterns exist, but no dedicated web a11y skill and audit checklist |
| Performance | Partial | `performance-optimizer` and optimization guidance exist, but no built-in web performance budget skill |
| SEO | Missing | No SEO skill or metadata checklist for web launches |
| Security | Partial | `security-review` exists; no explicit web security skill with OWASP/headers/CSP/authZ checklist |
| Auth | Missing | No auth playbook covering sessions/JWT/OIDC/passkeys/RBAC |
| Payments | Missing | No Stripe/Paystack/Flutterwave/PayPal playbook |
| Forms, email, notifications | Missing | No web forms and transactional messaging guidance |
| Data and CMS | Missing | No schema design, content modeling, media storage, or CMS workflow skill |
| Search | Missing | No full-text + vector search skill for web apps |
| Analytics, consent, and privacy | Missing | No GDPR/NDPR/CCPA or consent pattern |
| i18n/l10n and RTL | Missing | No site localization delivery workflow |
| Testing | Partial | `e2e-testing` and `quality-gate` exist, but not website-specific coverage and validation gates |
| DevOps | Partial | `deployment-patterns` exists but not the full website build/deploy lifecycle |
| Hosting guides | Partial | Deployment guidance exists; no hosting decision guide for web products |
| Maintenance | Missing | No handoff, uptime, dependency update, or operational maintenance playbook |
| Low-bandwidth and emerging-market considerations | Missing | No lightweight/mobile-first/offline/low-data guidance |

## Conclusion

The repo already has a strong general-purpose ECC infrastructure and a useful set of framework patterns. However, it is not yet a complete website-building harness. The current content is broad and reusable, but the gaps are concentrated in the exact areas the objective requires: website-type-specific playbooks, stack-specific starter templates, cross-cutting web standards, and deployment-to-production coverage.

## Prioritized change plan

### Priority 1 — Create the web foundation

1. Add `skills/web-discovery/` and `skills/web-design-system/`.
2. Add `skills/web-accessibility/`, `skills/web-seo/`, `skills/web-performance/`, `skills/web-security/`.
3. Add shared command files for `/new-site`, `/plan-site`, `/design-system`, `/a11y-audit`, `/seo-audit`, `/perf-audit`, `/security-audit`, `/test-site`, `/deploy`, `/launch-checklist`, `/handoff-docs`.
4. Add a master orchestration playbook under `docs/` or `skills/`.

### Priority 2 — Fill type coverage

Create one skill and starter template per major website type, beginning with:

- marketing/landing pages
- documentation site
- business/corporate site
- blog/content site
- e-commerce
- SaaS app
- admin dashboard
- marketplace/directory
- booking/scheduling
- AI-powered site
- analytics dashboard

### Priority 3 — Fill stack coverage

Add default starter packs for the most important stacks:

- plain HTML/CSS/JS
- React + Vite
- Next.js App Router
- Astro
- Vue/Nuxt
- SvelteKit
- Node + Express/Fastify/Nest
- Django + DRF or Flask
- Laravel
- Supabase + Postgres

### Priority 4 — Add Copilot and Claude parity

Update `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.github/prompts/*.prompt.md`, `.github/agents/*.agent.md`, and keep `AGENTS.md` synchronized with a generated source-of-truth workflow.

### Priority 5 — Add validation, CI, and starter verification

Extend the Node validation script to check:

- frontmatter validity
- unique skill/agent names
- broken relative links
- starter install/build success
- hook and secret-scan gate compliance

## Intentionally out of scope or “handoff-only” coverage

These should be documented as handoff playbooks rather than deep built-from-scratch starters unless the project explicitly shifts to a CMS-first distribution model:

- WordPress theme/plugin work
- Shopify Liquid/Hydrogen storefront work
- Webflow handoff and implementation guidance
- highly specialized domain sites (e.g., internal enterprise portals) can be built as domain variants of the shared starter base, but they do not require separate top-level repo conventions

This keeps the repo aligned with its existing conventions: general-purpose skills and commands, extended by concrete website implementation playbooks rather than a foreign framework layout.

## Proposed implementation structure

The repo should grow by extension, not by new top-level architecture. The most natural structure is:

```text
agents/
  web-architect.md
  frontend-engineer.md
  backend-engineer.md
  ui-ux-designer.md
  accessibility-auditor.md
  seo-specialist.md
  security-reviewer-web.md
  performance-engineer.md
  devops-deployer.md
  qa-e2e-tester.md
  content-strategist.md

skills/
  web-discovery/
  web-design-system/
  web-accessibility/
  web-seo/
  web-performance/
  web-security/
  web-auth/
  web-payments/
  web-forms-email/
  web-cms-data/
  web-search/
  web-analytics-privacy/
  web-i18n/
  web-testing/
  web-devops/
  web-hosting/
  web-maintenance/
  web-low-bandwidth/
  marketing-site/
  docs-site/
  content-site/
  business-site/
  ecommerce-site/
  saas-app/
  admin-dashboard/
  marketplace-site/
  booking-site/
  ai-site/
  analytics-dashboard/
  html-css-js-starter/
  react-vite-starter/
  nextjs-app-router-starter/
  astro-starter/
  nuxt-starter/
  sveltekit-starter/
  node-express-starter/
  django-starter/
  laravel-starter/

commands/
  new-site.md
  plan-site.md
  add-feature.md
  design-system.md
  a11y-audit.md
  seo-audit.md
  perf-audit.md
  security-audit.md
  test-site.md
  deploy.md
  launch-checklist.md
  handoff-docs.md

examples/
  web-starters/
    marketing-basic/
    ecommerce-basic/
    saas-basic/
    docs-site-basic/

hooks/
  pre-commit-web-checks.sh

rules/
  web-accessibility.md
  web-security.md
  web-performance.md

.github/
  copilot-instructions.md
  instructions/
  prompts/
  agents/

.docs/
  WEB_COVERAGE_AUDIT.md
  ARCHITECTURE.md
```

This plan stays consistent with the existing repo conventions instead of creating a new framework or a parallel product structure.
