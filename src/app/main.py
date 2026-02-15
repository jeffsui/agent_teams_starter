from fastapi import FastAPI
from src.app.api import health


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Agent Teams Starter",
        description="A starter template for agent teams applications",
        version="0.1.0",
    )

    # Include routers
    app.include_router(health.router, prefix="/api", tags=["health"])

    return app


app = create_app()
