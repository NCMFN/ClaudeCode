from .base import create_agent
from ..utils.context import FrameworkContext

def get_architect(llm_config: dict) -> 'AssistantAgent':
    system_message = (
        "You are the Architect Agent. "
        "Based on structured requirements, design the system architecture and module breakdown. "
        "Specify the high-level components, their interactions, and data flows."
    )
    return create_agent("Architect", system_message, llm_config)
