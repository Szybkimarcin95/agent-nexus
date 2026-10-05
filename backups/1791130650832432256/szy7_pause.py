import asyncio, json, time
from pathlib import Path
from agents import Runner
from szy7_common import build_agent

STATE_DIR = Path(__file__).parent / "state"
STATE_DIR.mkdir(exist_ok=True)

async def main():
    agent = build_agent()
    result = await Runner.run(agent, "Create the SZY-7 restart proof report.")
    assert result.interruptions, "expected approval interruption"
    state = result.to_state()
    item = result.interruptions[0]
    run_id = f"RUN-{int(time.time())}"
    envelope = {
        "run_id": run_id,
        "status": "paused_approval",
        "call_id": item.call_id,
        "tool_name": item.tool_name or item.name,
        "sdk_state": state.to_json(),
    }
    path = STATE_DIR / f"{run_id}.json"
    path.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
    print(run_id)

if __name__ == "__main__": asyncio.run(main())
