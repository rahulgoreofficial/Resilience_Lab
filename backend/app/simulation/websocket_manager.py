"""
WebSocket Manager for Live Simulation Progress Updates.
Manages active WebSocket connections per simulation_id and safely broadcasts execution events.
Handles client disconnects gracefully without disrupting simulations.
"""

from typing import Dict, List, Any
import json
import logging
from fastapi import WebSocket

logger = logging.getLogger("simulation_ws")


class ConnectionManager:
    """Manages active WebSocket subscribers for simulation progress channels."""

    def __init__(self):
        # simulation_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, simulation_id: str):
        """Accepts and registers a new WebSocket subscriber."""
        await websocket.accept()
        if simulation_id not in self.active_connections:
            self.active_connections[simulation_id] = []
        self.active_connections[simulation_id].append(websocket)
        logger.info(f"WebSocket client connected for simulation {simulation_id}")

    def disconnect(self, websocket: WebSocket, simulation_id: str):
        """Unregisters a disconnected WebSocket subscriber."""
        if simulation_id in self.active_connections:
            if websocket in self.active_connections[simulation_id]:
                self.active_connections[simulation_id].remove(websocket)
            if not self.active_connections[simulation_id]:
                del self.active_connections[simulation_id]
        logger.info(f"WebSocket client disconnected for simulation {simulation_id}")

    async def broadcast_event(self, simulation_id: str, event_data: Dict[str, Any]):
        """
        Sends an execution event to all clients subscribed to simulation_id.
        Tolerates dead connections without crashing.
        """
        if simulation_id not in self.active_connections:
            return

        dead_connections: List[WebSocket] = []
        message_str = json.dumps(event_data)

        for connection in self.active_connections[simulation_id]:
            try:
                await connection.send_text(message_str)
            except Exception as exc:
                logger.warning(f"Failed to send to WebSocket, marking for removal: {exc}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead, simulation_id)


# Global singleton connection manager
ws_manager = ConnectionManager()

