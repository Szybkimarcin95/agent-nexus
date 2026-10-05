import pytest
from eval.simulate_workflow import FullWorkflowSimulation
from invariants import InvariantViolation


def test_supervisor_full_cycle(tmp_path):
    result = FullWorkflowSimulation(tmp_path).simulate_full_cycle("release simulation")
    assert result["phases_completed"] == 4
    assert result["final_status"] == "COMPLETED"
    assert result["test_scope_replays"] == 1
    assert result["audit_problems"] == 0
    assert result["write_exercise_ok"] is True


def test_graph_researcher_is_denied(tmp_path):
    with pytest.raises(InvariantViolation):
        FullWorkflowSimulation(tmp_path).simulate_full_cycle(
            "write must be denied", role="GraphResearcher"
        )
