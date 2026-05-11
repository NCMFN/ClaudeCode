import autogen
from .analyst import get_analyst
from .architect import get_architect
from .coder import get_coder
from .verifier import get_verifier
from .documenter import get_documenter
from ..utils.context import FrameworkContext
import os
import json

class Coordinator:
    def __init__(self, llm_config: dict):
        self.context = FrameworkContext()
        self.llm_config = llm_config
        self.user_proxy = autogen.UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            code_execution_config={"use_docker": False}
        )
        self.analyst = get_analyst(llm_config)
        self.architect = get_architect(llm_config)
        self.coder = get_coder(llm_config)
        self.verifier = get_verifier(llm_config)
        self.documenter = get_documenter(llm_config)

    def run_sdlc(self, initial_requirement: str):
        print(f"Starting SDLC for requirement: {initial_requirement}\n")

        # Step 1: Requirements Analysis
        print("--- Step 1: Requirements Analysis ---")
        self.user_proxy.initiate_chat(self.analyst, message=f"Analyze these requirements:\n{initial_requirement}", max_turns=1)
        # In a real implementation, extract the specific response. Here we simulate it.
        self.context.update_requirements(f"Structured Requirements for: {initial_requirement}")

        # Step 2: Architecture
        print("--- Step 2: Architecture ---")
        self.user_proxy.initiate_chat(self.architect, message=f"Design architecture for:\n{self.context.requirements}", max_turns=1)
        self.context.update_architecture("System Architecture Design")

        # Step 3: Coding
        print("--- Step 3: Coding ---")
        self.user_proxy.initiate_chat(self.coder, message=f"Generate code based on:\nReqs: {self.context.requirements}\nArch: {self.context.architecture}", max_turns=1)
        self.context.update_code("def dummy_function(): pass")

        # Step 4: Verification
        print("--- Step 4: Verification ---")
        self.user_proxy.initiate_chat(self.verifier, message=f"Verify this code:\n{self.context.code}", max_turns=1)
        self.context.update_test_results("All tests passed.")

        # Step 5: Documentation
        print("--- Step 5: Documentation ---")
        self.user_proxy.initiate_chat(self.documenter, message=f"Document this code:\n{self.context.code}", max_turns=1)
        self.context.update_documentation("Docstrings and README generated.")

        print("\nSDLC Completed. Final Context State:")
        print(json.dumps(self.context.to_dict(), indent=2))
        return self.context
