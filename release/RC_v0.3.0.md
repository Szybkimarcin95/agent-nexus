# Agent Nexus v0.3.0-rc — Release Candidate

Status: feature-freeze ready. SZY-10 Controlled Writes remains LOCKED pending external gate-report sign-off.

## Included
SZY-18 full-cycle simulation; SZY-19 append-only Knowledge Graph; SZY-20 SHA-256 manifest; SZY-21 deployment runbook and environment validation; SZY-22 optional offline local LLM with FSM fallback.

## Intentional limitations
- Docker is unavailable on Termux; remote deployment waits for Linux host.
- OpenAI API and billing are off.
- No GGUF model is downloaded; local LLM uses safe FSM degraded mode.
- Production writes remain disabled.

## Verification
Local targeted suites cover SZY-18 through SZY-22. Release packaging does not unlock writes and does not push to GitHub.