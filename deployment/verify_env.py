from __future__ import annotations
import os, json

REQUIRED_JOBS = {
 "NEO4J_URI": (True, "bolt://localhost:7687"),
 "NEO4J_USERNAME": (True, "neo4j"),
 "NEO4J_PASSWORD": (True, None),
 "NEO4J_DATABASE": (True, "neo4j"),
 "NEO4J_READ_ONLY": (True, "true"),
 "AGENT_NEXUS_WRITE": (True, "0"),
 "ALLOWED_ROLES": (False, "GraphResearcher,IssueTriage,Supervisor"),
 "DEFAULT_ROLE": (False, "GraphResearcher"),
 "GITHUB_READ_ONLY": (False, "1"),
 "GITHUB_TOOLS": (False, "issue_read,pull_request_read,get_file_contents"),
 "GITHUB_PERSONAL_ACCESS_TOKEN": (False, None),
}

def verify_env(verbose=True):
    out={"ok":True,"missing_required":[],"warnings":[],"policy_state":{}}
    for var,(required,default) in REQUIRED_JOBS.items():
        val=os.environ.get(var)
        if val is None:
            if required and default is None: out["missing_required"].append(var); out["ok"]=False
            elif default is not None: out["policy_state"][var]={"value":default,"source":"default"}
        else: out["policy_state"][var]={"value":val,"source":"env"}
    ro=out["policy_state"].get("NEO4J_READ_ONLY",{"value":"true"})["value"]
    if ro.lower()!="true": out["warnings"].append("NEO4J_READ_ONLY != true"); out["ok"]=False
    write=out["policy_state"].get("AGENT_NEXUS_WRITE",{"value":"0"})["value"]
    if write!="0": out["warnings"].append("AGENT_NEXUS_WRITE != 0 — requires gate-report"); out["ok"]=False
    gh=out["policy_state"].get("GITHUB_READ_ONLY",{"value":"1"})["value"]
    if gh!="1": out["warnings"].append("GITHUB_READ_ONLY != 1"); out["ok"]=False
    return out

if __name__=="__main__": print(json.dumps(verify_env(),indent=2,ensure_ascii=False))
