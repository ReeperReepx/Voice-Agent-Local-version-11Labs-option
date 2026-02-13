# Phase 8: Docker + Deployment

## Task
Containerize all services.

## Requirements
- `infra/docker/` — Dockerfiles for ASR, LLM, TTS, orchestrator
- `docker-compose.yml` — full stack (postgres, redis, all services)
- `scripts/load_models.sh` — download all model weights
- `scripts/seed_db.sh` — init DB + seed
- `scripts/smoke_test.sh` — verify all services respond

## Completion Criteria
- `docker compose up` starts all services
- `scripts/smoke_test.sh` passes
- `<promise>COMPLETE</promise>`
