from __future__ import annotations
import json
from pathlib import Path
from knowledge.vector_db import VectorDB
from knowledge.knowledge_graph import KnowledgeGraph
from eventlog import EventLog


class VectorDBIntegration:
    def __init__(self, base: Path):
        self.base = Path(base)
        self.vdb = VectorDB(self.base / 'vectors.sqlite')
        self.kg = KnowledgeGraph(self.base / 'kg')
        self.el = EventLog(self.base / 'eventlog.jsonl')

    def index_kg_nodes(self, run_id=None, trace_id=None):
        nodes = self.kg.find_nodes(include_deleted=False)
        for node in nodes:
            content = json.dumps({'label': node['label'], 'props': node['props']}, ensure_ascii=False)
            self.vdb.add_chunk(f"kg_node:{node['node_id']}", content, {'node_id': node['node_id'], 'label': node['label']}, run_id, trace_id)
        return {'indexed': len(nodes), 'source': 'knowledge_graph'}

    def index_eventlog(self, eventlog_path=None, run_id=None, trace_id=None):
        path = Path(eventlog_path or self.base / 'eventlog.jsonl')
        if not path.exists():
            return {'indexed': 0, 'source': 'eventlog', 'reason': 'file not found'}
        count = 0
        for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
            try: entry = json.loads(line)
            except json.JSONDecodeError: continue
            self.vdb.add_chunk('eventlog', json.dumps(entry, ensure_ascii=False), {'event': entry.get('event'), 'run_id': entry.get('run_id'), 'trace_id': entry.get('trace_id')}, run_id, trace_id)
            count += 1
        return {'indexed': count, 'source': 'eventlog'}

    def search_all(self, query: str, top_k: int = 5):
        results = self.vdb.search(query, top_k=top_k)
        return {'query': query, 'total_results': len(results), 'results': results, 'backend': 'vector_db', 'indexed_sources': ['kg_nodes', 'eventlog']}
