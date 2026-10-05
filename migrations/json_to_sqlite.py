import json,sqlite3
from pathlib import Path
SCHEMA="""CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY,agent_name TEXT NOT NULL,prompt TEXT,status TEXT NOT NULL,trace_id TEXT NOT NULL,pending_action TEXT,approvals TEXT,sdk_state_blob TEXT,updated_at REAL DEFAULT(unixepoch()));
CREATE TABLE IF NOT EXISTS approvals(approval_id INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT NOT NULL,tool TEXT NOT NULL,server TEXT NOT NULL,decision TEXT NOT NULL,reasoning TEXT DEFAULT '',decided_by TEXT DEFAULT 'human:default',decided_at REAL NOT NULL);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);"""
def migrate(base_dir,db_path):
 db=sqlite3.connect(db_path); db.executescript(SCHEMA); src=Path(base_dir)/"envelopes"; migrated=skipped=0
 if not src.exists(): db.commit(); db.close(); return {"migrated":0,"skipped":0,"reason":"no envelopes dir"}
 for f in sorted(src.glob("*.json")):
  raw=json.loads(f.read_text()); rid=raw.get("run_id")
  if not rid or db.execute("SELECT 1 FROM runs WHERE run_id=?",(rid,)).fetchone(): skipped+=1; continue
  db.execute("INSERT INTO runs(run_id,agent_name,prompt,status,trace_id,pending_action,approvals,sdk_state_blob) VALUES(?,?,?,?,?,?,?,?)",(rid,raw.get("agent_name",""),raw.get("prompt",""),raw.get("status",""),raw.get("trace_id",""),json.dumps(raw.get("pending_action")) if raw.get("pending_action") else None,json.dumps(raw.get("approvals",[])),raw.get("sdk_state_blob")))
  for a in raw.get("approvals",[]): db.execute("INSERT INTO approvals(run_id,tool,server,decision,reasoning,decided_by,decided_at) VALUES(?,?,?,?,?,?,?)",(rid,a.get("tool",""),a.get("server",""),a.get("decision",""),a.get("reasoning",""),a.get("decided_by","human:default"),a.get("decided_at",0.0)))
  migrated+=1
 db.commit(); db.close(); return {"migrated":migrated,"skipped":skipped}
