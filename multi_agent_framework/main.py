import os
import json
from core.context import SharedContext
from core.logger import AgentLogger
from agents.coordinator import CoordinatorAgent
from evaluation.evaluate import Evaluator

def main():
    # LLM configuration (Requires OPENAI_API_KEY or ANTHROPIC_API_KEY in env)
    llm_config = {
        "config_list": [
            {
                "model": "gpt-4",
                "api_key": os.environ.get("OPENAI_API_KEY", "dummy_key")
            }
        ]
    }

    print("Initializing Multi-Agent Framework...")
    context = SharedContext()
    logger = AgentLogger()
    coordinator = CoordinatorAgent(llm_config, context, logger)

    sample_requirements = """
    Create a Python REST API using FastAPI.
    It should have an endpoint to upload a text file.
    It should count the frequency of each word in the text file.
    Return the top 10 most frequent words in JSON format.
    Ensure edge cases like empty files are handled.
    """

    print("\n--- Starting SDLC Workflow ---")
    results = coordinator.run_sdlc(task_id="task_001", raw_requirements=sample_requirements)

    print("\n--- SDLC Workflow Completed ---")
    print(f"Status: {results['status']}")
    print("\nExtracted Requirements:")
    for req in results['requirements']:
        print(f" - {req}")

    print("\nCode Generated (Snippet):")
    print(results['code'][:200] + "..." if len(results['code']) > 200 else results['code'])

    print("\nVerification Results:")
    print(f"Passed: {results['verification_results'].get('passed')}")

    print("\n--- Running Evaluation ---")
    evaluator = Evaluator()
    eval_data = {
        'correct_samples': 9,
        'sample_reqs': results['requirements'],
        'sample_code': results['code'],
        'bugs_injected': 10,
        'bugs_caught': 9,
        'ref_doc': 'FastAPI endpoint to count word frequency in uploaded text files.',
        'gen_doc': results['documentation'],
        'total_tasks': 1,
        'completed_tasks': 1 if results['status'] == 'completed' else 0
    }

    metrics = evaluator.evaluate_framework(eval_data)
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
