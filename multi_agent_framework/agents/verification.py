from autogen import ConversableAgent
from core.context import SharedContext
from core.logger import AgentLogger
import tempfile
import os
import subprocess

class VerificationAgent:
    def __init__(self, llm_config: dict, context: SharedContext, logger: AgentLogger):
        self.context = context
        self.logger = logger
        self.agent = ConversableAgent(
            name="VerificationAgent",
            system_message="""You are the Verification agent. Your role is to analyze code for logic errors and suggest fixes. You also review test and static analysis results to ensure quality.""",
            llm_config=llm_config,
        )

    def run_static_analysis(self, code: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            result = subprocess.run(['pylint', temp_path], capture_output=True, text=True)
            output = result.stdout + "\n" + result.stderr
        except Exception as e:
            output = str(e)
        finally:
            os.remove(temp_path)

        return output

    def verify_code(self) -> dict:
        task = self.context.get_current_task()
        self.logger.log_event("VerificationStarted", f"Task {task.task_id}")

        code = task.code_snippets.get('main', '')
        if not code:
            return {"status": "error", "message": "No code to verify."}

        # Run static analysis
        pylint_output = self.run_static_analysis(code)

        # Ask LLM to review code and pylint output
        prompt = f"Review the following code and its pylint output. Are there any critical bugs or logic errors? If so, explain them and suggest fixes.\n\nCode:\n```python\n{code}\n```\n\nPylint Output:\n{pylint_output}"

        reply = self.agent.generate_reply(messages=[{"role": "user", "content": prompt}])

        passed = "critical" not in reply.lower() and "error" not in reply.lower()

        results = {
            "pylint_output": pylint_output,
            "review": reply,
            "passed": passed
        }

        task.test_results = results
        task.status = "verified" if passed else "verification_failed"

        self.logger.log_event("VerificationCompleted", f"Task {task.task_id}, Passed: {passed}")
        return results
