"""
WebSocket Endpoint: Live Simulation Progress Streaming.
Subscribes frontend clients to simulation execution events and delivers historical replay.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.repositories.simulation_repository import SimulationRepository
from app.simulation.websocket_manager import ws_manager
from app.core.logging import logger

ws_router = APIRouter()


@ws_router.websocket("/ws/simulations/{simulation_id}")
async def websocket_simulation_endpoint(websocket: WebSocket, simulation_id: str):
    """
    WebSocket endpoint allowing live subscription to simulation progress.
    On connection, replays any existing historical events from persistent storage.
    """
    await ws_manager.connect(websocket, simulation_id)
    try:
        # Replay already recorded events if any
        try:
            from app.database.session import get_db_context
            with get_db_context() as db:
                past_events = SimulationRepository.get_events(db, simulation_id)
                for ev in past_events:
                    await websocket.send_json(ev.to_dict())
        except Exception as exc:
            logger.debug(f"Event replay skipped: {exc}")

        while True:
            # Keep socket alive and respond to client ping
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, simulation_id)
    except Exception as exc:
        logger.warning(f"WebSocket client error: {exc}")
        ws_manager.disconnect(websocket, simulation_id)

