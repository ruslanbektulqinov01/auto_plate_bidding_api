from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from app.database import get_session
from app.core.security import get_current_user_ws
from app.controllers.bid_controller import BidController

router = APIRouter()


# Store active connections for different auction plates
class ConnectionManager:
    def __init__(self):
        # Map of plate_id -> list of connected websockets
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, plate_id: int):
        await websocket.accept()
        if plate_id not in self.active_connections:
            self.active_connections[plate_id] = []
        self.active_connections[plate_id].append(websocket)

    def disconnect(self, websocket: WebSocket, plate_id: int):
        if plate_id in self.active_connections:
            if websocket in self.active_connections[plate_id]:
                self.active_connections[plate_id].remove(websocket)
            if not self.active_connections[plate_id]:
                del self.active_connections[plate_id]

    async def broadcast_to_plate(self, plate_id: int, message: dict):
        if plate_id in self.active_connections:
            for connection in self.active_connections[plate_id]:
                await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/plates/{plate_id}/bids")
async def websocket_endpoint(
    websocket: WebSocket,
    plate_id: int,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_ws),
):
    await manager.connect(websocket, plate_id)
    try:
        # Send current highest bid when connecting
        bid_controller = BidController(db)
        highest_bid = await bid_controller.get_highest_bid_for_plate(plate_id)
        if highest_bid:
            await websocket.send_json(
                {
                    "type": "highest_bid",
                    "data": {
                        "amount": highest_bid.amount,
                        "user_id": highest_bid.user_id,
                        "timestamp": highest_bid.created_at.isoformat(),
                    },
                }
            )

        while True:
            # Wait for any messages from the client
            data = await websocket.receive_text()
            # You can process client messages here if needed

            from app.tasks.notification_tasks import send_bid_notification
            send_bid_notification.delay(plate_id, user.id, highest_bid.amount)
    except WebSocketDisconnect:
        manager.disconnect(websocket, plate_id)
# send_push_notification(user_id, plate_id, highest_bid.amount)
async def send_push_notification(user_id: int, plate_id: int, amount: float):
