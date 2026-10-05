from agents import Agent, function_tool

@function_tool(needs_approval=True)
async def publish_report(report: str) -> str:
    """Harmless approval-gated probe; no external side effect."""
    return f"approved:{report}"


def build_agent() -> Agent:
    return Agent(
        name="SZY7RestartProbe",
        instructions=(
            "For every request call publish_report exactly once with a short report. "
            "Do not answer before using the tool."
        ),
        tools=[publish_report],
    )
