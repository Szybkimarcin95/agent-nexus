import json, sys
from szy7_store import run_path, atomic_json

def main():
    if len(sys.argv) != 3 or sys.argv[2] not in {"approved", "rejected"}:
        raise SystemExit("usage: szy7_review.py RUN-ID approved|rejected")
    run_id, decision = sys.argv[1:]
    path = run_path(run_id)
    env = json.loads(path.read_text())
    if env["status"] != "paused_approval":
        raise ValueError("run is not awaiting approval")
    record = {"run_id": run_id, "action_id": env["call_id"],
        "tool": env["tool_name"], "decision": decision, "decided_by": "human:external"}
    approval_path = path.with_suffix(".approval.json")
    if approval_path.exists():
        if json.loads(approval_path.read_text()) != record:
            raise ValueError("conflicting approval already exists")
    else:
        atomic_json(approval_path, record)
    print("APPROVAL_WRITTEN=" + decision)

if __name__ == "__main__":
    main()
