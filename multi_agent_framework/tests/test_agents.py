from evaluation.evaluate import Evaluator

def test_evaluator_pass_at_k():
    evaluator = Evaluator()
    score = evaluator.calculate_pass_at_k(10, 10, 1)
    assert score == 1.0

def test_evaluator_traceability():
    evaluator = Evaluator()
    score = evaluator.calculate_traceability(["binary search"], "def binary_search(): pass")
    assert score > 0.0
