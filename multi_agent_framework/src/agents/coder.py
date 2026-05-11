from .base import create_agent
from ..utils.context import FrameworkContext

def get_coder(llm_config: dict) -> 'AssistantAgent':
    system_message = (
        "You are the Code Generation Agent. "
        "Write modular Python 3.10+ code based on the architecture and requirements provided. "
        "Ensure the code is clean, efficient, and well-structured."
    )
    return create_agent("Coder", system_message, llm_config)
