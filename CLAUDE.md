# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI starter project for building agent teams applications. The project uses a modular structure with clear separation of concerns.

## Commands

### Development
```bash
# Run development server with hot reload
uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

# Run production server
uv run uvicorn src.app.main:app --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/api/test_health.py

# Run with coverage
uv run pytest --cov=src

# Run with verbose output
uv run pytest -v
```

### Dependency Management
```bash
# Add a new dependency
uv add <package-name>

# Add development dependency
uv add --dev <package-name>

# Remove a dependency
uv remove <package-name>

# Update dependencies
uv sync
```

## Architecture

### Directory Structure
```
src/app/
├── main.py          # Application factory and router setup
├── api/             # API route handlers
│   └── health.py    # Health check endpoint
├── core/            # Core configuration and utilities
└── models/          # Pydantic models and schemas
tests/
└── api/             # API endpoint tests
```

### Key Patterns

- **Application Factory**: `create_app()` in `src/app/main.py` creates the FastAPI instance. Use this for testing to get a fresh app instance.
- **Router Organization**: Each feature/domain should have its own router in `src/app/api/`. Routers are included via `app.include_router()` in the app factory.
- **Dependency Injection**: Use FastAPI's Depends() for dependencies (database, auth, etc.). Place shared dependencies in `src/app/core/`.
- **Testing**: Uses pytest with pytest-asyncio for async support. Fixtures for test clients go in `tests/conftest.py` if shared across tests.

### Adding New Endpoints

1. Create a new router file in `src/app/api/` (e.g., `agents.py`)
2. Define routes using `APIRouter()`
3. Import and include the router in `create_app()` with appropriate prefix and tags
4. Add corresponding tests in `tests/api/`
