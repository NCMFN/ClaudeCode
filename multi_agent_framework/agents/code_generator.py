from autogen import ConversableAgent
from core.context import SharedContext
from core.logger import AgentLogger
import re

class CodeGenerator:
    def __init__(self, llm_config: dict, context: SharedContext, logger: AgentLogger):
        self.context = context
        self.logger = logger
        self.agent = ConversableAgent(
            name="CodeGenerator",
            system_message="""You are the Code Generation agent. Your role is to produce modular, high-quality Python code based on architectural notes and requirements.
Return your code enclosed in ```python ... ``` blocks. Include clear function signatures and types.""",
            llm_config=llm_config,
        )

    def generate_code(self) -> str:
        task = self.context.get_current_task()
        self.logger.log_event("CodeGenerationStarted", f"Task {task.task_id}")

        reqs_str = "\n".join([f"- {r}" for r in task.requirements])
        prompt = f"Generate Python 3.10+ code for the following architecture and requirements:\n\nRequirements:\n{reqs_str}\n\nArchitecture:\n{task.architecture_notes}\n\nProvide the code in ```python ``` blocks."

        reply = self.agent.generate_reply(messages=[{"role": "user", "content": prompt}])

        # Extract code blocks
        code_blocks = re.findall(r'```python(.*?)```', reply, re.DOTALL)
        if code_blocks:
            task.code_snippets['main'] = "\n\n".join(b.strip() for b in code_blocks)
        else:
            # Fallback if no block found
            task.code_snippets['main'] = reply

        task.status = "code_generated"

        self.logger.log_event("CodeGenerationCompleted", f"Task {task.task_id}")
        return reply
