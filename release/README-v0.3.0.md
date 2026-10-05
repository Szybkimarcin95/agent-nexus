# Agent Nexus v0.3.0

Offline release candidate for Termux.

## Verified
- SZY-18 full lifecycle simulation: task -> pause -> approval -> resume -> shadow write -> audit.
- Production write gate remains locked by default.
- No OpenAI API key, billing, Docker, or external service is required for local tests.
- Supervisor shadow workflow replays idempotently; GraphResearcher write path is denied.

## Run
```bash
cd ~/agent-nexus
PYTHONPATH=. ~/.agent-nexus/venv-termux/bin/python -m pytest -q tests/test_szy18_sim.py
```

Deployment and observability remain pending until Docker is available.
