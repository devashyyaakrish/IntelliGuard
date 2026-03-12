"""
WebSocket Route — Real-time threat feed for the dashboard.
"""

import asyncio
import json
import logging
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.nova.nova_forge import get_forge

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)
        logger.info("WebSocket client connected (total: %d)", len(self.active))

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)
        logger.info("WebSocket client disconnected (remaining: %d)", len(self.active))

    async def broadcast(self, message: dict):
        disconnected = []
        for ws in self.active:
            try:
                await ws.send_text(json.dumps(message, default=str))
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)


manager = ConnectionManager()


@router.websocket("/ws/feed")
async def websocket_feed(websocket: WebSocket):
    """Real-time security event feed via WebSocket."""
    await manager.connect(websocket)
    forge = get_forge()

    # Register as notification callback
    async def on_event(event_type: str, data: dict):
        await manager.broadcast({"type": event_type, "data": data, "ts": datetime.utcnow().isoformat()})

    forge.add_notification_callback(on_event)

    try:
        # Send initial state
        initial_state = forge.get_dashboard_state()
        await websocket.send_text(json.dumps({
            "type": "initial_state",
            "data": initial_state.model_dump(mode="json"),
            "ts": datetime.utcnow().isoformat(),
        }, default=str))

        # Heartbeat loop + periodic dashboard updates
        counter = 0
        while True:
            try:
                # Non-blocking: wait for client message or timeout
                await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
            except asyncio.TimeoutError:
                pass  # No client message, just send heartbeat
            except WebSocketDisconnect:
                break

            counter += 1
            # Send dashboard snapshot every 10 pings (~10s)
            if counter % 2 == 0:
                state = forge.get_dashboard_state()
                await websocket.send_text(json.dumps({
                    "type": "metrics_update",
                    "data": state.metrics.model_dump(mode="json"),
                    "ts": datetime.utcnow().isoformat(),
                }, default=str))

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
        # Remove callback
        if on_event in forge._notification_callbacks:
            forge._notification_callbacks.remove(on_event)
