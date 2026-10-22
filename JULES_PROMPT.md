GOAL
Turn the attached single-file prototype (`index.html`), a family tree app
called "Roots," into a real, deployable, multi-user, multi-tree web
application with a persistent backend. Keep the visual design, copy,
layout, and interaction patterns pixel-for-pixel identical — this is a
backend/persistence/auth/infrastructure migration, not a redesign. Treat
`index.html` as the frontend behavior specification: every function and
data shape described below refers to the actual code in that file, so
read it in full before proposing a schema or API.

═══════════════════════════════════════════
1. CURRENT ARCHITECTURE (read the code, then this section as a checklist)
═══════════════════════════════════════════
- Single static HTML file: inline CSS custom properties for light/dark
  theming, an inline SVG procedural avatar generator (`face()`), and
  vanilla ES5-style JS. No framework, no build step, no external requests.
- All state lives in one in-memory array, `people`, seeded from a
  constant `SEED` array and persisted only via `localStorage` (key
  "roots-demo3") through `load()`/`save()`.
- Long-form biography text lives in a separate `SEC` lookup object
  (5 sentences per person id) that gets merged onto each person once via
  `fill()` into `p.s = {b,e,c,p,h,g}` (Basics / Early life / Career /
  Personal life / Historical context / Legacy). New people added through
  the UI get placeholder text instead of real `SEC` entries — the
  migration should keep that same "N/A until edited" fallback behavior.
- Person shape (treat every field as required unless marked optional):
  id (number), name, rel (free-text relationship label, NOT
  authoritative — it's descriptive only, relationships are derived from
  par/unit), born (number|null), died (number|null), gen (integer
  generation index, 0 = great-grandparents), unit (string key shared by
  the two members of a couple), par (optional array of 0–2 parent ids),
  place (string), bio (string, one-paragraph summary), s (object of the
  6 long-form sections above), a (5-element avatar param array: skin
  tone index 0-4, hair color index 0-6, hair style code
  l/c/m/u/b/short/bald-ish single letters, clothing color index 0-5,
  glasses boolean-as-0/1), img (optional base64 data URI, square-cropped
  to 160×160 client-side before storage), me (optional boolean, marks
  the single "you" node), maiden (optional string — birth family name
  for people who married in), origin (optional string — place that
  family was from).
- Relationship model: a "unit" is 1–2 people sharing a `unit` string.
  `nodesOf()` groups `people` into units, sorts each unit so the member
  with known `par` (if any) comes first, then builds a tree of units by
  walking `par[0]` to find each unit's parent unit. A unit can have an
  "ext" (second) incoming parent link when the second partner also has
  known parents elsewhere in the tree (see Maria Adler / Walter Adler
  merging the Adler and Reyes root lines) — this produces a dashed
  connector line (`.ext`) distinct from the solid primary line. This
  dual-parent-unit case is load-bearing for the demo's two founding
  families and must not be lost.
- Layout: `sw()`/`place()` recursively size and position subtrees
  (siblings' subtree widths sum with a fixed gap `GAP`), producing
  absolute pixel coordinates per person, drawn as an SVG path network
  plus absolutely-positioned `.p` button elements on top of it, inside a
  scrollable/zoomable `#scroll > #size > #tree` container controlled by
  `scale` (0.25–1.3) and `focus(id)` (scrolls a person into view).
- "Married in" detection is purely `marriedIn(p) = !!p.maiden` — no
  parent-based heuristic. A married-in person gets a ⚭ badge
  (`.tag`) on their tree card (with a `title` attribute naming their
  birth family + origin for hover/long-press), and their profile sheet
  shows an "Original family" chip that, on tap, toasts a one-line
  sentence built from `origLabel()`.
- Ancestry tracing: `trace(id)` walks `par` recursively via `anc()`,
  toggles a `.anc` class on matched cards and `.hl` on matched SVG paths,
  and re-appends highlighted paths to the end of the SVG so they render
  on top. This must keep working identically against server-fetched data.
- Profile sheet (`openPerson`): shows avatar, name, rel, years, place,
  the married-in chip if applicable, a "Change photo" control (file
  input → canvas center-crop → base64 → `save()` + re-render), chip
  lists for Parents/Partner/Siblings/Children (each chip navigates to
  that person via `openPerson`), the six-tab biography view (`view()`),
  and an inline edit mode (`edit()`) that swaps each section into a
  `<textarea>` and writes back into `p.bio`/`p.s` on save.
- Add flow (`openAdd`): connect a new person to an existing one as
  "child" (computes `par` from the connected person + their existing
  partner, if any, and sets `gen = parent.gen + 1`) or "partner" (fails
  with a toast if the connected person already has a partner in their
  unit; reuses that unit and gen). When adding as partner, two optional
  fields — family name before marriage, and where that family was from —
  populate `maiden`/`origin` on the new person. Avatar params are
  randomized (`rnd()`) at creation time, seeded loosely by birth year and
  chosen gender-presentation.
- Decorative-only UI that should become real: the top "Family plan · $59
  per year · Renews … · 6 relatives can edit" banner and its "Invite"
  button (currently just toasts "Invite link copied (demo)").
- Everything user-facing is escaped via `esc()` before being placed into
  `innerHTML` — the backend/API layer must preserve this: never trust
  client input to be safe HTML server-side either, and the API should
  reject or sanitize control characters, not just rely on client escaping.

═══════════════════════════════════════════
2. DATA MODEL TO DESIGN
═══════════════════════════════════════════
Propose normalized tables (Postgres) covering at least:
- accounts (id, email, password hash or OAuth identity, created_at)
- families (id, name, created_at) — one row per independent tree,
  replacing the single hardcoded "The Adler Family" header
- family_memberships (account_id, family_id, role e.g. owner/editor,
  invited_by, joined_at) — powers a real version of "6 relatives can edit"
- family_invites (id, family_id, email or token, created_by, expires_at,
  accepted_at) — powers a real "Invite" button, e.g. generating a
  shareable join link or emailing one
- people (id, family_id, name, rel, born, died, gen, unit_key, place,
  bio_summary, avatar_params jsonb, photo_url, is_me boolean, maiden,
  origin, created_at, updated_at, created_by, updated_by)
- parents (person_id, parent_id) — normalize the current par[] array
  into a join table instead of an array column, so cycle/duplicate
  checks are simple SQL constraints
- units (key, family_id) if you want unit membership as its own table
  rather than a free-text column on people — either is fine, justify
  your choice
- bio_sections (person_id, section_key enum('b','e','c','p','h','g'),
  content, updated_at, updated_by) — normalize the current `s` object
- audit_log (optional but recommended) — who changed what, when, since
  multiple editors can now touch the same tree
Write and include the actual SQL migration (or ORM schema) for all of
the above, plus a one-time data-migration script that loads the existing
`SEED`/`SEC` arrays from `index.html` into one seeded `families` row, so
the demo dataset survives the migration byte-for-byte (same names, years,
bios, avatar params, maiden/origin fields).

═══════════════════════════════════════════
3. API SURFACE TO IMPLEMENT
═══════════════════════════════════════════
Design and implement a REST (or GraphQL, your call — justify it) API
covering at minimum:
- Auth: POST /signup, POST /login, POST /logout, session/token refresh
- GET /families — trees the current account can access
- POST /families — create a new tree
- GET /families/:id/people — full tree payload shaped so the existing
  `nodesOf()`/`render()`/`trace()` client logic needs minimal changes
- POST /families/:id/people — add a relative (child or partner), with
  the same validation the client currently does (partner slot already
  taken → 409, not a silent failure) plus server-side re-validation
- PATCH /people/:id — edit bio/summary/sections/place/years/photo
- POST /people/:id/photo — upload + store a real image, return a URL
  (replace the base64-in-localStorage approach entirely)
- POST /families/:id/invites, POST /invites/:token/accept — real invite
  flow behind the existing "Invite" button
- Sensible error responses (4xx with a machine-readable reason) that the
  frontend's existing `toast()` calls can be wired to display
Document every endpoint's request/response JSON shape explicitly in the
PR description or an OpenAPI spec file.

═══════════════════════════════════════════
4. FRONTEND REFACTOR REQUIREMENTS
═══════════════════════════════════════════
- Replace `load()`/`save()` with API calls; keep an in-memory `people`
  cache so `render()`, `trace()`, `nodesOf()`, `focus()`, etc. don't need
  to change their signatures.
- `openAdd`'s "ok" handler and `openPerson`'s "sv" (save biography)
  handler should call the API and only mutate local state / re-render on
  a successful response; show the existing `toast()` on failure with the
  server's error reason instead of assuming success.
- Photo upload should still do the client-side square-crop (existing
  canvas code) before sending the resulting blob to
  POST /people/:id/photo, then use the returned URL instead of the
  base64 string.
- Add a lightweight loading state for the initial tree fetch (the
  current app renders synchronously from a hardcoded array — there is no
  spinner or empty state today, and now there will be a network round
  trip) without changing the visual chrome otherwise.
- Decide and implement a conflict-handling strategy for concurrent edits
  from multiple family members (e.g. optimistic UI + last-write-wins
  with a toast if the server rejects a stale edit, or a simple
  refetch-on-focus). State which you chose and why.

═══════════════════════════════════════════
5. VALIDATION & BUSINESS RULES (server-side, not just client-side)
═══════════════════════════════════════════
- A person cannot be their own ancestor (cycle check on the parents table)
- A unit has at most two members/partners
- `gen` should be derived/validated server-side from parentage rather
  than trusted verbatim from the client
- `marriedIn` stays defined as "has a maiden field set" — don't invent a
  parent-based heuristic that could reclassify existing people
- Only members of a family (per family_memberships) may read or write
  that family's people/bio/photos

═══════════════════════════════════════════
6. TESTING
═══════════════════════════════════════════
- Unit tests for the layout/grouping logic ported from `nodesOf()`/
  `sw()`/`place()` (these are pure functions today — keep them pure and
  test them directly against fixture family data, including the
  dual-root-line "ext" case)
- Integration tests for every API endpoint above, including the
  cycle/duplicate-partner/authorization failure cases
- At least one end-to-end test covering: log in → view tree → add a
  partner with a maiden name → see the ⚭ badge and origin chip render
  correctly → edit a biography → reload and confirm persistence

═══════════════════════════════════════════
7. DEPLOYMENT & OPS
═══════════════════════════════════════════
- Dockerfile(s) for the app (and docker-compose for app + Postgres +
  object storage locally)
- Environment-based config for DB URL, object storage credentials/bucket,
  session secret, and any OAuth client ids — document them in a
  `.env.example`
- A basic CI config (lint + test) is a nice-to-have if your setup
  supports it

═══════════════════════════════════════════
8. NON-FUNCTIONAL / QUALITY BAR
═══════════════════════════════════════════
- Preserve accessibility affordances already present (focus-visible
  outlines, aria-modal on the sheet, Escape-to-close, reduced-motion
  handling on the "new person" pop animation) — don't regress them while
  refactoring event wiring.
- Preserve the safe-area-inset handling for mobile web.
- Sanitize all user-supplied text server-side in addition to the
  client's existing `esc()` escaping.
- The tree should still render acceptably for a few hundred people —
  call out if your chosen approach needs pagination/virtualization
  beyond that scale, but don't over-engineer for it up front.

═══════════════════════════════════════════
DELIVERY
═══════════════════════════════════════════
Work incrementally and keep the app runnable at each step. Start by
posting: (a) the schema/migration, (b) the OpenAPI/endpoint list, and
(c) a short plan for the frontend refactor — before writing the full
implementation, so the approach can be reviewed early.
