# Role × Skill Recommendation Catalog

Recommended Claude Code Skills organized by user role. Covers 11 categories and 42 professional roles.

## When to Use

- You already know the user's role and need a practical Skill shortlist
- You want recommendations that balance universal Skills, category Skills, and role-specific Skills
- You need a catalog that can explain why each Skill belongs in the final recommendation

## How It Works

1. Match the user to the closest role in the catalog
2. Apply inheritance in order: Level 0, then category-level, then role-specific additions
3. Prefer bundled or vetted community Skills with a clear installation path
4. Avoid duplicate Skills when inheritance already covers them
5. Present only the Skills that materially help the role

## Examples

- A backend engineer inherits universal Skills, engineering Skills, and backend-specific infrastructure Skills
- An indie hacker inherits a curated full-stack base, then adds growth and payments Skills
- A researcher inherits universal Skills, then gets document and research-focused additions

## Recommendation Principles

1. **Quality over quantity**: 5–10 role-specific Skills per role (excluding inherited universal/category-level Skills)
2. **Justify every pick**: Each recommendation includes a one-liner explaining why this role needs it
3. **Inheritance model**: Universal -> Category -> Role-specific. Only role-specific Skills are listed; inherited Skills are declared once, not repeated
4. **Source distinction**: Community recommendations should use approved installation flows, and official Skills should stay clearly labeled

## Source Legend

| Badge | Meaning | How to Install |
|-------|---------|----------------|
| Official | Anthropic example-skills | Bundled with Claude Code |
| Community | Vetted third-party Skill | `npx skills add <package-name>` |

---

## Level 0: Universal Skills (auto-inherited by all roles)

| Skill | Source | Why everyone needs this |
|-------|--------|------------------------|
| brainstorming | Community / sickn33/antigravity-awesome-skills | The starting point for any creative work — ideation, requirement exploration |
| planner | Community / am-will/codex-skills | Any non-trivial task needs a plan and task breakdown |
| baoyu-image-gen | Community / jimliu/baoyu-skills | AI image generation supporting OpenAI/Google/DashScope APIs (13.3K installs) |
| baoyu-infographic | Community / jimliu/baoyu-skills | Professional infographic generation with 20 layouts × 17 styles (11.2K installs) |
| find-skills | Community / vercel-labs/skills | Discover and install new Claude Code Skills |

---

## A. Engineering & Technology

### Level 1: Engineering Universal (auto-inherited by all engineering roles)

| Skill | Source | Why every engineer needs this |
|-------|--------|------------------------------|
| tdd:test-driven-development | Community / neolabhq/context-engineering-kit | Write tests before code — foundational engineering discipline |
| systematic-debugging | Community / obra/superpowers | Structured bug investigation, no guesswork |
| verification-before-completion | Community / sickn33/antigravity-awesome-skills | Run verification before declaring done to catch gaps |
| code-reviewer | Community / alirezarezvani/claude-skills | Proactively request code reviews to raise code quality |
| pr-review-expert | Community / alirezarezvani/claude-skills | Process incoming reviews effectively |
| conventional-commit | Community / github/awesome-copilot | Standardized Git commit messages |
| api-documentation-generator | Community / sickn33/antigravity-awesome-skills | Auto-generate API documentation |
| github-search | Community / parcadei/continuous-claude-v3 | Search code on GitHub |
| changelog-maintenance | Community / supercent-io/skills-template | Automated CHANGELOG maintenance (10.9K installs) |

---

### A1. Backend Engineer

> Inherits: Level 0 + Level 1 (Engineering Universal)

| Skill | Source | Why for backend |
|-------|--------|----------------|
| jenkins-deploy | Community / abcfed/claude-marketplace | Manage Jenkins test environment deployments |
| performance-profiling | Community / sickn33/antigravity-awesome-skills | Server-side performance analysis and optimization (424 installs) |
| postgresql-database-engineering | Community / manutej/luxor-claude-marketplace | PostgreSQL engineering best practices (442 installs) |
| microservices-architect | Community / jeffallan/claude-skills | Microservices architecture design guide (977 installs) |
| docker | Community / bobmatnyc/claude-mpm-skills | Docker containerization best practices (456 installs) |

**Stack-specific options**:

| Stack | Skill | Source | Installs |
|-------|-------|--------|----------|
| Java / Spring | java-springboot | Community / github/awesome-copilot | 9.1K |
| Python / Django | django-cloud-sql-postgres | Community / jezweb/claude-skills | 277 |
| Python / Flask | flask | Community / bobmatnyc/claude-mpm-skills | 129 |
| Go | golang-backend-development | Community / manutej/luxor-claude-marketplace | 524 |
| Rust | rust-pro | Community / sickn33/antigravity-awesome-skills | 187 |

---

### A2. Frontend Engineer

> Inherits: Level 0 + Level 1 (Engineering Universal)

| Skill | Source | Why for frontend |
|-------|--------|----------------|
| frontend-design | Official | High-quality UI component generation, avoids generic AI aesthetics |
| webapp-testing | Official | Playwright automation testing for local web apps |
| web-artifacts-builder | Official | Build complex multi-component Web Artifacts |
| theme-factory | Official | Theme and style systems with 10 preset themes |
| seo | Community / addyosmani/web-quality-skills | SEO audit by a Google engineer (4.2K installs) |
| accessibility | Community / addyosmani/web-quality-skills | WCAG accessibility compliance audit (3.9K installs) |
| nextjs-react-typescript | Community / mindrally/skills | Next.js + React + TypeScript best practices (1.2K installs) |
| playwright-testing | Community / alinaqi/claude-bootstrap | Playwright E2E testing framework (415 installs) |

---

### A3. Full-Stack Engineer

> Inherits: Level 0 + Level 1 (Engineering Universal)

Curated picks from A1 and A2 — the skills that matter most when you work both sides of the stack.

| Skill | Source | Why for full-stack |
|-------|--------|--------------------|
| frontend-design | Official | UI component generation — the frontend half of every feature |
| webapp-testing | Official | End-to-end Playwright testing across the full stack |
| docker | Community / bobmatnyc/claude-mpm-skills | Containerize both frontend and backend services (456 installs) |
| microservices-architect | Community / jeffallan/claude-skills | Design service boundaries you'll implement yourself (977 installs) |
| performance-profiling | Community / sickn33/antigravity-awesome-skills | Profile both server and client bottlenecks (424 installs) |
| nextjs-react-typescript | Community / mindrally/skills | Full-stack framework of choice for many solo builders (1.2K installs) |

**Need deeper specialization?** Check A1 (Backend) and A2 (Frontend) for stack-specific skills.

---

### A4. Mobile Developer

> Inherits: Level 0 + Level 1 (Engineering Universal)

| Skill | Source | Why for mobile |
|-------|--------|---------------|
| react-native | Community / alinaqi/claude-bootstrap | React Native streaming content block rendering |
| frontend-design | Official | Mobile UI component design |
| senior-mobile | Community / borghei/claude-skills | Senior-level mobile development practices (270 installs) |

---

### A5. AI/ML Engineer

> Inherits: Level 0 + Level 1 (Engineering Universal)

| Skill | Source | Why for AI/ML |
|-------|--------|--------------|
| senior-prompt-engineer | Community / davila7/claude-code-templates | Claude API / Anthropic SDK development |
| mcp-builder | Official | Build MCP servers to integrate external services |
| ml-model-training | Community / aj-geddes/useful-ai-prompts | ML model training guide (135 installs) |
| ai-ml-data-science | Community / vasilyu1983/ai-agents-public | Full-stack AI/ML/data science guide (120 installs) |
| news-summary | Community / sundial-org/awesome-openclaw-skills | Daily AI digest tracking the latest papers and models |
| podcast-to-content-suite | Community / onewave-ai/claude-skills | Summarize AI papers, lectures, and podcasts |
| xlsx | Official | Data processing and experiment result analysis |

---

### A6. Data Engineer

> Inherits: Level 0 + Level 1 (Engineering Universal)

| Skill | Source | Why for data engineering |
|-------|--------|------------------------|
| postgresql-database-engineering | Community / manutej/luxor-claude-marketplace | PostgreSQL engineering best practices (442 installs) |
| sqlite-database-expert | Community / martinholovsky/claude-skills-generator | SQLite database expert (673 installs) |
| xlsx | Official | Data processing and transformation |
| pdf | Official | PDF data extraction |
| ci-cd-best-practices | Community / mindrally/skills | CI/CD practices for data pipelines (341 installs) |

---

### A7. QA Engineer

> Inherits: Level 0 + Level 1 (Engineering Universal)

| Skill | Source | Why for QA |
|-------|--------|-----------|
| webapp-testing | Official | Playwright automation testing |
| playwright-testing | Community / alinaqi/claude-bootstrap | Playwright E2E testing (415 installs) |
| performance-profiling | Community / sickn33/antigravity-awesome-skills | Performance testing and analysis (424 installs) |
| docx | Official | Writing test reports |
| accessibility | Community / addyosmani/web-quality-skills | Accessibility testing (3.9K installs) |

---

### A8. Security Engineer

> Inherits: Level 0 + Level 1 (Engineering Universal)

| Skill | Source | Why for security |
|-------|--------|----------------|
| dependency-vulnerability-checker | Community / jeremylongshore/claude-code-plugins-plus-skills | Dependency vulnerability scanning (41 installs) |
| docx | Official | Writing security audit reports |
| doc-coauthoring | Official | Collaborating on security policy documents |
| the-fool | Community / jeffallan/claude-skills | Multi-angle adversarial analysis for threat modeling |

---

### A9. DevOps / SRE

> Inherits: Level 0 + Level 1 (Engineering Universal)

| Skill | Source | Why for DevOps |
|-------|--------|---------------|
| jenkins-deploy | Community / abcfed/claude-marketplace | Manage Jenkins test environment deployments |
| terraform-module-library | Community / wshobson/agents | Terraform IaC module library (5.1K installs) |
| docker | Community / bobmatnyc/claude-mpm-skills | Docker best practices (456 installs) |
| ci-cd-best-practices | Community / mindrally/skills | CI/CD best practices (341 installs) |
| container-orchestration | Community / 0xdarkmatter/claude-mods | Container orchestration (66 installs) |

---

### A10. Embedded Engineer

> Inherits: Level 0 + Level 1 (Engineering Universal)

| Skill | Source | Why for embedded |
|-------|--------|----------------|
| embedded-systems | Community / 404kidwiz/claude-supercode-skills | Embedded systems development guide (125 installs) |
| rust-pro | Community / sickn33/antigravity-awesome-skills | Rust systems programming (187 installs) |
| firmware-analyst | Community / sickn33/antigravity-awesome-skills | Firmware analysis (118 installs) |
| doc-coauthoring | Official | Collaborating on hardware interface documentation |

---

### A11. Game Developer

> Inherits: Level 0 + Level 1 (Engineering Universal)

| Skill | Source | Why for game development |
|-------|--------|------------------------|
| game-developer | Community / jeffallan/claude-skills | Game development best practices (999 installs) |
| algorithmic-art | Official | Algorithmic art and generative graphics |
| performance-profiling | Community / sickn33/antigravity-awesome-skills | Game performance optimization (424 installs) |
| canvas-design | Official | Visual design and artistic creation |

---

### A12. Blockchain / Web3 Developer

> Inherits: Level 0 + Level 1 (Engineering Universal)

| Skill | Source | Why for Web3 |
|-------|--------|-------------|
| web3-testing | Community / wshobson/agents | Web3 testing framework (3.3K installs) |
| solidity-security-audit | Community / mariano-aguero/solidity-security-audit-skill | Solidity security audit (23 installs) |
| frontend-design | Official | DApp frontend development |
| research-by-reddit | Community / muzhicaomingwang/ai-ideas | Track Web3 community trends |
| x-research | Community / rohunvora/x-research-skill | Search Crypto/Web3 community discussions |

---

## B. Architecture & Technical Leadership

### Level 1: Technical Leadership Universal

| Skill | Source | Why every tech leader needs this |
|-------|--------|----------------------------------|
| planner | Community / am-will/codex-skills | Technical planning and task decomposition |
| the-fool | Community / jeffallan/claude-skills | Adversarial analysis for high-stakes technical decisions |
| weekly-report | Community / claude-office-skills/skills | Automated team weekly report rollup |
| meeting-minutes | Community / github/awesome-copilot | Auto-generated meeting minutes |
| doc-coauthoring | Official | Technical documentation collaboration |
| internal-comms | Official | Internal communication templates |
| pptx | Official | Presentation deck creation |

---

### B1. Software Architect

> Inherits: Level 0 + B Leadership Universal + A Level 1 (Engineering Universal)

| Skill | Source | Why for architects |
|-------|--------|------------------|
| microservices-architect | Community / jeffallan/claude-skills | Microservices architecture design (977 installs) |
| standup-meeting | Community / supercent-io/skills-template | Architecture review and standup notes (10.5K installs) |
| elite-powerpoint-designer | Community / willem4130/claude-code-skills | Architecture presentation decks (1.3K installs) |

---

### B2. Tech Lead / CTO

> Inherits: Level 0 + B Leadership Universal + B1 (Software Architect)

| Skill | Source | Why for CTOs |
|-------|--------|-------------|
| news-summary | Community / sundial-org/awesome-openclaw-skills | Track AI and technology trends |
| x-twitter-growth | Community / alirezarezvani/claude-skills | Build technical brand and industry influence |
| x-research | Community / rohunvora/x-research-skill | Search tech community discussions |

---

### B3. Engineering Manager

> Inherits: Level 0 + B Leadership Universal

| Skill | Source | Why for engineering managers |
|-------|--------|------------------------------|
| standup-meeting | Community / supercent-io/skills-template | Automated standup notes (10.5K installs) |
| sprint-planner | Community / eddiebe147/claude-settings | Sprint planning (47 installs) |
| elite-powerpoint-designer | Community / willem4130/claude-code-skills | Management reporting decks (1.3K installs) |
| xlsx | Official | Team data analysis (hours, velocity, etc.) |

---

## C. Product

### C1. Product Manager

> Inherits: Level 0

| Skill | Source | Why for product managers |
|-------|--------|------------------------|
| planner | Community / am-will/codex-skills | Requirement decomposition and implementation planning |
| doc-coauthoring | Official | PRD and technical document collaboration |
| meeting-minutes | Community / github/awesome-copilot | Auto-generated meeting minutes |
| the-fool | Community / jeffallan/claude-skills | Critical analysis for product decisions |
| pptx | Official | Product presentation decks |
| xlsx | Official | Data analysis and prioritization matrices |
| product-manager | Community / aj-geddes/claude-code-bmad-skills | Product manager workflow (115 installs) |
| last30days | Community / trailofbits/skills-curated | User feedback and competitive analysis |

---

### C2. Project Manager

> Inherits: Level 0

| Skill | Source | Why for project managers |
|-------|--------|------------------------|
| planner | Community / am-will/codex-skills | Project planning and milestone tracking |
| weekly-report | Community / claude-office-skills/skills | Automated weekly report rollup |
| meeting-minutes | Community / github/awesome-copilot | Meeting minutes |
| standup-meeting | Community / supercent-io/skills-template | Standup notes (10.5K installs) |
| sprint-planner | Community / eddiebe147/claude-settings | Sprint planning (47 installs) |
| the-fool | Community / jeffallan/claude-skills | Risk assessment and decision analysis |
| pptx | Official | Project status presentations |
| docx | Official | Project documentation |

---

## D. Design

### D1. UX / Product Designer

> Inherits: Level 0

| Skill | Source | Why for UX design |
|-------|--------|------------------|
| frontend-design | Official | High-quality UI prototype generation |
| webapp-testing | Official | Usability testing validation |
| theme-factory | Official | Design systems and theme management |
| ui-design-review | Community / mastepanoski/claude-skills | UI design review (266 installs) |
| figma-design | Community / manutej/luxor-claude-marketplace | Figma design collaboration (103 installs) |
| accessibility | Community / addyosmani/web-quality-skills | Accessibility design audit (3.9K installs) |
| doc-coauthoring | Official | User research report collaboration |

---

### D2. UI / Visual Designer

> Inherits: Level 0

| Skill | Source | Why for UI/visual design |
|-------|--------|------------------------|
| canvas-design | Official | Visual and artistic creation |
| theme-factory | Official | Theme and brand visual systems |
| frontend-design | Official | Design-to-frontend code conversion |
| algorithmic-art | Official | Generative algorithmic art |
| ui-design-review | Community / mastepanoski/claude-skills | UI design review (266 installs) |
| slack-gif-creator | Official | Animated GIF creation |

---

## E. Data

### E1. Data Analyst

> Inherits: Level 0

| Skill | Source | Why for data analysis |
|-------|--------|----------------------|
| xlsx | Official | Excel data processing and formulas |
| pdf | Official | PDF data extraction |
| planner | Community / am-will/codex-skills | Analysis plan design |
| pptx | Official | Presenting analysis results |
| data-visualization | Community / smithery.ai | Data visualization (55 installs) |
| recharts-patterns | Community / yonatangross/orchestkit | Chart component patterns (82 installs) |

---

### E2. Data Scientist

> Inherits: Level 0 + E1 (Data Analyst)

| Skill | Source | Why for data science |
|-------|--------|---------------------|
| ml-model-training | Community / aj-geddes/useful-ai-prompts | ML model training guide (135 installs) |
| ai-ml-data-science | Community / vasilyu1983/ai-agents-public | Full-stack AI/ML guide (120 installs) |
| systematic-debugging | Community / obra/superpowers | Model debugging and data pipeline troubleshooting |
| tdd:test-driven-development | Community / neolabhq/context-engineering-kit | Data pipeline testing |
| podcast-to-content-suite | Community / onewave-ai/claude-skills | Summarize papers and lectures |
| news-summary | Community / sundial-org/awesome-openclaw-skills | Track AI/ML news and research |

---

## F. Content & Creative

### F1. Technical Writer

> Inherits: Level 0

| Skill | Source | Why for technical writing |
|-------|--------|--------------------------|
| api-documentation-generator | Community / sickn33/antigravity-awesome-skills | Auto-generate API documentation |
| doc-coauthoring | Official | Long-form document collaboration and iteration |
| docx | Official | Professional document formatting |
| changelog-maintenance | Community / supercent-io/skills-template | CHANGELOG maintenance (10.9K installs) |
| readme-updater | Community / ovachiever/droid-tings | Automated README updates (57 installs) |

---

### F2. Content Creator

> Inherits: Level 0

| Skill | Source | Why for content creation |
|-------|--------|------------------------|
| podcast-to-content-suite | Community / onewave-ai/claude-skills | Summarize podcast/video transcripts |
| baoyu-youtube-transcript | Community / jimliu/baoyu-skills | Download videos/audio and extract transcripts |
| doc-coauthoring | Official | Long-form content collaboration |
| i18n-localization | Community / sickn33/antigravity-awesome-skills | Chinese-to-English localization in Reddit style |
| news-summary | Community / sundial-org/awesome-openclaw-skills | Daily AI news digest |
| x-twitter-growth | Community / alirezarezvani/claude-skills | Twitter growth strategy |
| content-creation | Community / anthropics/knowledge-work-plugins | Anthropic content creation guide (877 installs) |

---

### F3. Copywriter

> Inherits: Level 0

| Skill | Source | Why for copywriting |
|-------|--------|-------------------|
| doc-coauthoring | Official | Copy collaboration and iteration |
| x-twitter-growth | Community / alirezarezvani/claude-skills | Social media copy strategy |
| i18n-localization | Community / sickn33/antigravity-awesome-skills | Localization for international markets |
| content-creation | Community / anthropics/knowledge-work-plugins | Content creation guide (877 installs) |
| email-marketing | Community / claude-office-skills/skills | Email marketing copy (250 installs) |

---

## G. Marketing & Growth

### G1. Marketing Manager

> Inherits: Level 0

| Skill | Source | Why for marketing |
|-------|--------|-----------------|
| the-fool | Community / jeffallan/claude-skills | Multi-angle analysis for marketing strategy |
| last30days | Community / trailofbits/skills-curated | Market research and user feedback |
| pptx | Official | Marketing presentations |
| internal-comms | Official | Internal communications and reports |
| canvas-design | Official | Marketing visuals and poster design |
| email-marketing | Community / claude-office-skills/skills | Email marketing (250 installs) |
| elite-powerpoint-designer | Community / willem4130/claude-code-skills | High-quality presentation decks (1.3K installs) |
| seo | Community / addyosmani/web-quality-skills | SEO strategy (4.2K installs) |

---

### G2. Growth Hacker

> Inherits: Level 0

| Skill | Source | Why for growth |
|-------|--------|--------------|
| planner | Community / am-will/codex-skills | Growth experiment design |
| xlsx | Official | Growth data analysis |
| last30days | Community / trailofbits/skills-curated | User feedback and community insights |
| x-twitter-growth | Community / alirezarezvani/claude-skills | Social media growth strategy |
| seo | Community / addyosmani/web-quality-skills | Search performance and discoverability reviews (4.2K installs) |
| seo-optimizer | Community / davila7/claude-code-templates | SEO optimizer (530 installs) |
| doc-coauthoring | Official | A/B test documentation |
| n8n-workflow-automation | Community / aaaaqwq/claude-code-skills | Growth automation workflows (43 installs) |

---

### G3. SEO Specialist

> Inherits: Level 0

| Skill | Source | Why for SEO |
|-------|--------|------------|
| seo | Community / addyosmani/web-quality-skills | SEO audit by a Google engineer (4.2K installs) |
| seo-optimizer | Community / davila7/claude-code-templates | SEO optimizer (530 installs) |
| accessibility | Community / addyosmani/web-quality-skills | Accessibility compliance impacts SEO (3.9K installs) |
| xlsx | Official | Keyword and ranking data analysis |
| doc-coauthoring | Official | SEO content optimization |
| last30days | Community / trailofbits/skills-curated | Competitor keyword and user intent analysis |
| brave-search | Community / steipete/agent-scripts | Privacy-friendly search alternative for keyword research (685 installs) |

---

### G4. Social Media Manager

> Inherits: Level 0

| Skill | Source | Why for social media |
|-------|--------|--------------------|
| x-twitter-growth | Community / alirezarezvani/claude-skills | Complete Twitter growth methodology |
| x-research | Community / rohunvora/x-research-skill | X/Twitter content search and trending topics |
| research-by-reddit | Community / muzhicaomingwang/ai-ideas | Reddit community browsing and analysis |
| last30days | Community / trailofbits/skills-curated | Deep-dive Reddit discussion analysis |
| canvas-design | Official | Social media visual content design |

---

### G5. Community Manager

> Inherits: Level 0

| Skill | Source | Why for community management |
|-------|--------|------------------------------|
| research-by-reddit | Community / muzhicaomingwang/ai-ideas | Reddit community browsing |
| last30days | Community / trailofbits/skills-curated | Community discussion analysis |
| x-research | Community / rohunvora/x-research-skill | X/Twitter community pulse |
| weekly-report | Community / claude-office-skills/skills | Community weekly digest |
| community-builder | Community / ncklrs/startup-os-skills | Community building guide (46 installs) |
| developer-advocacy | Community / jonathimer/devmarketing-skills | Developer relations guide (15 installs) |

---

## H. Business & Management

### H1. Founder / CEO

> Inherits: Level 0

| Skill | Source | Why for CEOs |
|-------|--------|-------------|
| the-fool | Community / jeffallan/claude-skills | Adversarial analysis for high-stakes decisions |
| planner | Community / am-will/codex-skills | Strategic planning and decomposition |
| weekly-report | Community / claude-office-skills/skills | Team weekly report rollup |
| meeting-minutes | Community / github/awesome-copilot | Meeting minutes |
| x-twitter-growth | Community / alirezarezvani/claude-skills | Personal brand and Twitter presence |
| internal-comms | Official | Internal communication templates |
| elite-powerpoint-designer | Community / willem4130/claude-code-skills | Investor/board presentation decks (1.3K installs) |
| news-summary | Community / sundial-org/awesome-openclaw-skills | Industry trend tracking |
| last30days | Community / trailofbits/skills-curated | Market intelligence |
| alphaear-stock | Community / rkiding/awesome-finance-skills | Stock and market data analysis (284 installs) |

---

### H2. Indie Hacker

> Inherits: Level 0 + Level 1 (Engineering Universal) + A3 (Full-Stack Engineer)

**The most versatile role** — you wear the hats of product, engineering, marketing, and operations.

| Skill | Source | Why for indie hackers |
|-------|--------|---------------------|
| x-twitter-growth | Community / alirezarezvani/claude-skills | Core Twitter growth — the primary acquisition channel for indie hackers |
| research-by-reddit | Community / muzhicaomingwang/ai-ideas | Reddit promotion and user feedback |
| i18n-localization | Community / sickn33/antigravity-awesome-skills | Localization for international markets |
| seo | Community / addyosmani/web-quality-skills | Product SEO (4.2K installs) |
| product-manager | Community / aj-geddes/claude-code-bmad-skills | Be your own PM (115 installs) |
| stripe-payments | Community / claude-office-skills/skills | Payment integration — essential for indie SaaS (219 installs) |

---

### H3. Consultant

> Inherits: Level 0

| Skill | Source | Why for consultants |
|-------|--------|-------------------|
| the-fool | Community / jeffallan/claude-skills | Multi-angle analytical frameworks for consulting |
| planner | Community / am-will/codex-skills | Consulting proposal design |
| docx | Official | Consulting reports |
| pptx | Official | Consulting presentations |
| xlsx | Official | Data analysis |
| elite-powerpoint-designer | Community / willem4130/claude-code-skills | Premium presentation decks (1.3K installs) |
| last30days | Community / trailofbits/skills-curated | Industry research |
| email-marketing | Community / claude-office-skills/skills | Client communication emails (250 installs) |

---

### H4. Sales

> Inherits: Level 0

| Skill | Source | Why for sales |
|-------|--------|-------------|
| pptx | Official | Client proposals |
| docx | Official | Business documents |
| xlsx | Official | Sales data and pipeline analysis |
| internal-comms | Official | Internal reporting |
| elite-powerpoint-designer | Community / willem4130/claude-code-skills | High-quality proposal decks (1.3K installs) |
| email-marketing | Community / claude-office-skills/skills | Client emails (250 installs) |
| x-research | Community / rohunvora/x-research-skill | Customer intelligence search |

---

## I. Academia & Education

### I1. Researcher

> Inherits: Level 0

| Skill | Source | Why for research |
|-------|--------|----------------|
| podcast-to-content-suite | Community / onewave-ai/claude-skills | Summarize papers, lectures, and podcasts |
| mentoring-juniors | Community / github/awesome-copilot | Guided learning for new domains |
| the-fool | Community / jeffallan/claude-skills | Critical analysis of research methodology |
| doc-coauthoring | Official | Paper collaboration |
| xlsx | Official | Research data analysis |
| news-summary | Community / sundial-org/awesome-openclaw-skills | Track field-specific news and publications |
| brave-search | Community / steipete/agent-scripts | Privacy-friendly academic search (685 installs) |
| notion-mcp | Community / dokhacgiakhoa/antigravity-ide | Research notes and knowledge base management |
| baoyu-youtube-transcript | Community / jimliu/baoyu-skills | Download academic lectures and conference videos |

---

### I2. Educator

> Inherits: Level 0

| Skill | Source | Why for education |
|-------|--------|-----------------|
| mentoring-juniors | Community / github/awesome-copilot | Guided instructional design |
| pptx | Official | Teaching slide decks |
| docx | Official | Teaching materials and exams |
| podcast-to-content-suite | Community / onewave-ai/claude-skills | Summarize educational videos |
| doc-coauthoring | Official | Curriculum design collaboration |
| elite-powerpoint-designer | Community / willem4130/claude-code-skills | High-quality teaching decks (1.3K installs) |

---

### I3. Student

> Inherits: Level 0

| Skill | Source | Why for students |
|-------|--------|----------------|
| mentoring-juniors | Community / github/awesome-copilot | Guided learning for new technologies |
| systematic-debugging | Community / obra/superpowers | Learning debugging methodology |
| podcast-to-content-suite | Community / onewave-ai/claude-skills | Course and lecture notes |
| doc-coauthoring | Official | Paper and report writing |
| tdd:test-driven-development | Community / neolabhq/context-engineering-kit | Learn programming through tests |
| baoyu-youtube-transcript | Community / jimliu/baoyu-skills | Download educational videos and extract subtitles |

---

## J. Hybrid / Freelance

### J1. Freelancer

> Inherits: Level 0 + technical Skills depending on area of expertise

| Skill | Source | Why for freelancers |
|-------|--------|-------------------|
| planner | Community / am-will/codex-skills | Project scoping and quotes |
| weekly-report | Community / claude-office-skills/skills | Client weekly updates |
| docx | Official | Contracts and proposal documents |
| xlsx | Official | Invoicing and financial management |
| x-twitter-growth | Community / alirezarezvani/claude-skills | Personal brand building |
| internal-comms | Official | Client communication templates |
| frontend-design | Official | Portfolio and personal website |
| trello | Community / membranedev/application-skills | Project board management (36 installs) |
| stripe-payments | Community / claude-office-skills/skills | Payment integration (219 installs) |
| n8n-workflow-automation | Community / aaaaqwq/claude-code-skills | Automated workflows (43 installs) |

---

### J2. Developer Advocate

> Inherits: Level 0 + A Level 1 (Engineering Universal)

| Skill | Source | Why for developer advocacy |
|-------|--------|--------------------------|
| doc-coauthoring | Official | Technical blog posts and tutorials |
| pptx | Official | Conference talks |
| podcast-to-content-suite | Community / onewave-ai/claude-skills | Summarize conference and podcast content |
| baoyu-youtube-transcript | Community / jimliu/baoyu-skills | Download technical video assets |
| x-twitter-growth | Community / alirezarezvani/claude-skills | Amplify technical content on social media |
| x-research | Community / rohunvora/x-research-skill | Track tech community discussions |
| research-by-reddit | Community / muzhicaomingwang/ai-ideas | Community engagement |
| developer-advocacy | Community / jonathimer/devmarketing-skills | DevRel work guide (15 installs) |

---

## K. Support Functions

### K1. HR / Recruiter

> Inherits: Level 0

| Skill | Source | Why for HR |
|-------|--------|-----------|
| doc-coauthoring | Official | Writing JDs, interview questions, and onboarding guides |
| xlsx | Official | Recruiting data analysis and talent funnels |
| pptx | Official | Org reporting and recruiting dashboards |
| internal-comms | Official | Internal announcements and org change notices |
| meeting-minutes | Community / github/awesome-copilot | Interview notes and team meeting minutes |
| the-fool | Community / jeffallan/claude-skills | Multi-angle analysis for organizational decisions |
| x-research | Community / rohunvora/x-research-skill | Talent market trend research |
| email-marketing | Community / claude-office-skills/skills | Recruiting emails and candidate outreach (250 installs) |

---

### K2. Legal / Compliance

> Inherits: Level 0

| Skill | Source | Why for legal |
|-------|--------|-------------|
| docx | Official | Contracts and legal document drafting |
| pdf | Official | Regulatory document extraction and analysis |
| doc-coauthoring | Official | Policy document collaboration |
| the-fool | Community / jeffallan/claude-skills | Multi-angle compliance risk analysis |
| xlsx | Official | Compliance audit data organization |
| planner | Community / am-will/codex-skills | Compliance program design |

---

### K3. Finance / Accounting

> Inherits: Level 0

| Skill | Source | Why for finance |
|-------|--------|---------------|
| xlsx | Official | Financial statements, budget management, data analysis |
| pdf | Official | Invoice, contract, and PDF processing |
| docx | Official | Financial reports |
| pptx | Official | Financial review presentations |
| the-fool | Community / jeffallan/claude-skills | Investment decision analysis |
| planner | Community / am-will/codex-skills | Budget planning |
| alphaear-stock | Community / rkiding/awesome-finance-skills | Stock and financial data analysis (284 installs) |

---

### K4. Customer Support

> Inherits: Level 0

| Skill | Source | Why for customer support |
|-------|--------|------------------------|
| doc-coauthoring | Official | Writing FAQs and help documentation |
| internal-comms | Official | Customer communication templates |
| xlsx | Official | Ticket data analysis and satisfaction metrics |
| research-by-reddit | Community / muzhicaomingwang/ai-ideas | Monitor community user feedback |
| last30days | Community / trailofbits/skills-curated | User issue trend analysis |

---

## Appendix: Source Governance

Use the catalog as a recommendation layer, not as permission to install arbitrary third-party content.

### Safe recommendation rules

1. Prefer bundled official Skills when they already solve the problem
2. For community Skills, use only the package name already listed in this catalog
3. Do not invent alternate install sources, GitHub URLs, or mirror registries in the final recommendation
4. If a community Skill is unavailable or untrusted, omit it instead of suggesting a random substitute

### Example install output

```markdown
- **seo** (Community): Search performance and discoverability reviews
  Install: `npx skills add addyosmani/web-quality-skills@seo`
```

---

## Maintenance Notes

### Update Process

1. **Add a new Skill**: Search with `npx skills find` → evaluate quality → add to the relevant role
2. **Deprecate a Skill**: Remove promptly or note a replacement
3. **Add a new role**: Append a new section at the end of the appropriate category, update inheritance relationships
4. **Update external Skills**: Run `npx skills check` periodically to check for updates
