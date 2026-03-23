# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Start services (PostgreSQL + app with auto-migration)
docker compose up

# Run full test suite (requires test DB and venv)
source .venv/bin/activate
DATABASE_URL=postgresql://taskmanager:taskmanager@localhost:5433/taskmanager \
TEST_DATABASE_URL=postgresql://taskmanager:taskmanager@localhost:5433/taskmanager_test \
pytest tests/ -v

# Run a single test
pytest tests/test_create_task.py::test_create_task_minimal -v

# Generate a new migration after model changes
DATABASE_URL=postgresql://taskmanager:taskmanager@localhost:5433/taskmanager \
alembic revision --autogenerate -m "description"

# Apply migrations
DATABASE_URL=postgresql://taskmanager:taskmanager@localhost:5433/taskmanager \
alembic upgrade head
```

Database credentials: `taskmanager`/`taskmanager`, DB name `taskmanager`, Docker-exposed on port **5433** (not 5432). Test DB: `taskmanager_test` on same server.

## Architecture

FastAPI REST API with SQLAlchemy ORM and PostgreSQL. Single domain entity: **Task**.

- `app/main.py` — FastAPI app, includes the tasks router
- `app/models.py` — `Task` SQLAlchemy model with `TaskStatus` and `TaskPriority` enums
- `app/schemas.py` — Pydantic v2 request/response schemas with `from_attributes` for ORM mapping
- `app/routers/tasks.py` — all 8 endpoints in a single router (prefix `/tasks`)
- `app/database.py` — engine, session factory, `get_db()` dependency
- `app/config.py` — reads `DATABASE_URL` from environment via pydantic-settings

**Route ordering matters:** `/tasks/search` and `/tasks/stats` are defined before `/tasks/{task_id}` to prevent FastAPI from parsing literal paths as UUID parameters.

**Status transitions** follow a strict state machine (`VALID_TRANSITIONS` dict): `todo → in_progress → done`. No skipping, no backwards. Enforced in `PATCH /tasks/{task_id}/status`.

**Partial updates** use `model_dump(exclude_unset=True)` so only client-supplied fields are changed.

## Testing

Tests use a real PostgreSQL database (not SQLite) because the app uses PG-specific features (UUID type, ILIKE, ENUM). Each test runs in a transaction that rolls back automatically (`conftest.py` overrides `get_db` with a transactional session). The `db_session` fixture is available for direct ORM access when bypassing API validation (e.g., inserting overdue tasks with past due dates).
