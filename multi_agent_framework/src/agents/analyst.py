from .base import create_agent
from ..utils.context import FrameworkContext

def get_analyst(llm_config: dict) -> 'AssistantAgent':
    system_message = (
        "You are the Requirement Analyst Agent. "
        "Your job is to parse natural language requirements into structured task specifications. "
        "Focus on defining the core features, constraints, and success criteria."
    )
    return create_agent("Requirement_Analyst", system_message, llm_config)
