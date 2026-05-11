from .base import create_agent
from ..utils.context import FrameworkContext

def get_verifier(llm_config: dict) -> 'AssistantAgent':
    system_message = (
        "You are the Verification Agent. "
        "Write unit tests (using pytest) for the generated code. "
        "Perform static analysis and logic checks to identify potential bugs."
    )
    return create_agent("Verifier", system_message, llm_config)
