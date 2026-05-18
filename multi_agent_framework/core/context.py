from typing import Any, Dict, List
from pydantic import BaseModel, Field

class TaskSpec(BaseModel):
    task_id: str
    description: str
    requirements: List[str] = Field(default_factory=list)
    architecture_notes: str = ""
    code_snippets: Dict[str, str] = Field(default_factory=dict)
    test_results: Dict[str, Any] = Field(default_factory=dict)
    documentation: str = ""
    status: str = "initialized"

class SharedContext:
    """
    A shared context object to avoid context window drift between specialized agents.
    It holds the state of the current SDLC task.
    """
    def __init__(self):
        self.tasks: Dict[str, TaskSpec] = {}
        self.current_task_id: str | None = None

    def create_task(self, task_id: str, description: str) -> TaskSpec:
        task = TaskSpec(task_id=task_id, description=description)
        self.tasks[task_id] = task
        self.current_task_id = task_id
        return task

    def get_task(self, task_id: str) -> TaskSpec:
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found in shared context.")
        return self.tasks[task_id]

    def get_current_task(self) -> TaskSpec:
        if not self.current_task_id:
            raise ValueError("No task is currently active.")
        return self.get_task(self.current_task_id)

    def update_task_status(self, task_id: str, status: str):
        task = self.get_task(task_id)
        task.status = status
