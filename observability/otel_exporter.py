import json,time
from contextlib import contextmanager
def instrument_span(name,attributes=None,output=None):
 @contextmanager
 def span():
  started=time.time(); record={"name":name,"attributes":attributes or {},"started_at":started}
  try: yield record
  finally:
   record["ended_at"]=time.time(); record["duration_ms"]=(record["ended_at"]-started)*1000
   if output is not None: output.append(record)
 return span()
def write_jsonl(record,path):
 path.parent.mkdir(parents=True,exist_ok=True); path.open("a").write(json.dumps(record,sort_keys=True)+"\n")
