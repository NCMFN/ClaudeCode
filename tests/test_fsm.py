import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.fsm.ep_depin_fsm import EPDePINFSM

def test_s1_state():
    fsm = EPDePINFSM()
    assert fsm.get_state(80) == 'S1_FULL'

def test_s2_state():
    fsm = EPDePINFSM()
    assert fsm.get_state(50) == 'S2_PROOF_ONLY'

def test_s3_state():
    fsm = EPDePINFSM()
    assert fsm.get_state(25) == 'S3_RELAY_ONLY'

def test_s4_state():
    fsm = EPDePINFSM()
    assert fsm.get_state(10) == 'S4_PRIMARY_ONLY'

def test_primary_task_invariant():
    fsm = EPDePINFSM()
    for state in EPDePINFSM.STATES:
        assert fsm.primary_task_active(state) == True

def test_hysteresis():
    fsm = EPDePINFSM()
    # Go to S2
    fsm.get_state(58)
    assert fsm.current_state == 'S2_PROOF_ONLY'
    # Try to go to S1 at 62 (hysteresis is 60+5=65)
    fsm.get_state(62)
    assert fsm.current_state == 'S2_PROOF_ONLY'
    # Exceed hysteresis
    fsm.get_state(66)
    assert fsm.current_state == 'S1_FULL'

def test_no_blockchain_in_s4():
    fsm = EPDePINFSM()
    ops = fsm.get_blockchain_ops('S4_PRIMARY_ONLY')
    assert ops['sign_proofs'] == False
    assert ops['submit_tx'] == False
    assert ops['relay_peers'] == False
