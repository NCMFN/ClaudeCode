from core.context import SharedContext

def test_shared_context_creation():
    context = SharedContext()
    task = context.create_task("T1", "A simple task")
    assert task.task_id == "T1"
    assert task.description == "A simple task"
    assert context.current_task_id == "T1"

def test_shared_context_retrieval():
    context = SharedContext()
    context.create_task("T1", "A simple task")
    task = context.get_task("T1")
    assert task.task_id == "T1"

def test_status_update():
    context = SharedContext()
    context.create_task("T1", "A simple task")
    context.update_task_status("T1", "in_progress")
    task = context.get_task("T1")
    assert task.status == "in_progress"
