from typing import Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # key = user_id, value = WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, user_id: str, message: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json({"message": message})

manager = ConnectionManager()
