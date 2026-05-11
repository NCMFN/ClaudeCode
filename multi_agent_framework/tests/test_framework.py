import pytest
import sys
import os

# Add parent directory to path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.context import FrameworkContext
from src.agents.base import create_agent

def test_framework_context():
    ctx = FrameworkContext()
    assert ctx.requirements == ""

    ctx.update_requirements("Test requirement")
    assert ctx.requirements == "Test requirement"

    summary = ctx.get_context_summary()
    assert "true" in summary.lower()  # Should indicate requirements are set

    dict_repr = ctx.to_dict()
    assert dict_repr["requirements"] == "Test requirement"

def test_agent_creation():
    llm_config = {"config_list": [{"model": "gpt-4", "api_key": "dummy"}]}
    agent = create_agent("TestAgent", "System message", llm_config)
    assert agent.name == "TestAgent"
    assert agent.system_message == "System message"
