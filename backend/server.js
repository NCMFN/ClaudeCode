const express = require('express');
const { Pool } = require('pg');
const multer = require('multer');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const path = require('path');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use('/uploads', express.static(process.env.UPLOADS_DIR || path.join(__dirname, 'uploads')));
app.use(express.static(path.join(__dirname, '../frontend')));

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || "postgres://postgres:postgres@localhost:5432/roots"
});

// Auth middleware
const auth = (req, res, next) => {
  const token = req.header('Authorization')?.replace('Bearer ', '');
  if (!token) return res.status(401).send({ error: 'Please authenticate.' });
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.userId = decoded.id;
    next();
  } catch (e) {
    res.status(401).send({ error: 'Please authenticate.' });
  }
};

// Family membership check
const familyAuth = async (req, res, next) => {
  const familyId = req.params.familyId || req.body.familyId;
  const { rows } = await pool.query('SELECT 1 FROM family_members WHERE family_id = $1 AND user_id = $2', [familyId, req.userId]);
  if (rows.length === 0) return res.status(403).send({ error: 'Not authorized for this family.' });
  next();
};

app.post('/api/auth/register', async (req, res) => {
  const { email, password } = req.body;
  try {
    const hash = await bcrypt.hash(password, 10);
    const { rows } = await pool.query('INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id', [email, hash]);
    const userId = rows[0].id;

    // Create initial family tree
    const familyResult = await pool.query('INSERT INTO families (name) VALUES ($1) RETURNING id', ['My Family']);
    const familyId = familyResult.rows[0].id;
    await pool.query('INSERT INTO family_members (family_id, user_id, role) VALUES ($1, $2, $3)', [familyId, userId, 'admin']);

    const token = jwt.sign({ id: userId }, process.env.JWT_SECRET);
    res.send({ token, familyId });
  } catch (e) {
    res.status(400).send({ error: e.message });
  }
});

app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;
  try {
    const { rows } = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    if (rows.length === 0) throw new Error('Invalid login');
    const valid = await bcrypt.compare(password, rows[0].password_hash);
    if (!valid) throw new Error('Invalid login');
    const token = jwt.sign({ id: rows[0].id }, process.env.JWT_SECRET);

    const familyRows = await pool.query('SELECT family_id FROM family_members WHERE user_id = $1 LIMIT 1', [rows[0].id]);
    res.send({ token, familyId: familyRows.rows[0]?.family_id });
  } catch (e) {
    res.status(400).send({ error: e.message });
  }
});

app.get('/api/families/:familyId/tree', auth, familyAuth, async (req, res) => {
  const { familyId } = req.params;
  try {
    const peopleResult = await pool.query('SELECT * FROM people WHERE family_id = $1', [familyId]);
    const relationsResult = await pool.query('SELECT * FROM relationships WHERE family_id = $1', [familyId]);
    const biosResult = await pool.query(`
      SELECT b.* FROM bios b
      JOIN people p ON b.person_id = p.id
      WHERE p.family_id = $1
    `, [familyId]);

    const people = peopleResult.rows.map(p => {
      const par = relationsResult.rows
        .filter(r => r.person_id === p.id)
        .map(r => r.parent_id);

      const bioData = biosResult.rows.find(b => b.person_id === p.id) || {};
      const s = {
        b: bioData.basics,
        e: bioData.early_life,
        c: bioData.career,
        p: bioData.personal_life,
        h: bioData.historical_context,
        g: bioData.legacy
      };

      return {
        id: p.id,
        name: p.name,
        rel: p.rel,
        born: p.born,
        died: p.died,
        gen: p.gen,
        unit: p.unit,
        place: p.place,
        maiden: p.maiden,
        origin: p.origin,
        bio: p.bio,
        a: p.avatar_params,
        img: p.img_url,
        me: p.is_me,
        par: par.length ? par : undefined,
        s: Object.keys(s).some(k => s[k]) ? s : undefined
      };
    });

    res.send(people);
  } catch (e) {
    res.status(500).send({ error: e.message });
  }
});

app.post('/api/families/:familyId/people', auth, familyAuth, async (req, res) => {
  const { familyId } = req.params;
  const { name, rel, born, died, gen, unit, place, maiden, origin, bio, a, par } = req.body;

  try {
    await pool.query('BEGIN');
    const { rows } = await pool.query(
      `INSERT INTO people (family_id, name, rel, born, died, gen, unit, place, maiden, origin, bio, avatar_params)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12) RETURNING id`,
      [familyId, name, rel, born, died, gen, unit, place, maiden, origin, bio, a]
    );
    const newId = rows[0].id;

    if (par && par.length) {
      for (const parentId of par) {
        await pool.query(
          'INSERT INTO relationships (family_id, person_id, parent_id) VALUES ($1, $2, $3)',
          [familyId, newId, parentId]
        );
      }
    }

    await pool.query('COMMIT');
    res.send({ id: newId });
  } catch (e) {
    await pool.query('ROLLBACK');
    res.status(500).send({ error: e.message });
  }
});

app.put('/api/families/:familyId/people/:personId/bio', auth, familyAuth, async (req, res) => {
  const { personId } = req.params;
  const { bio, s } = req.body;

  try {
    await pool.query('BEGIN');
    await pool.query('UPDATE people SET bio = $1 WHERE id = $2', [bio, personId]);

    if (s) {
      await pool.query(`
        INSERT INTO bios (person_id, basics, early_life, career, personal_life, historical_context, legacy)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (person_id) DO UPDATE SET
          basics = EXCLUDED.basics,
          early_life = EXCLUDED.early_life,
          career = EXCLUDED.career,
          personal_life = EXCLUDED.personal_life,
          historical_context = EXCLUDED.historical_context,
          legacy = EXCLUDED.legacy
      `, [personId, s.b, s.e, s.c, s.p, s.h, s.g]);
    }
    await pool.query('COMMIT');
    res.send({ success: true });
  } catch (e) {
    await pool.query('ROLLBACK');
    res.status(500).send({ error: e.message });
  }
});

const upload = multer({ dest: process.env.UPLOADS_DIR });
app.post('/api/families/:familyId/people/:personId/photo', auth, familyAuth, upload.single('photo'), async (req, res) => {
  const { personId } = req.params;
  try {
    const imgUrl = `/uploads/${req.file.filename}`;
    await pool.query('UPDATE people SET img_url = $1 WHERE id = $2', [imgUrl, personId]);
    res.send({ url: imgUrl });
  } catch (e) {
    res.status(500).send({ error: e.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
