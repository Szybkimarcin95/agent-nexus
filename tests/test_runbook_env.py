from deployment.verify_env import verify_env, REQUIRED_JOBS

def test_safe_defaults(monkeypatch):
    for v in REQUIRED_JOBS: monkeypatch.delenv(v, raising=False)
    s=verify_env(False)
    assert s["ok"] is False  # password is intentionally required
    assert s["policy_state"]["AGENT_NEXUS_WRITE"]["value"]=="0"
    assert s["policy_state"]["NEO4J_READ_ONLY"]["value"]=="true"

def test_unlock_is_rejected(monkeypatch):
    monkeypatch.setenv("NEO4J_PASSWORD","x"); monkeypatch.setenv("AGENT_NEXUS_WRITE","1")
    s=verify_env(False); assert s["ok"] is False
    assert any("AGENT_NEXUS_WRITE" in x for x in s["warnings"])

def test_read_only_flags(monkeypatch):
    monkeypatch.setenv("NEO4J_PASSWORD","x"); monkeypatch.setenv("NEO4J_READ_ONLY","false")
    assert verify_env(False)["ok"] is False
