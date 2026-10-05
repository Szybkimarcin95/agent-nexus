import json, os, re, tempfile
from pathlib import Path

def state_dir():
    p = Path(os.environ.get("NEXUS_STATE_DIR", Path(__file__).parent / "state"))
    p.mkdir(parents=True, exist_ok=True)
    return p

def run_path(run_id):
    if not re.fullmatch(r"RUN-[A-Za-z0-9-]+", run_id):
        raise ValueError("invalid run ID")
    return state_dir() / (run_id + ".json")

def atomic_json(path, value):
    fd, tmp = tempfile.mkstemp(prefix=".nexus-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(value, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def validate_decision(env, record):
    for key, expected in (("run_id", env["run_id"]), ("action_id", env["call_id"]),
                          ("tool", env["tool_name"])):
        if record.get(key) != expected:
            raise ValueError("approval mismatch: " + key)
    if record.get("decision") not in {"approved", "rejected"}:
        raise ValueError("invalid decision")
    if not record.get("decided_by"):
        raise ValueError("missing reviewer")
