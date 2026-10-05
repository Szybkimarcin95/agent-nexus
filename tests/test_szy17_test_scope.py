import pytest
from runtime_fallback.test_scope import TestScopeRuntime,gate_write_test
from invariants import InvariantViolation
def ok(): return [{"tool":"neo4j.write","decision":"approved"}]
def test_gate_and_namespace(tmp_path):
 x=gate_write_test("Supervisor","neo4j.write",{"x":1},"r1",ok()); assert x["authorized"] and x["idempotency_key"].startswith("test:")
def test_role_and_approval_block(tmp_path):
 with pytest.raises(InvariantViolation): gate_write_test("GraphResearcher","neo4j.write",{},"r1",ok())
 with pytest.raises(InvariantViolation): gate_write_test("Supervisor","neo4j.write",{},"r1",[])
def test_exercise_replay(tmp_path):
 out=TestScopeRuntime(tmp_path).exercise("r1"); assert out["replays"]==1
def test_prod_isolated(tmp_path):
 prod=tmp_path/"prod.sqlite"; rt=TestScopeRuntime(tmp_path); out=rt.exercise("r1"); assert rt.verify_no_production_leak(prod)["leak"] is False
