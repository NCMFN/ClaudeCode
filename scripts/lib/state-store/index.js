'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const Database = require('better-sqlite3');

const { applyMigrations, getAppliedMigrations } = require('./migrations');
const { createQueryApi } = require('./queries');
const { assertValidEntity, validateEntity } = require('./schema');

const DEFAULT_STATE_STORE_RELATIVE_PATH = path.join('.claude', 'ecc', 'state.db');

function resolveStateStorePath(options = {}) {
  if (options.dbPath) {
    if (options.dbPath === ':memory:') {
      return options.dbPath;
    }
    return path.resolve(options.dbPath);
  }

  const homeDir = options.homeDir || process.env.HOME || os.homedir();
  return path.join(homeDir, DEFAULT_STATE_STORE_RELATIVE_PATH);
}

function openDatabase(dbPath) {
  if (dbPath !== ':memory:') {
    fs.mkdirSync(path.dirname(dbPath), { recursive: true });
  }

  const db = new Database(dbPath);
  db.pragma('foreign_keys = ON');
  try {
    db.pragma('journal_mode = WAL');
  } catch (_error) {
    // Some SQLite environments reject WAL for in-memory or readonly contexts.
  }
  return db;
}

function createStateStore(options = {}) {
  const dbPath = resolveStateStorePath(options);
  const db = openDatabase(dbPath);
  const appliedMigrations = applyMigrations(db);
  const queryApi = createQueryApi(db);

  return {
    dbPath,
    close() {
      db.close();
    },
    getAppliedMigrations() {
      return getAppliedMigrations(db);
    },
    validateEntity,
    assertValidEntity,
    ...queryApi,
    _database: db,
    _migrations: appliedMigrations,
  };
}

module.exports = {
  DEFAULT_STATE_STORE_RELATIVE_PATH,
  createStateStore,
  resolveStateStorePath,
};
