import inspect
from agents.mcp import MCPServerStdio, create_static_tool_filter


def test_stdio_supports_required_controls():
    sig = str(inspect.signature(MCPServerStdio))
    for name in (
        'tool_filter', 'require_approval', 'max_retry_attempts',
        'cache_tools_list', 'tool_input_guardrails', 'tool_output_guardrails'
    ):
        assert name in sig


def test_static_filter_builder_exists():
    f = create_static_tool_filter(
        allowed_tool_names=['get-schema', 'read-cypher']
    )
    assert f is not None


def test_read_only_tool_sets_have_no_writes():
    neo4j = {'get-schema', 'read-cypher'}
    github = {'issue_read', 'pull_request_read', 'get_file_contents'}
    forbidden = {'write-cypher', 'create_pull_request', 'issue_write'}
    assert neo4j.isdisjoint(forbidden)
    assert github.isdisjoint(forbidden)
