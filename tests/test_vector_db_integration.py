from knowledge.vector_db_integration import VectorDBIntegration
from knowledge.knowledge_graph import KnowledgeGraph
from eventlog import EventLog


def test_index_kg_nodes(tmp_path):
    kg = KnowledgeGraph(tmp_path / 'kg')
    kg.put_node('Project', {'name': 'Alpha'}, 'R1', 'T1')
    assert VectorDBIntegration(tmp_path).index_kg_nodes()['indexed'] == 1


def test_index_eventlog(tmp_path):
    EventLog(tmp_path / 'eventlog.jsonl').append({'run_id': 'R1', 'trace_id': 'T1', 'event': 'plan', 'payload': {'tool': 'neo4j.read'}})
    assert VectorDBIntegration(tmp_path).index_eventlog()['indexed'] == 1


def test_search_across_indexed_sources(tmp_path):
    kg = KnowledgeGraph(tmp_path / 'kg')
    kg.put_node('Project', {'name': 'Alpha'}, 'R1', 'T1')
    integration = VectorDBIntegration(tmp_path)
    integration.index_kg_nodes()
    out = integration.search_all('Alpha project')
    assert out['backend'] == 'vector_db' and out['total_results'] >= 1
