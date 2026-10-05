import inspect
import agents
from agents import RunState, Runner, function_tool


def test_agents_import_and_version():
    assert tuple(map(int, agents.__version__.split('.')[:2])) >= (0, 23)


def test_runstate_contract():
    assert hasattr(RunState, 'to_json')
    assert hasattr(RunState, 'from_json')
    assert hasattr(RunState, 'get_interruptions')
    assert hasattr(RunState, 'approve')
    assert hasattr(RunState, 'reject')
    assert 'approval_item' in str(inspect.signature(RunState.approve))


def test_runner_accepts_runstate_input():
    sig = str(inspect.signature(Runner.run))
    assert 'RunState' in sig


def test_function_tool_supports_approval():
    sig = str(inspect.signature(function_tool))
    assert 'needs_approval' in sig
