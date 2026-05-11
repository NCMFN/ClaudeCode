# Setup Guide for Multi-Agent Autonomous Framework

## Prerequisites
- Python 3.10+
- An OpenAI or Anthropic API key

## Installation
1. Clone the repository.
2. Navigate to the `multi_agent_framework` directory:
   ```bash
   cd multi_agent_framework
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
Set your API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key"
# OR
export ANTHROPIC_API_KEY="your-api-key"
```

## Running the Framework
Execute the coordinator script to start the development loop:
```bash
python scripts/run.py
```

## Running Tests
Execute pytest from the root of the multi_agent_framework directory:
```bash
pytest tests/
```
