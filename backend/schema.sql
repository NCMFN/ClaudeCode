CREATE TABLE IF NOT EXISTS families (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS family_members (
    family_id INTEGER REFERENCES families(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    PRIMARY KEY (family_id, user_id)
);

CREATE TABLE IF NOT EXISTS people (
    id SERIAL PRIMARY KEY,
    family_id INTEGER REFERENCES families(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    rel VARCHAR(255),
    born INTEGER,
    died INTEGER,
    gen INTEGER,
    unit VARCHAR(50),
    place VARCHAR(255),
    maiden VARCHAR(255),
    origin VARCHAR(255),
    bio TEXT,
    avatar_params JSONB,
    img_url VARCHAR(255),
    is_me BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS relationships (
    id SERIAL PRIMARY KEY,
    family_id INTEGER REFERENCES families(id) ON DELETE CASCADE,
    person_id INTEGER REFERENCES people(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES people(id) ON DELETE CASCADE,
    UNIQUE (person_id, parent_id)
);

CREATE TABLE IF NOT EXISTS bios (
    person_id INTEGER PRIMARY KEY REFERENCES people(id) ON DELETE CASCADE,
    basics TEXT,
    early_life TEXT,
    career TEXT,
    personal_life TEXT,
    historical_context TEXT,
    legacy TEXT
);
