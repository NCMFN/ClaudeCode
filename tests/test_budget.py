import pytest
from coherence_safe_obfuscation.budget import calculate_budget_ns

def test_calculate_budget_standard():
    # T1s in us
    t1_times = [100.0, 150.0, 120.0]
    # min is 100.0 us = 100,000 ns
    # eta = 0.1 -> budget should be 10,000 ns
    budget = calculate_budget_ns(t1_times, eta=0.1)
    assert budget == 10000.0

def test_calculate_budget_zero_eta():
    t1_times = [100.0, 150.0]
    budget = calculate_budget_ns(t1_times, eta=0.0)
    assert budget == 0.0

def test_calculate_budget_zero_t1():
    t1_times = [0.0, 150.0]
    budget = calculate_budget_ns(t1_times, eta=0.1)
    assert budget == 0.0

def test_calculate_budget_empty():
    with pytest.raises(ValueError, match="Must provide at least one T1 time"):
        calculate_budget_ns([])

def test_calculate_budget_negative_eta():
    with pytest.raises(ValueError, match="Safety coefficient eta must be non-negative"):
        calculate_budget_ns([100.0], eta=-0.1)

def test_calculate_budget_negative_t1():
    with pytest.raises(ValueError, match="T1 times cannot be negative"):
        calculate_budget_ns([100.0, -50.0], eta=0.1)
