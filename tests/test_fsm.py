import pytest
from src.fsm.fsm import EPDePINFSM

def test_initial_state():
    fsm = EPDePINFSM()
    assert fsm.get_state() == "S1_FULL"
    assert fsm.get_blockchain_ops() == {"poc": True, "relay": True}
    assert fsm.primary_task_active(fsm.get_state()) == True

def test_downward_transitions():
    fsm = EPDePINFSM()

    # Drop below T1 (60%) -> S2
    fsm.update_soc(59.0)
    assert fsm.get_state() == "S2_PROOF_ONLY"
    assert fsm.get_blockchain_ops() == {"poc": True, "relay": False}

    # Drop below T2 (35%) -> S4
    fsm.update_soc(34.0)
    assert fsm.get_state() == "S4_PRIMARY_ONLY"
    assert fsm.get_blockchain_ops() == {"poc": False, "relay": False}

def test_hysteresis():
    fsm = EPDePINFSM()

    # Drop to S2
    fsm.update_soc(59.0)
    assert fsm.get_state() == "S2_PROOF_ONLY"

    # Go back up slightly, should NOT transition back without +5% hysteresis
    fsm.update_soc(61.0)
    assert fsm.get_state() == "S2_PROOF_ONLY"

    # Go past hysteresis threshold (T1 + 5 = 65)
    fsm.update_soc(65.0)
    assert fsm.get_state() == "S1_FULL"

    # Drop to S4
    fsm.update_soc(34.0)
    assert fsm.get_state() == "S4_PRIMARY_ONLY"

    # Go back up slightly past T2 (35), should NOT transition
    fsm.update_soc(36.0)
    assert fsm.get_state() == "S4_PRIMARY_ONLY"

    # Go past T2 hysteresis (T2 + 5 = 40)
    fsm.update_soc(40.0)
    assert fsm.get_state() == "S2_PROOF_ONLY"

def test_primary_task_invariant():
    fsm = EPDePINFSM()
    for state in fsm.STATES:
        assert fsm.primary_task_active(state) == True

def test_no_blockchain_ops_in_s4():
    fsm = EPDePINFSM()
    fsm.update_soc(10.0) # Force to S4
    assert fsm.get_state() == "S4_PRIMARY_ONLY"
    ops = fsm.get_blockchain_ops()
    assert ops["poc"] == False
    assert ops["relay"] == False
