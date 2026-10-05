import os
from agents import Agent, function_tool, RunConfig

@function_tool(needs_approval=True)
async def publish_report(report: str) -> str:
    """Harmless approval-gated probe; no external side effect."""
    return f"approved:{report}"

def build_agent():
    model = None
    if os.environ.get("NEXUS_TEST_MODEL") == "1":
        from szy7_test_model import RestartProbeModel
        model = RestartProbeModel()
    return Agent(name="SZY7RestartProbe", model=model,
        instructions="Call publish_report once. After tool output, answer without more tools.",
        tools=[publish_report])

def run_config():
    return RunConfig(tracing_disabled=True)
