import asyncio, json, sys, fcntl
from agents import RunState, Runner
from szy7_common import build_agent, run_config
from szy7_store import run_path, atomic_json, validate_decision

async def resume(run_id):
    path = run_path(run_id)
    with path.with_suffix(".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        env = json.loads(path.read_text())
        if env["status"] in {"completed", "denied"}:
            print("RESUME_STATUS=" + env["status"])
            return
        if env["status"] == "resuming":
            raise ValueError("previous resume outcome uncertain; reconcile before retry")
        approval_path = path.with_suffix(".approval.json")
        if not approval_path.exists():
            print("RESUME_STATUS=pending")
            return
        approval = json.loads(approval_path.read_text())
        validate_decision(env, approval)
        agent = build_agent()
        state = await RunState.from_json(agent, env["sdk_state"])
        items = [x for x in state.get_interruptions() if x.call_id == env["call_id"]]
        if len(items) != 1 or items[0].tool_name != env["tool_name"]:
            raise ValueError("interruption identity mismatch")
        if approval["decision"] == "approved":
            state.approve(items[0])
        else:
            state.reject(items[0], rejection_message="rejected by external reviewer")
        env["status"] = "resuming"
        atomic_json(path, env)
        result = await Runner.run(agent, state, run_config=run_config())
        if result.interruptions:
            raise ValueError("unexpected second interruption")
        env["status"] = "completed" if approval["decision"] == "approved" else "denied"
        env["final_output"] = str(result.final_output)
        atomic_json(path, env)
        print("RESUME_STATUS=" + env["status"])

async def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: szy7_resume.py RUN-ID")
    await resume(sys.argv[1])

if __name__ == "__main__":
    asyncio.run(main())
