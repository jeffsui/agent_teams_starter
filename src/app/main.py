from fastapi import FastAPI
from src.app.api import health
from src.app.api.agents import architect, implement, reviewer, tester
from src.app.api import orchestration


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Agent Teams Starter",
        description="A starter template for agent teams applications with 4 specialized agents",
        version="0.1.0",
    )

    # Include routers
    app.include_router(health.router, prefix="/api", tags=["health"])

    # Individual agent endpoints
    app.include_router(architect.router, prefix="/api/agents", tags=["agents"])
    app.include_router(implement.router, prefix="/api/agents", tags=["agents"])
    app.include_router(reviewer.router, prefix="/api/agents", tags=["agents"])
    app.include_router(tester.router, prefix="/api/agents", tags=["agents"])

    # Orchestration endpoints
    app.include_router(orchestration.router, prefix="/api", tags=["orchestration"])

    return app


app = create_app()
