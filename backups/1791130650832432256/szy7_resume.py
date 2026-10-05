import asyncio, json, sys
from pathlib import Path
from agents import RunState, Runner
from szy7_common import build_agent

async def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: szy7_resume.py RUN-ID")
    run_id = sys.argv[1]
    state_dir = Path(__file__).parent / "state"
    env = json.loads((state_dir / f"{run_id}.json").read_text())
    approval = json.loads((state_dir / f"{run_id}.approval.json").read_text())
    agent = build_agent()
    state = await RunState.from_json(agent, env["sdk_state"])
    item = next(x for x in state.get_interruptions() if x.call_id == env["call_id"])
    if approval["decision"] == "approved":
        state.approve(item)
    else:
        state.reject(item, rejection_message="rejected by external reviewer")
    result = await Runner.run(agent, state)
    assert not result.interruptions, "unexpected second interruption"
    env["status"] = "completed" if approval["decision"] == "approved" else "denied"
    env["final_output"] = str(result.final_output)
    (state_dir / f"{run_id}.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
    print(f"RESUME_STATUS={env['status']}")

if __name__ == "__main__": asyncio.run(main())
