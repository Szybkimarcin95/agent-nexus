from pathlib import Path
from knowledge.vector_db import VectorDB


def main():
    db = VectorDB(Path.home() / 'agent-nexus' / 'vector_db' / 'vectors.sqlite')
    db.add_chunk('runtime', 'Termux native runtime uses an FSM router and SQLite knowledge graph.')
    db.add_chunk('security', 'SZY-10 controlled writes remain locked pending an all-green gate report.')
    print(db.stats())
    print(db.search('controlled writes status', top_k=3))


if __name__ == '__main__':
    main()
