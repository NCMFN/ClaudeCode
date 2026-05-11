from .base import create_agent
from ..utils.context import FrameworkContext

def get_documenter(llm_config: dict) -> 'AssistantAgent':
    system_message = (
        "You are the Documentation Agent. "
        "Auto-generate docstrings, README, and API docs for the provided code. "
        "Ensure the documentation matches the code implementation."
    )
    return create_agent("Documenter", system_message, llm_config)
