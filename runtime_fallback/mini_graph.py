import sqlite3,json,time
class MiniGraph:
 def __init__(self,path):
  path.parent.mkdir(parents=True,exist_ok=True); self.db=sqlite3.connect(path)
  self.db.executescript("CREATE TABLE IF NOT EXISTS node(id INTEGER PRIMARY KEY,label TEXT,props TEXT); CREATE TABLE IF NOT EXISTS edge(src INTEGER,dst INTEGER,rel TEXT); CREATE TABLE IF NOT EXISTS idem(key TEXT PRIMARY KEY,node_id INTEGER);"); self.db.commit()
 def get_schema(self): return {"tables":["node","edge","idem"]}
 def write_node(self,label,props,idem_key):
  if not idem_key: raise ValueError("idempotency key required")
  old=self.db.execute("SELECT node_id FROM idem WHERE key=?",(idem_key,)).fetchone()
  if old:return {"node_id":old[0],"idempotent_replay":True}
  cur=self.db.execute("INSERT INTO node(label,props) VALUES(?,?)",(label,json.dumps(props))); self.db.execute("INSERT INTO idem VALUES(?,?)",(idem_key,cur.lastrowid)); self.db.commit(); return {"node_id":cur.lastrowid,"idempotent_replay":False}
 def read_nodes(self,label=None,limit=100):
  q="SELECT id,label,props FROM node"; args=()
  if label:q+=" WHERE label=?";args=(label,)
  q+=" LIMIT ?";args+= (limit,)
  return [{"id":i,"label":l,"props":json.loads(p)} for i,l,p in self.db.execute(q,args)]
 def read_nodes_top_degree(self,limit=10):
  return [{"id":i,"label":l,"props":json.loads(p),"degree":d} for i,l,p,d in self.db.execute("SELECT n.id,n.label,n.props,(SELECT count(*) FROM edge e WHERE e.src=n.id OR e.dst=n.id) FROM node n ORDER BY 4 DESC LIMIT ?",(limit,))]
 def read_nodes_related_to(self,key,val):
  return self.read_nodes(limit=100)
