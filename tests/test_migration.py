import json,sqlite3
from migrations.json_to_sqlite import migrate
def test_json_to_sqlite_is_idempotent(tmp_path):
 src=tmp_path/"envelopes"; src.mkdir(); (src/"RUN-x.json").write_text(json.dumps({"run_id":"RUN-x","status":"paused","trace_id":"T1","approvals":[{"tool":"neo4j.write","server":"neo4j","decision":"approved","decided_at":1}]}))
 db=tmp_path/"runs.db"; assert migrate(tmp_path,db)["migrated"]==1; assert migrate(tmp_path,db)["skipped"]==1
 c=sqlite3.connect(db); assert c.execute("select count(*) from runs").fetchone()[0]==1; assert c.execute("select count(*) from approvals").fetchone()[0]==1
