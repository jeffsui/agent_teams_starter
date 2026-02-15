"""WebSocket API endpoints for real-time updates."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.app.core.websocket_manager import get_websocket_manager


router = APIRouter()


@router.websocket("/ws/workflows")
async def workflow_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time workflow updates.

    Clients connecting to this endpoint will receive real-time updates
    for all workflow status changes.

    Message format:
    {
        "type": "workflow_update",
        "workflow_id": "uuid",
        "status": "pending|running|completed|failed",
        "current_step": "architect|implement|reviewer|tester|null",
        "data": {}
    }
    """
    ws_manager = get_websocket_manager()

    await ws_manager.connect(websocket)

    try:
        # Send welcome message
        await ws_manager.send_personal_message(
            {"type": "connected", "message": "Connected to workflow updates"},
            websocket,
        )

        # Keep connection alive and listen for client messages
        while True:
            # Receive any messages from client (for ping/pong, etc.)
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        pass
    finally:
        ws_manager.disconnect(websocket)
