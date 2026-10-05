from dataclasses import dataclass
from enum import Enum
CANONICAL_TOOLS={"neo4j.schema":"get-schema","neo4j.read":"read-cypher","neo4j.write":"write-cypher","github.issue.read":"issue_read","github.pr.read":"pull_request_read","github.issue.write":"issue_write","github.pr.create":"create_pull_request","github.repo.read":"get_file_contents"}
@dataclass(frozen=True)
class ToolCapability:
    logical_name:str; canonical_name:str; server:str; read_only:bool; requires_approval:bool
CAPABILITIES={n:ToolCapability(n,c,"neo4j" if n.startswith("neo4j.") else "github",(".write" not in n and ".create" not in n),(".write" in n or ".create" in n)) for n,c in CANONICAL_TOOLS.items()}
class Decision(str,Enum): ALLOW="allow"; DISALLOW="disallow"; NEEDS_APPROVAL="needs_approval"
ROLE_CAPABILITY={"GraphResearcher":{"neo4j.schema","neo4j.read","github.issue.read","github.pr.read","github.repo.read"},"IssueTriage":{"github.issue.read","github.pr.read","github.repo.read"},"Supervisor":set(CAPABILITIES)}
APPROVAL_REQUIRED={"neo4j.write","github.issue.write","github.pr.create"}
def decide(role,logical_tool):
    if role not in ROLE_CAPABILITY or logical_tool not in CAPABILITIES or logical_tool not in ROLE_CAPABILITY[role]: return Decision.DISALLOW
    return Decision.NEEDS_APPROVAL if logical_tool in APPROVAL_REQUIRED else Decision.ALLOW
def filter_tools_for_role(role,all_canonical):
    allowed={CAPABILITIES[n].canonical_name for n in ROLE_CAPABILITY.get(role,set())}
    return [t for t in all_canonical if t in allowed]
