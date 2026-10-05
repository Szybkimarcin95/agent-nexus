KEYWORD_MAP=[("utwórz","neo4j.write"),("usuń","neo4j.write"),("schema","neo4j.schema"),("top 10","neo4j.read"),("węzłów","neo4j.read"),("wezłów","neo4j.read"),("projekty","neo4j.read"),("projekt","neo4j.read"),("issue","github.issue.read"),("pull request","github.pr.read"),("napisz","run_code"),("skrypt","run_code")]
def route(task):
 low=task.lower()
 for kw,tool in KEYWORD_MAP:
  if kw in low: return tool,{"task":task,"keyword_match":kw}
 return "run_code",{"task":task,"routing":"default"}
