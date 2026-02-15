from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from src.app.api import health
from src.app.api.agents import architect, implement, reviewer, tester
from src.app.api import orchestration, dashboard, websocket


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

    # Dashboard endpoints
    app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])

    # WebSocket endpoint
    app.include_router(websocket.router, tags=["websocket"])

    # Mount static files (frontend)
    frontend_path = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
    if frontend_path.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

        @app.get("/", include_in_schema=False)
        async def root():
            """Serve the frontend index.html."""
            index_file = frontend_path / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            return {"message": "Frontend not built. Run 'cd frontend && npm run build'"}

        # SPA fallback - serve index.html for unmatched routes
        @app.get("/{full_path:path}", include_in_schema=False)
        async def spa_fallback(full_path: str):
            """SPA fallback for client-side routing."""
            index_file = frontend_path / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            return {"message": "Frontend not built. Run 'cd frontend && npm run build'"}

    return app


app = create_app()
