from autogen import AssistantAgent

def create_agent(name: str, system_message: str, llm_config: dict) -> AssistantAgent:
    return AssistantAgent(
        name=name,
        system_message=system_message,
        llm_config=llm_config
    )
