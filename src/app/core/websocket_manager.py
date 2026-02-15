"""WebSocket connection manager for real-time updates."""
import json
from typing import Set
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect


class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""

    def __init__(self) -> None:
        """Initialize the connection manager."""
        self._active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection.

        Args:
            websocket: The WebSocket connection to accept.
        """
        await websocket.accept()
        self._active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection.

        Args:
            websocket: The WebSocket connection to remove.
        """
        self._active_connections.discard(websocket)

    async def broadcast(self, message: dict) -> None:
        """Broadcast a message to all connected clients.

        Args:
            message: The message dictionary to broadcast.
        """
        if not self._active_connections:
            return

        message_json = json.dumps(message)
        disconnected = set()

        for connection in self._active_connections:
            try:
                await connection.send_text(message_json)
            except Exception:
                disconnected.add(connection)

        # Remove disconnected clients
        self._active_connections -= disconnected

    async def broadcast_workflow_update(
        self,
        workflow_id: str,
        status: str,
        current_step: str | None = None,
        data: dict | None = None,
    ) -> None:
        """Broadcast a workflow status update to all connected clients.

        Args:
            workflow_id: The workflow ID.
            status: The workflow status.
            current_step: The current step being executed.
            data: Additional data to include.
        """
        message = {
            "type": "workflow_update",
            "workflow_id": workflow_id,
            "status": status,
            "current_step": current_step,
            "data": data or {},
        }
        await self.broadcast(message)

    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        """Send a message to a specific WebSocket connection.

        Args:
            message: The message dictionary to send.
            websocket: The specific WebSocket connection.
        """
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            self.disconnect(websocket)


# Global connection manager instance
_manager: ConnectionManager | None = None


def get_websocket_manager() -> ConnectionManager:
    """Get the global connection manager instance.

    Returns:
        The global ConnectionManager instance.
    """
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager
