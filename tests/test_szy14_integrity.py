import sqlite3,json
from eventlog import EventLog
from runstate import RunStore
from observability.otel_exporter import instrument_span
from migrations.json_to_sqlite import migrate
def test_event_log_survives_sqlite_migration(tmp_path):
 env=tmp_path/"envelopes"; env.mkdir(); e={"run_id":"RUN-chain","status":"paused","trace_id":"trace-1","approvals":[]}
 RunStore(env).save(e); result=migrate(tmp_path,tmp_path/"db.sqlite"); assert result["migrated"]==1
 c=sqlite3.connect(tmp_path/"db.sqlite"); assert c.execute("select count(*) from runs where run_id='RUN-chain'").fetchone()[0]==1
def test_otel_span_wraps_runstate():
 out=[]
 with instrument_span("test-span",{"run":"x"},out):
  assert True
 assert out[0]["name"]=="test-span" and out[0]["duration_ms"]>=0
def test_eventlog_does_not_change_span_identity(tmp_path):
 log=EventLog(tmp_path/"events.jsonl"); row=log.append({"run_id":"RUN-x","trace_id":"T1","event":"read"})
 assert row["run_id"]=="RUN-x" and log.read()[0]["trace_id"]=="T1"
