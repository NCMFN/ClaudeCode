use anyhow::Result;
use rusqlite::Connection;
use std::path::Path;

use super::{Session, SessionMetrics, SessionState};

pub struct StateStore {
    conn: Connection,
}

impl StateStore {
    pub fn open(path: &Path) -> Result<Self> {
        let conn = Connection::open(path)?;
        let store = Self { conn };
        store.init_schema()?;
        Ok(store)
    }

    fn init_schema(&self) -> Result<()> {
        self.conn.execute_batch(
            "
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                task TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                state TEXT NOT NULL DEFAULT 'pending',
                pid INTEGER,
                worktree_path TEXT,
                worktree_branch TEXT,
                worktree_base TEXT,
                tokens_used INTEGER DEFAULT 0,
                tool_calls INTEGER DEFAULT 0,
                files_changed INTEGER DEFAULT 0,
                duration_secs INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tool_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES sessions(id),
                tool_name TEXT NOT NULL,
                input_summary TEXT,
                output_summary TEXT,
                duration_ms INTEGER,
                risk_score REAL DEFAULT 0.0,
                timestamp TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_session TEXT NOT NULL,
                to_session TEXT NOT NULL,
                content TEXT NOT NULL,
                msg_type TEXT NOT NULL DEFAULT 'info',
                read INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_sessions_state ON sessions(state);
            CREATE INDEX IF NOT EXISTS idx_tool_log_session ON tool_log(session_id);
            CREATE INDEX IF NOT EXISTS idx_messages_to ON messages(to_session, read);
            ",
        )?;
        self.ensure_sessions_pid_column()?;
        Ok(())
    }

    fn ensure_sessions_pid_column(&self) -> Result<()> {
        let mut stmt = self.conn.prepare("PRAGMA table_info(sessions)")?;
        let mut rows = stmt.query([])?;

        while let Some(row) = rows.next()? {
            let column_name: String = row.get(1)?;
            if column_name == "pid" {
                return Ok(());
            }
        }

        self.conn
            .execute("ALTER TABLE sessions ADD COLUMN pid INTEGER", [])?;
        Ok(())
    }

    pub fn insert_session(&self, session: &Session) -> Result<()> {
        self.conn.execute(
            "INSERT INTO sessions (id, task, agent_type, state, pid, worktree_path, worktree_branch, worktree_base, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)",
            rusqlite::params![
                session.id,
                session.task,
                session.agent_type,
                session.state.to_string(),
                session.pid.map(i64::from),
                session.worktree.as_ref().map(|w| w.path.to_string_lossy().to_string()),
                session.worktree.as_ref().map(|w| w.branch.clone()),
                session.worktree.as_ref().map(|w| w.base_branch.clone()),
                session.created_at.to_rfc3339(),
                session.updated_at.to_rfc3339(),
            ],
        )?;
        Ok(())
    }

    pub fn update_state_and_pid(
        &self,
        session_id: &str,
        state: &SessionState,
        pid: Option<u32>,
    ) -> Result<()> {
        self.conn.execute(
            "UPDATE sessions SET state = ?1, pid = ?2, updated_at = ?3 WHERE id = ?4",
            rusqlite::params![
                state.to_string(),
                pid.map(i64::from),
                chrono::Utc::now().to_rfc3339(),
                session_id,
            ],
        )?;
        Ok(())
    }

    pub fn update_state(&self, session_id: &str, state: &SessionState) -> Result<()> {
        self.conn.execute(
            "UPDATE sessions SET state = ?1, updated_at = ?2 WHERE id = ?3",
            rusqlite::params![
                state.to_string(),
                chrono::Utc::now().to_rfc3339(),
                session_id,
            ],
        )?;
        Ok(())
    }

    pub fn update_metrics(&self, session_id: &str, metrics: &SessionMetrics) -> Result<()> {
        self.conn.execute(
            "UPDATE sessions SET tokens_used = ?1, tool_calls = ?2, files_changed = ?3, duration_secs = ?4, cost_usd = ?5, updated_at = ?6 WHERE id = ?7",
            rusqlite::params![
                metrics.tokens_used,
                metrics.tool_calls,
                metrics.files_changed,
                metrics.duration_secs,
                metrics.cost_usd,
                chrono::Utc::now().to_rfc3339(),
                session_id,
            ],
        )?;
        Ok(())
    }

    pub fn list_sessions(&self) -> Result<Vec<Session>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, task, agent_type, state, pid, worktree_path, worktree_branch, worktree_base,
                    tokens_used, tool_calls, files_changed, duration_secs, cost_usd,
                    created_at, updated_at
             FROM sessions ORDER BY updated_at DESC",
        )?;

        let sessions = stmt
            .query_map([], |row| {
                let state_str: String = row.get(3)?;
                let state = match state_str.as_str() {
                    "running" => SessionState::Running,
                    "idle" => SessionState::Idle,
                    "completed" => SessionState::Completed,
                    "failed" => SessionState::Failed,
                    "stopped" => SessionState::Stopped,
                    _ => SessionState::Pending,
                };

                let pid = row
                    .get::<_, Option<i64>>(4)?
                    .and_then(|value| u32::try_from(value).ok());

                let worktree_path: Option<String> = row.get(5)?;
                let worktree = worktree_path.map(|p| super::WorktreeInfo {
                    path: std::path::PathBuf::from(p),
                    branch: row.get::<_, String>(6).unwrap_or_default(),
                    base_branch: row.get::<_, String>(7).unwrap_or_default(),
                });

                let created_str: String = row.get(13)?;
                let updated_str: String = row.get(14)?;

                Ok(Session {
                    id: row.get(0)?,
                    task: row.get(1)?,
                    agent_type: row.get(2)?,
                    state,
                    pid,
                    worktree,
                    created_at: chrono::DateTime::parse_from_rfc3339(&created_str)
                        .unwrap_or_default()
                        .with_timezone(&chrono::Utc),
                    updated_at: chrono::DateTime::parse_from_rfc3339(&updated_str)
                        .unwrap_or_default()
                        .with_timezone(&chrono::Utc),
                    metrics: SessionMetrics {
                        tokens_used: row.get(8)?,
                        tool_calls: row.get(9)?,
                        files_changed: row.get(10)?,
                        duration_secs: row.get(11)?,
                        cost_usd: row.get(12)?,
                    },
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(sessions)
    }

    pub fn get_session(&self, id: &str) -> Result<Option<Session>> {
        let sessions = self.list_sessions()?;
        Ok(sessions
            .into_iter()
            .find(|s| s.id == id || s.id.starts_with(id)))
    }

    pub fn send_message(&self, from: &str, to: &str, content: &str, msg_type: &str) -> Result<()> {
        self.conn.execute(
            "INSERT INTO messages (from_session, to_session, content, msg_type, timestamp)
             VALUES (?1, ?2, ?3, ?4, ?5)",
            rusqlite::params![from, to, content, msg_type, chrono::Utc::now().to_rfc3339()],
        )?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::session::{Session, SessionMetrics, SessionState};
    use std::path::PathBuf;

    fn temp_db_path() -> PathBuf {
        std::env::temp_dir().join(format!("ecc2-store-test-{}.db", uuid::Uuid::new_v4()))
    }

    fn sample_session(id: &str, state: SessionState, pid: Option<u32>) -> Session {
        let now = chrono::Utc::now();
        Session {
            id: id.to_string(),
            task: "Investigate crash".to_string(),
            agent_type: "claude".to_string(),
            state,
            pid,
            worktree: None,
            created_at: now,
            updated_at: now,
            metrics: SessionMetrics::default(),
        }
    }

    #[test]
    fn open_migrates_existing_sessions_table_with_pid_column() -> Result<()> {
        let path = temp_db_path();
        let conn = Connection::open(&path)?;
        conn.execute_batch(
            "
            CREATE TABLE sessions (
                id TEXT PRIMARY KEY,
                task TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                state TEXT NOT NULL DEFAULT 'pending',
                worktree_path TEXT,
                worktree_branch TEXT,
                worktree_base TEXT,
                tokens_used INTEGER DEFAULT 0,
                tool_calls INTEGER DEFAULT 0,
                files_changed INTEGER DEFAULT 0,
                duration_secs INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            ",
        )?;
        conn.execute(
            "INSERT INTO sessions (id, task, agent_type, state, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            rusqlite::params![
                "legacy",
                "Recover state",
                "claude",
                "running",
                chrono::Utc::now().to_rfc3339(),
                chrono::Utc::now().to_rfc3339(),
            ],
        )?;
        drop(conn);

        let store = StateStore::open(&path)?;
        let session = store
            .get_session("legacy")?
            .expect("legacy session should load");

        assert_eq!(session.pid, None);

        let _ = std::fs::remove_file(path);
        Ok(())
    }

    #[test]
    fn insert_session_persists_pid() -> Result<()> {
        let path = temp_db_path();
        let store = StateStore::open(&path)?;
        let session = sample_session("abc12345", SessionState::Running, Some(4242));

        store.insert_session(&session)?;

        let loaded = store
            .get_session("abc12345")?
            .expect("session should be persisted");
        assert_eq!(loaded.pid, Some(4242));
        assert_eq!(loaded.state, SessionState::Running);

        let _ = std::fs::remove_file(path);
        Ok(())
    }
}
