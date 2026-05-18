from autogen import ConversableAgent
from core.context import SharedContext
from core.logger import AgentLogger

class RequirementAnalyst:
    def __init__(self, llm_config: dict, context: SharedContext, logger: AgentLogger):
        self.context = context
        self.logger = logger
        self.agent = ConversableAgent(
            name="RequirementAnalyst",
            system_message="""You are the Requirement Analyst agent. Your role is to parse natural language requirements into structured task specifications.
Extract key functional requirements, non-functional requirements, and constraints. Output them as a bulleted list.""",
            llm_config=llm_config,
        )

    def analyze(self, raw_requirements: str) -> str:
        task = self.context.get_current_task()
        self.logger.log_event("RequirementAnalysisStarted", f"Task {task.task_id}")

        # In a real dynamic setup, this agent would reply to a user proxy or coordinator.
        # Here we simulate the processing step directly for the framework integration.
        prompt = f"Analyze the following requirements and extract a structured list of technical requirements:\n\n{raw_requirements}"

        reply = self.agent.generate_reply(messages=[{"role": "user", "content": prompt}])

        task.requirements = [line.strip("- *").strip() for line in reply.split("\n") if line.strip().startswith(("-", "*"))]
        task.status = "requirements_analyzed"

        self.logger.log_event("RequirementAnalysisCompleted", f"Task {task.task_id}")
        return reply
