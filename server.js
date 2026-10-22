const express = require('express');
const { Pool } = require('pg');
const bodyParser = require('body-parser');
const cors = require('cors');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const asyncHandler = require('express-async-handler');
const multer = require('multer');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('.'));

const pool = new Pool({
  user: process.env.PGUSER || 'jules',
  host: process.env.PGHOST || 'localhost',
  database: process.env.PGDATABASE || 'roots',
  password: process.env.PGPASSWORD || 'jules',
  port: process.env.PGPORT || 5432,
});

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';

// Auth middleware
const requireAuth = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: 'No authorization header' });

  const token = authHeader.split(' ')[1];
  try {
    const user = jwt.verify(token, JWT_SECRET);
    req.user = user;
    next();
  } catch (err) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

app.post('/api/auth/signup', asyncHandler(async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'Email and password required' });

  const hash = await bcrypt.hash(password, 10);
  try {
    const result = await pool.query('INSERT INTO accounts (email, password_hash) VALUES ($1, $2) RETURNING id, email', [email, hash]);
    const user = result.rows[0];
    const token = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET, { expiresIn: '7d' });
    res.json({ token, user });
  } catch (err) {
    if (err.code === '23505') return res.status(409).json({ error: 'Email already exists' });
    throw err;
  }
}));

app.post('/api/auth/login', asyncHandler(async (req, res) => {
  const { email, password } = req.body;
  const result = await pool.query('SELECT * FROM accounts WHERE email = $1', [email]);
  const user = result.rows[0];

  if (!user || !(await bcrypt.compare(password, user.password_hash))) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  const token = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET, { expiresIn: '7d' });
  res.json({ token, user: { id: user.id, email: user.email } });
}));

app.get('/api/auth/me', requireAuth, asyncHandler(async (req, res) => {
  res.json({ user: req.user });
}));

// Family endpoints
app.get('/api/families', requireAuth, asyncHandler(async (req, res) => {
  const result = await pool.query(`
    SELECT f.id, f.name, fm.role
    FROM families f
    JOIN family_memberships fm ON f.id = fm.family_id
    WHERE fm.account_id = $1
  `, [req.user.id]);
  res.json(result.rows);
}));

app.post('/api/families', requireAuth, asyncHandler(async (req, res) => {
  const { name } = req.body;
  if (!name) return res.status(400).json({ error: 'Name is required' });

  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const fRes = await client.query('INSERT INTO families (name) VALUES ($1) RETURNING id, name', [name]);
    const family = fRes.rows[0];

    await client.query('INSERT INTO family_memberships (account_id, family_id, role) VALUES ($1, $2, $3)', [req.user.id, family.id, 'owner']);
    await client.query('COMMIT');
    res.json(family);
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}));

app.post('/api/families/:id/invites', requireAuth, asyncHandler(async (req, res) => {
  const familyId = parseInt(req.params.id);
  const fmRes = await pool.query('SELECT role FROM family_memberships WHERE account_id = $1 AND family_id = $2', [req.user.id, familyId]);
  if (fmRes.rowCount === 0) return res.status(403).json({ error: 'Not a member of this family' });

  const token = require('crypto').randomBytes(32).toString('hex');
  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

  await pool.query(
    'INSERT INTO family_invites (family_id, token, created_by, expires_at) VALUES ($1, $2, $3, $4)',
    [familyId, token, req.user.id, expiresAt]
  );

  res.json({ token, link: `/invite/${token}` });
}));

app.post('/api/invites/:token/accept', requireAuth, asyncHandler(async (req, res) => {
  const { token } = req.params;
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const inviteRes = await client.query('SELECT * FROM family_invites WHERE token = $1 AND accepted_at IS NULL AND expires_at > NOW()', [token]);
    if (inviteRes.rowCount === 0) {
      await client.query('ROLLBACK');
      return res.status(400).json({ error: 'Invalid or expired invite' });
    }
    const invite = inviteRes.rows[0];

    await client.query(`
      INSERT INTO family_memberships (account_id, family_id, role, invited_by)
      VALUES ($1, $2, $3, $4)
      ON CONFLICT (account_id, family_id) DO NOTHING
    `, [req.user.id, invite.family_id, 'editor', invite.created_by]);

    await client.query('UPDATE family_invites SET accepted_at = NOW() WHERE id = $1', [invite.id]);

    await client.query('COMMIT');
    res.json({ family_id: invite.family_id });
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}));

const upload = multer({ dest: 'uploads/' });
app.use('/uploads', express.static('uploads'));

async function getTreeForFamily(familyId) {
  const peopleRes = await pool.query('SELECT * FROM people WHERE family_id = $1 ORDER BY id', [familyId]);
  const parentsRes = await pool.query(`
    SELECT p.person_id, p.parent_id
    FROM parents p
    JOIN people pp ON p.person_id = pp.id
    WHERE pp.family_id = $1
  `, [familyId]);

  const bioRes = await pool.query(`
    SELECT b.person_id, b.section_key, b.content
    FROM bio_sections b
    JOIN people pp ON b.person_id = pp.id
    WHERE pp.family_id = $1
  `, [familyId]);

  const people = peopleRes.rows.map(p => {
    const parentIds = parentsRes.rows.filter(pr => pr.person_id === p.id).map(pr => pr.parent_id);
    const s = {};
    bioRes.rows.filter(b => b.person_id === p.id).forEach(b => {
      s[b.section_key] = b.content;
    });

    const obj = {
      id: p.id,
      name: p.name,
      rel: p.rel || undefined,
      born: p.born,
      died: p.died,
      gen: p.gen,
      unit: p.unit_key,
      a: p.avatar_params,
      me: p.is_me || undefined,
      img: p.photo_url || undefined,
      maiden: p.maiden || undefined,
      origin: p.origin || undefined,
      place: p.place || undefined,
      bio: p.bio_summary || undefined,
    };
    if (parentIds.length > 0) obj.par = parentIds;
    if (Object.keys(s).length > 0) obj.s = s;
    return obj;
  });
  return people;
}

app.get('/api/families/:id/people', requireAuth, asyncHandler(async (req, res) => {
  const familyId = parseInt(req.params.id);
  const fmRes = await pool.query('SELECT role FROM family_memberships WHERE account_id = $1 AND family_id = $2', [req.user.id, familyId]);
  if (fmRes.rowCount === 0) return res.status(403).json({ error: 'Not a member of this family' });

  const tree = await getTreeForFamily(familyId);
  res.json(tree);
}));

app.post('/api/families/:id/people', requireAuth, asyncHandler(async (req, res) => {
  const familyId = parseInt(req.params.id);
  const fmRes = await pool.query('SELECT role FROM family_memberships WHERE account_id = $1 AND family_id = $2', [req.user.id, familyId]);
  if (fmRes.rowCount === 0) return res.status(403).json({ error: 'Not a member of this family' });

  const { mode, targetPersonId, personData } = req.body;
  if (!['child', 'partner'].includes(mode)) return res.status(400).json({ error: 'Invalid mode' });

  const targetRes = await pool.query('SELECT * FROM people WHERE id = $1 AND family_id = $2', [targetPersonId, familyId]);
  if (targetRes.rowCount === 0) return res.status(404).json({ error: 'Target person not found' });
  const target = targetRes.rows[0];

  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    let gen = target.gen;
    let unitKey = target.unit_key;
    let parentIds = [];

    if (mode === 'partner') {
      const unitCountRes = await client.query('SELECT count(*) FROM people WHERE unit_key = $1 AND family_id = $2', [target.unit_key, familyId]);
      if (parseInt(unitCountRes.rows[0].count) >= 2) {
        await client.query('ROLLBACK');
        return res.status(409).json({ error: 'Target person already has a partner' });
      }
    } else if (mode === 'child') {
      gen = target.gen + 1;
      unitKey = `${Date.now()}-${Math.random().toString(36).substring(2, 6)}`;

      const partnerRes = await client.query('SELECT id FROM people WHERE unit_key = $1 AND id != $2 AND family_id = $3', [target.unit_key, target.id, familyId]);
      parentIds = [target.id];
      if (partnerRes.rowCount > 0) parentIds.push(partnerRes.rows[0].id);
    }

    const p = personData;
    const result = await client.query(`
      INSERT INTO people (family_id, name, rel, born, died, gen, unit_key, place, bio_summary, avatar_params, is_me, maiden, origin, created_by)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
      RETURNING id, name, rel, born, died, gen, unit_key, place, bio_summary, avatar_params, is_me, maiden, origin
    `, [
      familyId, p.name, p.rel, p.born || null, p.died || null, gen, unitKey, p.place, p.bio, JSON.stringify(p.a || []), !!p.is_me, p.maiden, p.origin, req.user.id
    ]);

    const newPersonId = result.rows[0].id;

    for (const parentId of parentIds) {
      await client.query('INSERT INTO parents (person_id, parent_id) VALUES ($1, $2)', [newPersonId, parentId]);
    }

    await client.query('COMMIT');

    const obj = {
      id: newPersonId, name: p.name, rel: p.rel, born: p.born, died: p.died, gen, unit: unitKey, a: p.a, me: p.is_me, maiden: p.maiden, origin: p.origin, place: p.place, bio: p.bio
    };
    if (parentIds.length > 0) obj.par = parentIds;
    res.json(obj);
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}));

app.patch('/api/people/:id', requireAuth, asyncHandler(async (req, res) => {
  const personId = parseInt(req.params.id);
  const familyRes = await pool.query('SELECT family_id FROM people WHERE id = $1', [personId]);
  if (familyRes.rowCount === 0) return res.status(404).json({ error: 'Person not found' });
  const familyId = familyRes.rows[0].family_id;

  const fmRes = await pool.query('SELECT role FROM family_memberships WHERE account_id = $1 AND family_id = $2', [req.user.id, familyId]);
  if (fmRes.rowCount === 0) return res.status(403).json({ error: 'Not a member of this family' });

  const p = req.body;
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const updateFields = [];
    const updateValues = [];
    let paramIdx = 1;

    const allowed = ['name', 'rel', 'born', 'died', 'place', 'bio', 'maiden', 'origin'];
    for (const key of allowed) {
      if (p[key] !== undefined) {
        updateFields.push(`${key === 'bio' ? 'bio_summary' : key} = $${paramIdx++}`);
        updateValues.push(p[key] === '' ? null : p[key]);
      }
    }
    if (p.a !== undefined) {
      updateFields.push(`avatar_params = $${paramIdx++}`);
      updateValues.push(JSON.stringify(p.a));
    }

    if (updateFields.length > 0) {
      updateFields.push(`updated_at = NOW()`, `updated_by = $${paramIdx++}`);
      updateValues.push(req.user.id);

      updateValues.push(personId);
      await client.query(`UPDATE people SET ${updateFields.join(', ')} WHERE id = $${paramIdx}`, updateValues);
    }

    if (p.s) {
      for (const [key, content] of Object.entries(p.s)) {
        await client.query(`
          INSERT INTO bio_sections (person_id, section_key, content, updated_by)
          VALUES ($1, $2, $3, $4)
          ON CONFLICT (person_id, section_key) DO UPDATE
          SET content = EXCLUDED.content, updated_at = NOW(), updated_by = EXCLUDED.updated_by
        `, [personId, key, content, req.user.id]);
      }
    }

    await client.query('COMMIT');
    res.json({ success: true });
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}));

app.post('/api/people/:id/photo', requireAuth, upload.single('photo'), asyncHandler(async (req, res) => {
  const personId = parseInt(req.params.id);
  const familyRes = await pool.query('SELECT family_id FROM people WHERE id = $1', [personId]);
  if (familyRes.rowCount === 0) return res.status(404).json({ error: 'Person not found' });
  const familyId = familyRes.rows[0].family_id;

  const fmRes = await pool.query('SELECT role FROM family_memberships WHERE account_id = $1 AND family_id = $2', [req.user.id, familyId]);
  if (fmRes.rowCount === 0) return res.status(403).json({ error: 'Not a member of this family' });

  if (!req.file) return res.status(400).json({ error: 'No photo provided' });

  const url = `/uploads/${req.file.filename}`;
  await pool.query('UPDATE people SET photo_url = $1 WHERE id = $2', [url, personId]);

  res.json({ url });
}));

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Server listening on port ${port}`));
