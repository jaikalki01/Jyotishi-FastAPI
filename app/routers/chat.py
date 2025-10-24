from typing import Dict, Set
from fastapi import WebSocket
import json
from datetime import datetime
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import User, ChatMessage, india_tz
from app.schemas.chat import ChatHistoryResponse, LastMessageOut, ChatMessageOut, ChatMessageCreate
from app.utils.authenticate import get_current_user
from app.utils.database import get_db, SessionLocal

router = APIRouter()
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        conns = self.active_connections.setdefault(room_id, set())
        conns.add(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket):
        conns = self.active_connections.get(room_id)
        if conns and websocket in conns:
            conns.remove(websocket)
            if not conns:
                del self.active_connections[room_id]

    async def broadcast(self, room_id: str, message: dict):
        for conn in list(self.active_connections.get(room_id, [])):
            try:
                await conn.send_json(message)
            except Exception:
                self.disconnect(room_id, conn)


manager = ConnectionManager()

# ✅ Chat History with pagination
@router.get("/{room_id}", response_model=ChatHistoryResponse)
def get_chat_history(
    room_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total = db.query(func.count(ChatMessage.id)).filter(ChatMessage.room_id == room_id).scalar() or 0
    offset = (page - 1) * size

    messages = (db.query(ChatMessage)
                .filter(ChatMessage.room_id == room_id)
                .order_by(ChatMessage.created_at.desc())
                .offset(offset)
                .limit(size)
                .all())

    # convert metadata JSON string -> dict
    for msg in messages:
        if msg.meta_data:
            try:
                msg.meta_data = json.loads(msg.meta_data)
            except Exception:
                pass

    return ChatHistoryResponse(messages=messages, page=page, size=size, total=total)


# ✅ Last message in a room
@router.get("/{room_id}/last", response_model=LastMessageOut)
def get_last_message(room_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = (db.query(ChatMessage)
           .filter(ChatMessage.room_id == room_id)
           .order_by(ChatMessage.created_at.desc())
           .first())
    if not msg:
        raise HTTPException(status_code=404, detail="No messages found")

    if msg.meta_data:
        try:
            msg.meta_data = json.loads(msg.meta_data)
        except Exception:
            pass

    return msg


# ✅ Mark messages as read
@router.post("/{room_id}/read")
def mark_as_read(room_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated = (db.query(ChatMessage)
               .filter(ChatMessage.room_id == room_id, ChatMessage.receiver_id == current_user.id, ChatMessage.is_read == False)
               .update({ChatMessage.is_read: True}, synchronize_session=False))
    db.commit()
    return {"marked_read": updated}


# ✅ Send message via REST (fallback if WS not used)
@router.post("/send", response_model=ChatMessageOut)
def send_message(payload: ChatMessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized sender")

    raw_metadata = json.dumps(payload.metadata) if payload.metadata else None
    msg = ChatMessage(
        room_id=payload.room_id,
        sender_id=payload.sender_id,
        receiver_id=payload.receiver_id,
        content=payload.content,
        meta_data=raw_metadata,
        created_at=datetime.now(india_tz),
        is_read=False
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # broadcast to WS
    data = ChatMessageOut.model_validate(msg).dict()
    manager.broadcast(msg.room_id, {"type": "message", "message": data})

    return msg


# ✅ WebSocket
@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    # ⚠️ TODO: implement token-based authentication (JWT, etc.)
    await manager.connect(room_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "send":
                sender_id = data["sender_id"]
                receiver_id = data["receiver_id"]
                content = data["content"]
                metadata = data.get("metadata")

                db = SessionLocal()
                try:
                    msg = ChatMessage(
                        room_id=room_id,
                        sender_id=sender_id,
                        receiver_id=receiver_id,
                        content=content,
                        meta_data=json.dumps(metadata) if metadata else None,
                        created_at=datetime.now(india_tz),
                        is_read=False
                    )
                    db.add(msg)
                    db.commit()
                    db.refresh(msg)

                    out = ChatMessageOut.model_validate(msg).dict()
                    await manager.broadcast(room_id, {"type": "message", "message": out})
                finally:
                    db.close()

            elif action == "read":
                user_id = data.get("user_id")
                db = SessionLocal()
                try:
                    updated = (db.query(ChatMessage)
                               .filter(ChatMessage.room_id == room_id,
                                       ChatMessage.receiver_id == user_id,
                                       ChatMessage.is_read == False)
                               .update({ChatMessage.is_read: True}, synchronize_session=False))
                    db.commit()
                    await manager.broadcast(room_id, {"type": "read_update", "user_id": user_id, "marked": updated})
                finally:
                    db.close()

    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
