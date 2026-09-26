const { Pool } = require('pg');
const fs = require('fs');
require('dotenv').config();

const pool = new Pool({
  connectionString: "postgres://postgres:postgres@localhost:5432/roots"
});

async function migrate() {
  const seedFile = fs.readFileSync('/tmp/seed.js', 'utf8');
  const secFile = fs.readFileSync('/app/frontend/index.html', 'utf8');

  // Extract SEC object safely
  const secMatch = secFile.match(/var SEC=\{([\s\S]*?)\};\nfunction era/);
  let secStr = secMatch ? `{${secMatch[1]}}` : '{}';
  const SEC = eval('(' + secStr + ')');

  // Extract SEED object safely
  const SEED = eval(seedFile + ' SEED_DATA;');

  try {
    await pool.query('BEGIN');

    // Clear old data
    // Ignore error if tables do not exist yet (they should since we ran schema.sql but just in case)

    // Run schema
    const schemaSql = fs.readFileSync('/app/backend/schema.sql', 'utf8');
    await pool.query(schemaSql);

    await pool.query('TRUNCATE TABLE family_members, bios, relationships, people, families, users RESTART IDENTITY CASCADE');

    // Create demo user
    const { rows: userRows } = await pool.query(
      "INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id",
      ['demo@example.com', 'dummyhash']
    );
    const userId = userRows[0].id;

    // Create family
    const { rows: familyRows } = await pool.query(
      "INSERT INTO families (name) VALUES ($1) RETURNING id",
      ['Adler Family Demo']
    );
    const familyId = familyRows[0].id;

    await pool.query(
      "INSERT INTO family_members (family_id, user_id, role) VALUES ($1, $2, $3)",
      [familyId, userId, 'admin']
    );

    console.log(`Created Family ID: ${familyId}`);

    const era = (y) => !y?"":y<1920?"Lived through two world wars and the Great Depression.":y<1945?"Childhood shaped by the Great Depression and the Second World War.":y<1970?"Grew up in the postwar boom, the civil rights era and the Cold War.":y<1990?"Came of age in the 1980s and 90s, as the Cold War ended and the internet arrived.":y<2010?"Grew up with the internet, 9/11 and the 2008 financial crisis.":"Born into the smartphone era and the pandemic years.";

    const idMap = {};
    for (const p of SEED) {
      const { rows: personRows } = await pool.query(
        `INSERT INTO people (family_id, name, rel, born, died, gen, unit, place, maiden, origin, bio, avatar_params, is_me)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) RETURNING id`,
        [familyId, p.name, p.rel, p.born, p.died, p.gen, p.unit, p.place, p.maiden, p.origin, p.bio, JSON.stringify(p.a), !!p.me]
      );
      idMap[p.id] = personRows[0].id;
    }

    for (const p of SEED) {
      const newId = idMap[p.id];

      if (p.par) {
        for (const oldParId of p.par) {
          if (idMap[oldParId]) {
            await pool.query(
              "INSERT INTO relationships (family_id, person_id, parent_id) VALUES ($1, $2, $3)",
              [familyId, newId, idMap[oldParId]]
            );
          }
        }
      }

      const x = SEC[p.id] || [];
      const N = "Not yet recorded. Tap Edit to add.";

      const parNames = p.par ? p.par.map(id => SEED.find(s => s.id === id)?.name).filter(Boolean).join(" and ") : "not yet recorded";
      const basics = `${p.name}, born ${p.born || "in an unknown year"}. Parents: ${parNames}. Siblings: none recorded.`;

      const s = {
        b: basics + (x[0] ? " " + x[0] : ""),
        e: x[1] || N,
        c: x[2] || N,
        p: x[3] || N,
        h: (era(p.born) + (p.place ? " Place: " + p.place + "." : "")).trim() || N,
        g: (p.died ? "Died in " + p.died + (p.born ? " at age " + (p.died - p.born) : "") + ". " : "") + (x[4] || N)
      };

      await pool.query(
        `INSERT INTO bios (person_id, basics, early_life, career, personal_life, historical_context, legacy)
         VALUES ($1, $2, $3, $4, $5, $6, $7)`,
        [newId, s.b, s.e, s.c, s.p, s.h, s.g]
      );
    }

    await pool.query('COMMIT');
    console.log('Migration completed successfully!');
  } catch (e) {
    await pool.query('ROLLBACK');
    console.error('Migration failed:', e);
  } finally {
    pool.end();
  }
}

migrate();
