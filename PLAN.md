# Roots Migration Plan

## 1. Schema & Migration (Postgres)

```sql
CREATE TABLE accounts (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE families (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE family_memberships (
  account_id INT REFERENCES accounts(id) ON DELETE CASCADE,
  family_id INT REFERENCES families(id) ON DELETE CASCADE,
  role VARCHAR(50) NOT NULL, -- 'owner' or 'editor'
  invited_by INT REFERENCES accounts(id) ON DELETE SET NULL,
  joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (account_id, family_id)
);

CREATE TABLE family_invites (
  id SERIAL PRIMARY KEY,
  family_id INT REFERENCES families(id) ON DELETE CASCADE,
  token VARCHAR(255) UNIQUE NOT NULL,
  created_by INT REFERENCES accounts(id) ON DELETE CASCADE,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  accepted_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE people (
  id SERIAL PRIMARY KEY,
  family_id INT REFERENCES families(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  rel VARCHAR(255),
  born INT,
  died INT,
  gen INT NOT NULL,
  unit_key VARCHAR(255) NOT NULL,
  place VARCHAR(255),
  bio_summary TEXT,
  avatar_params JSONB NOT NULL,
  photo_url TEXT,
  is_me BOOLEAN DEFAULT FALSE,
  maiden VARCHAR(255),
  origin VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  created_by INT REFERENCES accounts(id) ON DELETE SET NULL,
  updated_by INT REFERENCES accounts(id) ON DELETE SET NULL
);

CREATE TABLE parents (
  person_id INT REFERENCES people(id) ON DELETE CASCADE,
  parent_id INT REFERENCES people(id) ON DELETE CASCADE,
  PRIMARY KEY (person_id, parent_id)
);

CREATE TABLE bio_sections (
  person_id INT REFERENCES people(id) ON DELETE CASCADE,
  section_key VARCHAR(1) CHECK (section_key IN ('b','e','c','p','h','g')),
  content TEXT NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_by INT REFERENCES accounts(id) ON DELETE SET NULL,
  PRIMARY KEY (person_id, section_key)
);
```

**Migration script:** I will write a Node.js script (`migrate.js`) to parse `index.html` via regex/AST to extract `SEED` and `SEC`, connect to Postgres, insert a default `account` and `family` ("The Adler Family"), and iterate through the arrays to populate `people`, `parents`, and `bio_sections`, ensuring IDs match and parent relationships map correctly to the join table.

## 2. API Endpoints (OpenAPI / JSON shape)

REST API built with Node.js/Express.

- `POST /api/auth/signup`: `{ email, password }` -> `{ token, user }`
- `POST /api/auth/login`: `{ email, password }` -> `{ token, user }`
- `POST /api/auth/logout`: clear session/cookie
- `GET /api/auth/me`: `{ user }`

- `GET /api/families`: `[ { id, name, role } ]`
- `POST /api/families`: `{ name }` -> `{ id, name }`
- `GET /api/families/:id/people`: Returns the tree.
  `[ { id, name, rel, born, died, gen, unit, par: [id1, id2], place, bio, s: {b,e,c,p,h,g}, a: [...], img, me, maiden, origin } ]`
  *(Note: this endpoint joins `parents` into the `par` array, and `bio_sections` into the `s` object to match the client's current shape).*

- `POST /api/families/:id/people`: Add a person.
  Request: `{ mode: 'child'|'partner', targetPersonId, personData: { name, born, died, place, bio, a, maiden, origin, is_me } }`
  *Validation: Server finds `targetPerson`, derives `gen`, assigns `unit_key` (if partner, uses target's unit, ensuring count < 2; if child, new unit and adds parents). Cycle check during insertion.*
  Returns: `{ id, ...newPersonFields }`

- `PATCH /api/people/:id`: Edit fields.
  Request: `{ name, rel, born, died, place, bio, s: { ... }, maiden, origin, a }`
  Returns: updated person.

- `POST /api/people/:id/photo`: Multipart file upload.
  Returns: `{ url }` (served locally/S3).

- `POST /api/families/:id/invites`:
  Returns: `{ token, link }`
- `POST /api/invites/:token/accept`:
  Returns: `{ family_id }`

## 3. Frontend Refactor Plan

1. **Authentication UI**: Replace initial blank screen with a lightweight login/signup overlay if `/api/auth/me` fails.
2. **State Management**: Replace `localStorage` `load()` with a loading spinner followed by fetching `/api/families` (pick first) and then `/api/families/:id/people`. Keep the `people` array in memory cache so `nodesOf()`, `sw()`, `place()`, etc. remain untouched.
3. **Conflict Strategy**: **Optimistic UI with last-write-wins**. On edit, update the local cache immediately and send `PATCH`. If it fails (e.g., rejected by server or auth error), toast the error and trigger a full tree refetch. This keeps the UI snappy while guaranteeing eventual consistency.
4. **Bio Edits**: `openPerson`'s save handler will `PATCH` changes to the API, then update local state and re-render.
5. **Adding Relatives**: `openAdd` ok handler will call `POST /api/families/:id/people` with the `mode` and `targetId`. This moves the core `unit` assignment and validation (already 2 partners!) to the server, then inserts the returned person into local cache and calls `render()`.
6. **Photo Upload**: Change base64 logic to use `FormData` + `POST /api/people/:id/photo`, updating `img` with the URL returned by the server.
