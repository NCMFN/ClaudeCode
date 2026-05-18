from autogen import ConversableAgent
from core.context import SharedContext
from core.logger import AgentLogger

class Architect:
    def __init__(self, llm_config: dict, context: SharedContext, logger: AgentLogger):
        self.context = context
        self.logger = logger
        self.agent = ConversableAgent(
            name="Architect",
            system_message="""You are the Architect agent. Your role is to design system architecture and module breakdown based on structured requirements.
Provide a clear architectural overview, including key components, data flow, and technologies to be used.""",
            llm_config=llm_config,
        )

    def design_architecture(self) -> str:
        task = self.context.get_current_task()
        self.logger.log_event("ArchitectureDesignStarted", f"Task {task.task_id}")

        reqs_str = "\n".join([f"- {r}" for r in task.requirements])
        prompt = f"Design the system architecture and module breakdown for the following requirements:\n{reqs_str}\n\nProvide the architectural notes."

        reply = self.agent.generate_reply(messages=[{"role": "user", "content": prompt}])

        task.architecture_notes = reply
        task.status = "architecture_designed"

        self.logger.log_event("ArchitectureDesignCompleted", f"Task {task.task_id}")
        return reply
