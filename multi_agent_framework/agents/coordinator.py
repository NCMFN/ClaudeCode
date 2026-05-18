from core.context import SharedContext
from core.logger import AgentLogger
from .requirement_analyst import RequirementAnalyst
from .architect import Architect
from .code_generator import CodeGenerator
from .verification import VerificationAgent
from .documentation import DocumentationAgent

class CoordinatorAgent:
    def __init__(self, llm_config: dict, context: SharedContext, logger: AgentLogger):
        self.context = context
        self.logger = logger

        self.req_analyst = RequirementAnalyst(llm_config, context, logger)
        self.architect = Architect(llm_config, context, logger)
        self.code_gen = CodeGenerator(llm_config, context, logger)
        self.verifier = VerificationAgent(llm_config, context, logger)
        self.doc_gen = DocumentationAgent(llm_config, context, logger)

    def run_sdlc(self, task_id: str, raw_requirements: str) -> dict:
        """
        Executes the full SDLC pipeline dynamically, simulating inter-agent handoffs.
        """
        self.logger.log_event("SDLC_Started", f"Task {task_id}")
        task = self.context.create_task(task_id, raw_requirements)

        try:
            # Phase 1: Requirements
            self.logger.log_communication("Coordinator", "RequirementAnalyst", "Starting analysis")
            self.req_analyst.analyze(raw_requirements)

            # Phase 2: Architecture
            self.logger.log_communication("Coordinator", "Architect", "Starting architecture design")
            self.architect.design_architecture()

            # Phase 3: Code Generation & Verification Loop
            max_retries = 3
            for attempt in range(max_retries):
                self.logger.log_communication("Coordinator", "CodeGenerator", f"Generating code (Attempt {attempt+1})")
                self.code_gen.generate_code()

                self.logger.log_communication("Coordinator", "VerificationAgent", "Starting verification")
                results = self.verifier.verify_code()

                if results.get("passed", False):
                    break
                else:
                    self.logger.log_communication("VerificationAgent", "CodeGenerator", "Verification failed, please fix code.")
                    # In a fully dynamic system, the CodeGenerator would see the verifier's feedback.
                    # Here we append it to the architecture notes to inform the next generation attempt.
                    task.architecture_notes += f"\n\nFIX REQUEST:\n{results.get('review', '')}"

            # Phase 4: Documentation
            if task.status in ["verified", "code_generated"]: # Proceed if code exists
                self.logger.log_communication("Coordinator", "DocumentationAgent", "Starting documentation generation")
                self.doc_gen.generate_documentation()
                task.status = "completed"
            else:
                task.status = "failed_verification"

        except Exception as e:
            self.logger.log_event("SDLC_Error", str(e))
            task.status = "error"

        self.logger.log_event("SDLC_Completed", f"Task {task_id} finished with status {task.status}")

        return {
            "status": task.status,
            "requirements": task.requirements,
            "code": task.code_snippets.get('main', ''),
            "documentation": task.documentation,
            "verification_results": task.test_results
        }
