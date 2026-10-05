from __future__ import annotations
import json, sqlite3, time
from pathlib import Path
from .append_only_log import AppendOnlyLog

SCHEMA = """CREATE TABLE IF NOT EXISTS k_node(
 id INTEGER PRIMARY KEY AUTOINCREMENT,label TEXT NOT NULL,props TEXT DEFAULT '{}',
 ts_first REAL,ts_last REAL,deleted INTEGER DEFAULT 0,version INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS k_edge(
 id INTEGER PRIMARY KEY AUTOINCREMENT,src INTEGER NOT NULL,dst INTEGER NOT NULL,rel TEXT NOT NULL,
 props TEXT DEFAULT '{}',ts_first REAL,ts_last REAL,deleted INTEGER DEFAULT 0,version INTEGER DEFAULT 0);
CREATE INDEX IF NOT EXISTS idx_kn_label ON k_node(label);
CREATE INDEX IF NOT EXISTS idx_ke_src ON k_edge(src);
CREATE INDEX IF NOT EXISTS idx_ke_dst ON k_edge(dst);"""

class KnowledgeGraph:
    def __init__(self, base):
        base = Path(base); base.mkdir(parents=True, exist_ok=True)
        self.log = AppendOnlyLog(base/"kg_log.jsonl")
        self.db = sqlite3.connect(str(base/"kg_index.sqlite"))
        self.db.executescript(SCHEMA); self.db.commit()

    def put_node(self, label, props, run_id, trace_id, role=""):
        blob=json.dumps(props, ensure_ascii=False, sort_keys=True)
        row=self.db.execute("SELECT id FROM k_node WHERE label=? AND props=? AND deleted=0",(label,blob)).fetchone()
        now=time.time()
        if row:
            nid=row[0]; action="update"
            self.db.execute("UPDATE k_node SET ts_last=?,version=version+1 WHERE id=?",(now,nid))
        else:
            action="insert"
            nid=self.db.execute("INSERT INTO k_node(label,props,ts_first,ts_last,version) VALUES(?,?,?,?,1)",(label,blob,now,now)).lastrowid
        self.db.commit()
        self.log.append(action,f"node:{nid}",{"label":label,"props":props},run_id,trace_id,role)
        return self.get_node(nid)

    def delete_node(self,node_id,run_id,trace_id,role=""):
        cur=self.db.execute("UPDATE k_node SET deleted=1,ts_last=?,version=version+1 WHERE id=? AND deleted=0",(time.time(),node_id))
        self.db.commit()
        if cur.rowcount==0: raise ValueError(f"node {node_id} not found or already deleted")
        self.log.append("delete_tombstone",f"node:{node_id}",{},run_id,trace_id,role)
        return {"deleted":True,"node_id":node_id}

    def put_edge(self,src,dst,rel,props,run_id,trace_id,role=""):
        blob=json.dumps(props,ensure_ascii=False,sort_keys=True); now=time.time()
        row=self.db.execute("SELECT id FROM k_edge WHERE src=? AND dst=? AND rel=? AND deleted=0",(src,dst,rel)).fetchone()
        if row:
            eid=row[0]; action="update"; self.db.execute("UPDATE k_edge SET props=?,ts_last=?,version=version+1 WHERE id=?",(blob,now,eid))
        else:
            action="insert"; eid=self.db.execute("INSERT INTO k_edge(src,dst,rel,props,ts_first,ts_last,version) VALUES(?,?,?,?,?,?,1)",(src,dst,rel,blob,now,now)).lastrowid
        self.db.commit(); self.log.append(action,f"edge:{eid}",{"src":src,"dst":dst,"rel":rel,"props":props},run_id,trace_id,role)
        return {"edge_id":eid,"action":action}

    def get_node(self,nid):
        r=self.db.execute("SELECT id,label,props,ts_first,ts_last,deleted FROM k_node WHERE id=?",(nid,)).fetchone()
        return None if not r else {"node_id":r[0],"label":r[1],"props":json.loads(r[2]),"ts_first":r[3],"ts_last":r[4],"deleted":bool(r[5])}

    def find_nodes(self,label=None,limit=100,include_deleted=False):
        q="SELECT id,label,props,ts_first,ts_last,deleted FROM k_node"; args=[]; cond=[]
        if label: cond.append("label=?"); args.append(label)
        if not include_deleted: cond.append("deleted=0")
        if cond:q+=" WHERE "+" AND ".join(cond)
        q+=" LIMIT ?"; args.append(limit)
        return [{"node_id":r[0],"label":r[1],"props":json.loads(r[2]),"ts_first":r[3],"ts_last":r[4],"deleted":bool(r[5])} for r in self.db.execute(q,args)]

    def top_degree(self,limit=10):
        rows=self.db.execute("SELECT n.id,n.label,n.props,(SELECT COUNT(*) FROM k_edge e WHERE (e.src=n.id OR e.dst=n.id) AND e.deleted=0) FROM k_node n WHERE n.deleted=0 ORDER BY 4 DESC LIMIT ?",(limit,)).fetchall()
        return [{"node_id":r[0],"label":r[1],"props":json.loads(r[2]),"degree":r[3]} for r in rows]

    def related_to(self,node_id,hops=1):
        seen={node_id}; frontier=[node_id]; out=[]
        for _ in range(hops):
            nxt=[]
            for n in frontier:
                for (x,) in self.db.execute("SELECT CASE WHEN src=? THEN dst ELSE src END FROM k_edge WHERE (src=? OR dst=?) AND deleted=0",(n,n,n)):
                    if x not in seen: seen.add(x); nxt.append(x)
            frontier=nxt; out.extend(self.get_node(x) for x in nxt)
            if not frontier: break
        return [x for x in out if x and not x["deleted"]]

    def verify(self):
        return {"chain":self.log.verify_chain(),"active_nodes":self.db.execute("SELECT COUNT(*) FROM k_node WHERE deleted=0").fetchone()[0],"tombstoned":self.db.execute("SELECT COUNT(*) FROM k_node WHERE deleted=1").fetchone()[0]}
