from autogen import ConversableAgent
from core.context import SharedContext
from core.logger import AgentLogger

class DocumentationAgent:
    def __init__(self, llm_config: dict, context: SharedContext, logger: AgentLogger):
        self.context = context
        self.logger = logger
        self.agent = ConversableAgent(
            name="DocumentationAgent",
            system_message="""You are the Documentation agent. Your role is to auto-generate docstrings, README sections, and API docs based on the provided code and requirements.""",
            llm_config=llm_config,
        )

    def generate_documentation(self) -> str:
        task = self.context.get_current_task()
        self.logger.log_event("DocumentationGenerationStarted", f"Task {task.task_id}")

        code = task.code_snippets.get('main', '')
        reqs_str = "\n".join([f"- {r}" for r in task.requirements])

        prompt = f"Generate comprehensive documentation (including a brief README section and API docs) for the following code, based on these requirements:\n\nRequirements:\n{reqs_str}\n\nCode:\n```python\n{code}\n```"

        reply = self.agent.generate_reply(messages=[{"role": "user", "content": prompt}])

        task.documentation = reply
        task.status = "documented"

        self.logger.log_event("DocumentationGenerationCompleted", f"Task {task.task_id}")
        return reply
