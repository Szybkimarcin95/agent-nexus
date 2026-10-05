from knowledge.vector_db import VectorDB,_tokenize,_cosine_sim
def test_tokenize(): assert "agent" in _tokenize("Hello Agent")
def test_cosine(): assert _cosine_sim({"a":1},{"a":1})==1
def test_search(tmp_path):
 d=VectorDB(tmp_path/"v.sqlite"); d.add_chunk("a","local AI runtime"); d.add_chunk("b","cooking pasta"); assert d.search("local runtime")[0]["source"]=="a"
def test_tombstone(tmp_path):
 d=VectorDB(tmp_path/"v.sqlite"); c=d.add_chunk("x","delete this chunk"); d.delete_chunk(c["chunk_id"]); assert not d.search("delete chunk")
def test_verify(tmp_path):
 d=VectorDB(tmp_path/"v.sqlite"); d.add_chunk("x","one"); assert d.verify()["active_chunks"]==1
def test_integration(tmp_path):
 from knowledge.vector_db_integration import VectorDBIntegration
 from knowledge.knowledge_graph import KnowledgeGraph
 kg=KnowledgeGraph(tmp_path/"kg"); kg.put_node("Project",{"name":"Alpha"},"R","T")
 i=VectorDBIntegration(tmp_path); assert i.index_kg_nodes()["indexed"]==1; assert i.search_all("Alpha")["results"]
