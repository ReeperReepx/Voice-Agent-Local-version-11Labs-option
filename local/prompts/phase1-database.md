# Phase 1: Scaffold + Database

## Task
Set up the project structure, PostgreSQL schema, seed data for top 20 destinations, and retrieval layer.

## Requirements
- `local/` folder with full directory tree
- `services/visa_db/schema.sql` — tables: destinations, visa_questions, followups, risk_factors
- `services/visa_db/seed/` — SQL seed files for all 20 countries
- `services/visa_db/retrieval.py` — query questions by country, category, difficulty
- `requirements.txt`, `.env.example`, `docker-compose.yml` (postgres + redis)

## Completion Criteria (tests must pass)
- `pytest tests/unit/test_visa_db.py` — all pass
- Schema creates without error
- Seed data loads, retrieval returns questions for US, UK, India origin
- `<promise>COMPLETE</promise>`
