Convert the attached single-file HTML prototype (`index.html`) — a family
tree app called "Roots" — into a real, deployable, multi-user web
application. Preserve all existing UI, styling, layout, and interaction
design exactly as-is; this is a backend/persistence/auth migration, not a
redesign.

CURRENT STATE (read this first)
- Everything is in one static HTML file: inline CSS, inline SVG avatar
  generator, and vanilla JS (no framework, no build step).
- All family data (people, relationships, photos, biographies) lives in a
  single in-memory JS array (`SEED`), and is persisted only via
  `localStorage` on one browser, under the key "roots-demo3".
- Data model per person: id, name, rel (relationship label), born, died,
  gen (generation index), unit (couple/partnership grouping key), par
  (array of 0-2 parent ids), place, bio, a (avatar params: skin tone,
  hair color, hair style, clothing color, glasses), img (optional uploaded
  photo as base64 data URI), s (object of long-form bio sections: b/e/c/p/h/g
  for Basics/Early life/Career/Personal life/Historical context/Legacy),
  and for people who married into the family: maiden (birth family name)
  and origin (place that family was from).
- The tree is laid out and rendered entirely client-side by walking
  parent/partner relationships into "units" (couples) and generations.
- Features to preserve: pan/zoom tree view with "whole tree" and "find me"
  buttons, click-to-trace ancestry highlighting, a bottom sheet for
  viewing/editing a person's profile and biography tabs, photo upload with
  client-side square-crop downscaling, an "Add a relative" flow (add as
  child or partner, with an optional maiden-name/origin pair of fields
  when adding a partner), toast notifications, light/dark theme support,
  and the ⚭ "married in" badge + tappable origin-family chip.

WHAT TO BUILD
1. Backend + database: stand up a real backend (Node/Express or your
   framework of choice) with a proper relational database (Postgres is
   fine) instead of localStorage. Design normalized tables for people,
   relationships/units, and the long-form bio sections, migrating the
   existing SEED data as the initial dataset for one demo family.
2. Multi-user accounts: real signup/login (email+password or OAuth),
   sessions, and support for multiple independent family trees — each
   belonging to one account or a shared group of accounts. Turn the
   decorative "Family plan / Invite" UI into a working invite flow: an
   invited member can join a specific family's tree and edit it, matching
   the "6 relatives can edit" language already in the UI.
3. Real photo storage: replace base64-in-localStorage with actual file
   uploads to object storage (S3-compatible bucket or equivalent), sized
   and served efficiently, with the existing client-side square-crop
   preserved as a pre-upload step.
4. API layer: expose REST or GraphQL endpoints for reading a tree, adding
   a relative (child or partner, including the maiden-name/origin fields),
   editing a biography, and uploading a photo. The existing frontend
   functions (`render`, `openPerson`, `openAdd`, `save`) should be
   refactored to call these endpoints instead of mutating a local array
   and writing to localStorage, while keeping the exact same DOM output
   and CSS.
5. Data integrity: validate relationships server-side (no cycles, a
   person can't be their own ancestor, a unit has at most two partners,
   etc.) and add basic authorization (only members of a family can view
   or edit that family's tree).
6. Deployment: make it deployable as a normal web app (e.g. a Dockerfile
   or standard hosting config), with environment-based config for the
   database and object storage credentials.

CONSTRAINTS
- Do not change the visual design, copy, layout, or interaction patterns
  of the existing UI — this is about giving it a real backend, not a
  redesign.
- Keep the app usable on mobile web (it currently handles safe-area
  insets and touch scrolling deliberately — preserve that).
- Where you must choose a stack detail I haven't specified (ORM, exact
  hosting target, REST vs GraphQL), pick something conventional and
  explain the choice briefly in the PR description.

Please start by proposing the data model/schema and API surface, then
implement incrementally, keeping the app runnable at each step.
