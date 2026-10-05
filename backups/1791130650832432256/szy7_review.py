import json, sys
from pathlib import Path

if len(sys.argv) != 3 or sys.argv[2] not in {"approved", "rejected"}:
    raise SystemExit("usage: szy7_review.py RUN-ID approved|rejected")

run_id, decision = sys.argv[1], sys.argv[2]
state_dir = Path(__file__).parent / "state"
run_path = state_dir / f"{run_id}.json"
envelope = json.loads(run_path.read_text(encoding="utf-8"))
record = {
    "run_id": run_id,
    "action_id": envelope["call_id"],
    "tool": envelope["tool_name"],
    "decision": decision,
    "decided_by": "human:external",
}
approval_path = state_dir / f"{run_id}.approval.json"
approval_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
print(f"APPROVAL_WRITTEN={decision}")
