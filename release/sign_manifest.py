from __future__ import annotations
import hashlib, json, time
from pathlib import Path

def _sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(8192),b""): h.update(chunk)
    return h.hexdigest()

def _hash_dir(base):
    base=Path(base)
    return {p.relative_to(base).as_posix():_sha256(p) for p in sorted(base.rglob("*")) if p.is_file() and p.name!="manifest.json"}

def build_manifest(base, role="Preserver"):
    files=_hash_dir(base)
    top=hashlib.sha256(json.dumps(files,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    sig=hashlib.sha256(json.dumps({"hash":top,"role":role},sort_keys=True).encode()).hexdigest()
    return {"version":"v0.3.0","role":role,"timestamp":time.time(),"total_files":len(files),"files":files,"top_hash":top,"signature":sig}

def write_manifest(base,out_path,role="Preserver"):
    out_path=Path(out_path); out_path.parent.mkdir(parents=True,exist_ok=True)
    out_path.write_text(json.dumps(build_manifest(base,role),indent=2,ensure_ascii=False))
    return out_path

def verify_manifest(base,manifest_path):
    p=Path(manifest_path)
    if not p.exists(): return {"ok":False,"reason":"manifest not found"}
    old=json.loads(p.read_text()); new=build_manifest(base,old.get("role","Preserver"))
    same=new["top_hash"]==old.get("top_hash")
    return {"ok":same and new["total_files"]==old.get("total_files"),"top_hash_matches":same,
            "files_match":new["total_files"]==old.get("total_files"),
            "expected_files":old.get("total_files"),"actual_files":new["total_files"]}

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--base",required=True); ap.add_argument("--out")
    a=ap.parse_args(); out=Path(a.out or Path(a.base)/"manifest.json"); write_manifest(a.base,out); print(out)
