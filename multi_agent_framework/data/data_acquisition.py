from datasets import load_dataset
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetManager:
    def __init__(self, data_dir: str = "data_cache"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.datasets = {}

    def fetch_datasets(self):
        """
        Fetches the required datasets using HuggingFace datasets library.
        To avoid massive downloads during testing, we load subsets or streaming where applicable.
        """
        logger.info("Starting dataset acquisition...")

        try:
            # HumanEval (Code generation benchmark)
            logger.info("Loading HumanEval...")
            self.datasets['humaneval'] = load_dataset("openai_humaneval", split="test")

            # MBPP (Mostly Basic Python Problems)
            logger.info("Loading MBPP...")
            self.datasets['mbpp'] = load_dataset("mbpp", split="test")

            # SWE-bench (real-world GitHub issue resolution)
            logger.info("Loading SWE-bench...")
            self.datasets['swe_bench'] = load_dataset("princeton-nlp/SWE-bench", split="test")

            # CodeSearchNet (code + documentation pairs)
            # Using a smaller split for demonstration
            logger.info("Loading CodeSearchNet (Python)...")
            self.datasets['codesearchnet'] = load_dataset("code_search_net", "python", split="validation", trust_remote_code=True)

            # The Stack (Large multilingual code corpus)
            # Streaming because it's massive
            logger.info("Setting up streaming for The Stack...")
            self.datasets['the_stack'] = load_dataset("bigcode/the-stack", split="train", streaming=True, trust_remote_code=True)

            # CodeXGLUE (multi-task code benchmark) - using code-to-text python subset as an example
            logger.info("Loading CodeXGLUE...")
            self.datasets['codexglue'] = load_dataset("code_x_glue_ct_code_to_text", "python", split="validation", trust_remote_code=True)

            # CommitPackFT (instruction-tuned code commits)
            logger.info("Loading CommitPackFT (Python)...")
            self.datasets['commitpackft'] = load_dataset("bigcode/commitpackft", "python", split="train", trust_remote_code=True)

            logger.info("Dataset acquisition complete.")
            return True

        except Exception as e:
            logger.error(f"Error fetching datasets: {e}")
            return False

if __name__ == "__main__":
    manager = DatasetManager()
    manager.fetch_datasets()
