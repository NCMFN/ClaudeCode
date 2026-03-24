use anyhow::Result;
use std::fmt;

use super::store::StateStore;
use super::{Session, SessionMetrics, SessionState};
use crate::config::Config;
use crate::worktree;

pub async fn create_session(
    db: &StateStore,
    cfg: &Config,
    task: &str,
    agent_type: &str,
    use_worktree: bool,
) -> Result<String> {
    let id = uuid::Uuid::new_v4().to_string()[..8].to_string();
    let now = chrono::Utc::now();

    let wt = if use_worktree {
        Some(worktree::create_for_session(&id, cfg)?)
    } else {
        None
    };

    let session = Session {
        id: id.clone(),
        task: task.to_string(),
        agent_type: agent_type.to_string(),
        state: SessionState::Pending,
        pid: None,
        worktree: wt,
        created_at: now,
        updated_at: now,
        metrics: SessionMetrics::default(),
    };

    db.insert_session(&session)?;
    Ok(id)
}

pub fn list_sessions(db: &StateStore) -> Result<Vec<Session>> {
    db.list_sessions()
}

pub fn get_status(db: &StateStore, id: &str) -> Result<SessionStatus> {
    let session = db
        .get_session(id)?
        .ok_or_else(|| anyhow::anyhow!("Session not found: {id}"))?;
    Ok(SessionStatus(session))
}

pub async fn stop_session(db: &StateStore, id: &str) -> Result<()> {
    let session = db
        .get_session(id)?
        .ok_or_else(|| anyhow::anyhow!("Session not found: {id}"))?;

    db.update_state_and_pid(&session.id, &SessionState::Stopped, None)?;
    Ok(())
}

pub async fn resume_session(db: &StateStore, id: &str) -> Result<String> {
    let session = db
        .get_session(id)?
        .ok_or_else(|| anyhow::anyhow!("Session not found: {id}"))?;

    if session.state == SessionState::Completed {
        anyhow::bail!("Completed sessions cannot be resumed: {}", session.id);
    }

    if session.state == SessionState::Running {
        anyhow::bail!("Session is already running: {}", session.id);
    }

    db.update_state_and_pid(&session.id, &SessionState::Pending, None)?;
    Ok(session.id)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::session::store::StateStore;
    use std::path::PathBuf;

    fn temp_db_path() -> PathBuf {
        std::env::temp_dir().join(format!("ecc2-manager-test-{}.db", uuid::Uuid::new_v4()))
    }

    fn sample_session(id: &str, state: SessionState, pid: Option<u32>) -> Session {
        let now = chrono::Utc::now();
        Session {
            id: id.to_string(),
            task: "Resume previous task".to_string(),
            agent_type: "claude".to_string(),
            state,
            pid,
            worktree: None,
            created_at: now,
            updated_at: now,
            metrics: SessionMetrics::default(),
        }
    }

    #[tokio::test]
    async fn resume_session_requeues_failed_session() -> Result<()> {
        let path = temp_db_path();
        let store = StateStore::open(&path)?;
        store.insert_session(&sample_session(
            "deadbeef",
            SessionState::Failed,
            Some(31337),
        ))?;

        let resumed_id = resume_session(&store, "deadbeef").await?;
        let resumed = store
            .get_session(&resumed_id)?
            .expect("resumed session should exist");

        assert_eq!(resumed.state, SessionState::Pending);
        assert_eq!(resumed.pid, None);

        let _ = std::fs::remove_file(path);
        Ok(())
    }
}

pub struct SessionStatus(Session);

impl fmt::Display for SessionStatus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let s = &self.0;
        writeln!(f, "Session: {}", s.id)?;
        writeln!(f, "Task:    {}", s.task)?;
        writeln!(f, "Agent:   {}", s.agent_type)?;
        writeln!(f, "State:   {}", s.state)?;
        if let Some(pid) = s.pid {
            writeln!(f, "PID:     {pid}")?;
        }
        if let Some(ref wt) = s.worktree {
            writeln!(f, "Branch:  {}", wt.branch)?;
            writeln!(f, "Worktree: {}", wt.path.display())?;
        }
        writeln!(f, "Tokens:  {}", s.metrics.tokens_used)?;
        writeln!(f, "Tools:   {}", s.metrics.tool_calls)?;
        writeln!(f, "Files:   {}", s.metrics.files_changed)?;
        writeln!(f, "Cost:    ${:.4}", s.metrics.cost_usd)?;
        writeln!(f, "Created: {}", s.created_at)?;
        write!(f, "Updated: {}", s.updated_at)
    }
}
