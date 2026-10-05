from knowledge.append_only_log import AppendOnlyLog
from knowledge.knowledge_graph import KnowledgeGraph

def test_log_chain_and_tamper(tmp_path):
    p=tmp_path/"log.jsonl"; log=AppendOnlyLog(p)
    log.append("insert","node:1",{"x":1},"R","T")
    log.append("delete_tombstone","node:1",{},"R","T")
    assert log.verify_chain()["ok"]
    p.write_text(p.read_text().replace('"x": 1','"x": 9'))
    assert AppendOnlyLog(p).verify_chain()["ok"] is False

def test_graph_tombstone_and_edges(tmp_path):
    kg=KnowledgeGraph(tmp_path)
    a=kg.put_node("Person",{"name":"Anna"},"R","T")
    b=kg.put_node("Project",{"name":"Alpha"},"R","T")
    kg.put_edge(a["node_id"],b["node_id"],"WORKS_ON",{},"R","T")
    assert kg.related_to(a["node_id"])
    kg.delete_node(b["node_id"],"R","T")
    assert kg.get_node(b["node_id"])["deleted"]
    assert kg.verify()["chain"]["ok"]
    assert kg.verify()["tombstoned"]==1
