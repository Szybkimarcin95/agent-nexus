from __future__ import annotations
import json, math, re, sqlite3, time
from pathlib import Path

def _tokenize(text): return re.findall(r"[a-zA-Z0-9_]+", text.lower())
def _cosine_sim(a,b):
    common=set(a)&set(b); dot=sum(a[k]*b[k] for k in common)
    ma=math.sqrt(sum(x*x for x in a.values())); mb=math.sqrt(sum(x*x for x in b.values()))
    return 0.0 if not ma or not mb else dot/(ma*mb)

class VectorDB:
    def __init__(self, db_path):
        p=Path(db_path); p.parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(str(p)); self.db.executescript("CREATE TABLE IF NOT EXISTS chunk(id INTEGER PRIMARY KEY,source TEXT,content TEXT,tokens TEXT,vector TEXT,metadata TEXT,ts REAL,deleted INTEGER DEFAULT 0); CREATE TABLE IF NOT EXISTS v_doc_freq(term TEXT PRIMARY KEY,doc_count INTEGER);"); self.db.commit()
        self._total=self.db.execute("SELECT COUNT(*) FROM chunk WHERE deleted=0").fetchone()[0]
    def _vector(self,tokens):
        freq={}; 
        for t in set(tokens): freq[t]=tokens.count(t)
        df=dict(self.db.execute("SELECT term,doc_count FROM v_doc_freq"))
        mx=max(freq.values(),default=1); n=max(self._total,1)
        return {t:(c/mx)*(math.log((n+1)/(df.get(t,0)+1))+1) for t,c in freq.items()}
    def add_chunk(self,source,content,metadata=None,run_id=None,trace_id=None):
        toks=_tokenize(content); self._total+=1
        for t in set(toks): self.db.execute("INSERT INTO v_doc_freq(term,doc_count) VALUES(?,1) ON CONFLICT(term) DO UPDATE SET doc_count=doc_count+1",(t,))
        vec=self._vector(toks); cur=self.db.execute("INSERT INTO chunk(source,content,tokens,vector,metadata,ts) VALUES(?,?,?,?,?,?)",(source,content,json.dumps(toks),json.dumps(vec),json.dumps(metadata or {}),time.time())); self.db.commit()
        return {"chunk_id":cur.lastrowid,"source":source,"token_count":len(toks),"vector_dims":len(vec),"run_id":run_id,"trace_id":trace_id}
    def search(self,query,top_k=5,min_score=0.05):
        q=self._vector(_tokenize(query)); out=[]
        for row in self.db.execute("SELECT id,source,content,vector,metadata FROM chunk WHERE deleted=0"):
            score=_cosine_sim(q,json.loads(row[3]))
            if score>=min_score: out.append((score,{"chunk_id":row[0],"source":row[1],"content_preview":row[2][:300],"score":round(score,4),"metadata":json.loads(row[4])}))
        return [x[1] for x in sorted(out,key=lambda x:x[0],reverse=True)[:top_k]]
    def delete_chunk(self,chunk_id):
        cur=self.db.execute("UPDATE chunk SET deleted=1 WHERE id=? AND deleted=0",(chunk_id,)); self.db.commit(); return {"deleted":cur.rowcount>0,"chunk_id":chunk_id}
    def verify(self):
        total=self.db.execute("SELECT COUNT(*) FROM chunk").fetchone()[0]; active=self.db.execute("SELECT COUNT(*) FROM chunk WHERE deleted=0").fetchone()[0]
        return {"total_chunks":total,"active_chunks":active,"tombstoned_chunks":total-active,"unique_terms":self.db.execute("SELECT COUNT(*) FROM v_doc_freq").fetchone()[0],"no_external_deps":True}
    def stats(self): return {**self.verify(),"mode":"offline-pure-python","algorithm":"TF-IDF + cosine similarity","no_api_required":True}
