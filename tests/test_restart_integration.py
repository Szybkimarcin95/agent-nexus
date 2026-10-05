import json, os, subprocess, sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]

def command(tmp_path, script, *args, check=True):
    env = dict(os.environ, NEXUS_TEST_MODEL="1", NEXUS_STATE_DIR=str(tmp_path))
    env.pop("OPENAI_API_KEY", None)
    return subprocess.run([sys.executable, str(ROOT / script), *args],
        cwd=ROOT, env=env, capture_output=True, text=True, check=check, timeout=90)

def pause(tmp_path):
    result = command(tmp_path, "szy7_pause.py")
    return next(x for x in result.stdout.splitlines() if x.startswith("RUN-"))

@pytest.mark.parametrize("decision,status,expected", [
    ("approved", "completed", "approved:restart-proof"),
    ("rejected", "denied", "rejected by external reviewer"),
])
def test_actual_sdk_restart(tmp_path, decision, status, expected):
    run_id = pause(tmp_path)
    path = tmp_path / (run_id + ".json")
    paused = json.loads(path.read_text())
    assert paused["status"] == "paused_approval"
    assert paused["call_id"] == "call_restart_probe"
    command(tmp_path, "szy7_review.py", run_id, decision)
    result = command(tmp_path, "szy7_resume.py", run_id)
    assert "RESUME_STATUS=" + status in result.stdout
    final = json.loads(path.read_text())
    assert final["status"] == status
    assert expected in final["final_output"]
    before = path.read_bytes()
    command(tmp_path, "szy7_resume.py", run_id)
    assert path.read_bytes() == before

def test_unresolved_stays_pending(tmp_path):
    run_id = pause(tmp_path)
    path = tmp_path / (run_id + ".json")
    before = path.read_bytes()
    result = command(tmp_path, "szy7_resume.py", run_id)
    assert "RESUME_STATUS=pending" in result.stdout
    assert path.read_bytes() == before

@pytest.mark.parametrize("field", ["run_id", "action_id", "tool", "decision"])
def test_rejects_mismatched_record(tmp_path, field):
    run_id = pause(tmp_path)
    command(tmp_path, "szy7_review.py", run_id, "approved")
    path = tmp_path / (run_id + ".approval.json")
    record = json.loads(path.read_text())
    record[field] = "wrong"
    path.write_text(json.dumps(record))
    result = command(tmp_path, "szy7_resume.py", run_id, check=False)
    assert result.returncode != 0
    assert json.loads((tmp_path / (run_id + ".json")).read_text())["status"] == "paused_approval"

def test_conflicting_review_rejected(tmp_path):
    run_id = pause(tmp_path)
    command(tmp_path, "szy7_review.py", run_id, "approved")
    result = command(tmp_path, "szy7_review.py", run_id, "rejected", check=False)
    assert result.returncode != 0
    assert "conflicting approval" in result.stderr
