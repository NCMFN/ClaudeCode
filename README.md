# Roots – Family Tree Demo

A single-file, client-side prototype of a family tree app. Everything (data,
styling, logic) lives in `index.html` — there's no build step and no server.

## Run it
Just open `index.html` in any modern browser (double-click it, or drag it
into a browser tab). Works offline.

## What it does
- Renders a zoomable, pannable family tree across five generations
- Tap/click anyone to trace their ancestral line back to the great-grandparents
- Tap a person for a full profile: bio, tabs (Basics, Early life, Career,
  Personal life, Historical context, Legacy), and photo upload
- "Add a relative" lets you add a child or partner to any existing person
- People who **married into** the family (no blood parents in the tree) show
  a small ⚭ badge and a tappable "Original family" note naming the family
  and place they came from before marriage
- Data is saved to the browser's `localStorage`, so edits persist on reload
  in that same browser (there is no shared backend — it's all local)

## Known limitations (by design, since it's a demo)
- Single-user only: data lives in one browser's localStorage, nothing is
  shared between devices or people
- No accounts/auth — the "Family plan" and "Invite" UI elements are
  decorative and don't do anything real
- No real photo storage — uploaded photos are downscaled and stored as
  base64 data URIs inside localStorage
- No server-side validation, backups, or multi-tree support

See `JULES_PROMPT.md` for a ready-to-use prompt that asks Google Jules to
turn this into a real, multi-user, persisted web app.
