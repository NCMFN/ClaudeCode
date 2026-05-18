import math
from typing import List, Dict

class Evaluator:
    """
    Evaluates the multi-agent framework across several metrics.
    """

    @staticmethod
    def calculate_pass_at_k(n: int, c: int, k: int) -> float:
        """
        Calculates pass@k metric.
        n: total number of samples generated per problem
        c: number of correct samples
        k: k in pass@k
        """
        if n - c < k:
            return 1.0
        return 1.0 - math.prod(1.0 - k / i for i in range(n - c + 1, n + 1))

    @staticmethod
    def calculate_traceability(requirements: List[str], generated_code: str) -> float:
        """
        Simulates calculating requirement traceability.
        In reality, this would involve NLP to map reqs to code blocks.
        Here we do a naive keyword matching score.
        """
        if not requirements or not generated_code:
            return 0.0

        code_lower = generated_code.lower()
        matched = sum(1 for req in requirements if any(word.lower() in code_lower for word in req.split() if len(word) > 4))

        return matched / len(requirements)

    @staticmethod
    def calculate_verification_accuracy(bugs_injected: int, bugs_caught: int) -> float:
        """
        Ratio of bugs caught vs total bugs injected.
        """
        if bugs_injected == 0:
            return 1.0
        return bugs_caught / bugs_injected

    @staticmethod
    def calculate_bleu(reference: str, candidate: str) -> float:
        """
        Simplified BLEU score calculation for documentation quality.
        """
        if not reference or not candidate:
            return 0.0

        ref_words = set(reference.lower().split())
        cand_words = set(candidate.lower().split())

        if not cand_words:
            return 0.0

        overlap = len(ref_words.intersection(cand_words))
        return overlap / len(cand_words)

    @staticmethod
    def calculate_sdlc_completion_rate(total_tasks: int, completed_tasks: int) -> float:
        """
        Percentage of tasks fully completed without human intervention.
        """
        if total_tasks == 0:
            return 0.0
        return (completed_tasks / total_tasks) * 100.0

    def evaluate_framework(self, results_data: Dict) -> Dict:
        """
        Runs full evaluation based on aggregated task results.
        """
        metrics = {
            "pass_at_1": self.calculate_pass_at_k(10, results_data.get('correct_samples', 8), 1),
            "traceability_score": self.calculate_traceability(
                results_data.get('sample_reqs', []),
                results_data.get('sample_code', '')
            ),
            "verification_accuracy": self.calculate_verification_accuracy(
                results_data.get('bugs_injected', 10),
                results_data.get('bugs_caught', 8)
            ),
            "documentation_bleu": self.calculate_bleu(
                results_data.get('ref_doc', 'Example reference documentation string'),
                results_data.get('gen_doc', 'Example candidate documentation string generated')
            ),
            "sdlc_completion_rate": self.calculate_sdlc_completion_rate(
                results_data.get('total_tasks', 100),
                results_data.get('completed_tasks', 85)
            )
        }
        return metrics

if __name__ == "__main__":
    evaluator = Evaluator()
    dummy_data = {
        'correct_samples': 8,
        'sample_reqs': ['implement a binary tree', 'include a search method'],
        'sample_code': 'class Node: pass\nclass BinaryTree: def search(self): pass',
        'bugs_injected': 20,
        'bugs_caught': 18,
        'ref_doc': 'A class representing a binary tree with search capability.',
        'gen_doc': 'Binary tree class. Includes search method.',
        'total_tasks': 50,
        'completed_tasks': 48
    }
    print("Dummy Evaluation Results:", evaluator.evaluate_framework(dummy_data))
