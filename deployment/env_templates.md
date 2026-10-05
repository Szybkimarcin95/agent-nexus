# Agent Nexus Host Environment Templates

## .env.agent
No-API Termux mode. Secrets must come from a vault and never git.
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<secret-via-vault>
NEO4J_DATABASE=neo4j
NEO4J_READ_ONLY=true
AGENT_NEXUS_WRITE=0
ALLOWED_ROLES=GraphResearcher,IssueTriage,Supervisor
DEFAULT_ROLE=GraphResearcher

## .env.neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<secret-via-vault>
NEO4J_DATABASE=neo4j
NEO4J_READ_ONLY=true

## .env.github
GITHUB_PERSONAL_ACCESS_TOKEN=<secret-via-vault>
GITHUB_READ_ONLY=1
GITHUB_TOOLS=issue_read,pull_request_read,get_file_contents

Rules: AGENT_NEXUS_WRITE=1 only after a green gate report and Supervisor approval. Termux uses read-only plus isolated test-scope writes.