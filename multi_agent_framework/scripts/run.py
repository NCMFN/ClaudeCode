import os
import sys
# Add parent directory to path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.coordinator import Coordinator

def main():
    # Use dummy config if not set
    api_key = os.getenv("OPENAI_API_KEY", "dummy-key-for-testing")
    llm_config = {
        "config_list": [{"model": "gpt-4", "api_key": api_key}],
        "cache_seed": 42
    }

    coordinator = Coordinator(llm_config)
    coordinator.run_sdlc("Create a simple calculator function that adds two numbers.")

if __name__ == "__main__":
    main()
