import asyncio, uuid
from agents import Runner
from szy7_common import build_agent, run_config
from szy7_store import atomic_json, run_path

async def main():
    result = await Runner.run(build_agent(), "Create the SZY-7 restart proof report.",
                              run_config=run_config())
    if len(result.interruptions) != 1:
        raise ValueError("expected exactly one approval interruption")
    state = result.to_state()
    item = result.interruptions[0]
    run_id = "RUN-" + uuid.uuid4().hex
    envelope = {"run_id": run_id, "status": "paused_approval",
        "call_id": item.call_id, "tool_name": item.tool_name,
        "sdk_state": state.to_json()}
    atomic_json(run_path(run_id), envelope)
    print(run_id)

if __name__ == "__main__":
    asyncio.run(main())
