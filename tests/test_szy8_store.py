import pytest
from durable_store import DurableStore, Budget, BudgetExceeded, IdempotencyConflict
def test_run_survives_new_store_instance(tmp_path):
    s=DurableStore(tmp_path); s.create_run("RUN-a",state={"phase":"paused"}); s.consume("RUN-a",tool_calls=1,tokens=12)
    d=DurableStore(tmp_path).load_run("RUN-a"); assert d["state"]["phase"]=="paused" and d["usage"]["tool_calls"]==1
def test_budget_terminates_deterministically(tmp_path):
    s=DurableStore(tmp_path); s.create_run("RUN-b",Budget(max_tool_calls=1,max_tokens=50,max_runtime_seconds=60)); s.consume("RUN-b",tool_calls=1)
    with pytest.raises(BudgetExceeded,match="max_tool_calls"): s.consume("RUN-b",tool_calls=1)
    assert s.load_run("RUN-b")["status"]=="budget_exceeded"
def test_token_and_runtime_budgets(tmp_path):
    s=DurableStore(tmp_path); s.create_run("RUN-c",Budget(max_tool_calls=9,max_tokens=3,max_runtime_seconds=60))
    with pytest.raises(BudgetExceeded,match="max_tokens"): s.consume("RUN-c",tokens=4)
    s.create_run("RUN-d",Budget(max_runtime_seconds=1)); d=s.load_run("RUN-d")
    with pytest.raises(BudgetExceeded,match="max_runtime_seconds"): s.consume("RUN-d",now=d["usage"]["started_at"]+2)
def test_idempotency_replays_same_effect_and_rejects_conflict(tmp_path):
    s=DurableStore(tmp_path); assert s.record_effect("github:issue:1","ok")=="ok"; assert s.record_effect("github:issue:1","ok")=="ok"
    with pytest.raises(IdempotencyConflict): s.record_effect("github:issue:1","different")
    assert s.has_effect("github:issue:1")
