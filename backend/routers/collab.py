"""Real-time collaboration — WebSocket + Yjs-style ops relay."""
from __future__ import annotations
from typing import Any
import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth import get_current_user, decode_token
from ..database import get_db, SessionLocal
from ..models import Document, User
from ..config import get_settings

router = APIRouter(prefix="/api/collab", tags=["collab"])
settings = get_settings()


class Room:
    def __init__(self):
        self.clients: dict[str, WebSocket] = {}   # clientId -> ws
        self.presence: dict[str, dict] = {}       # clientId -> {name, color, cursor}
        self.docs: dict[int, dict] = {}           # docId -> latest snapshot (fallback)
        self.lock = asyncio.Lock()

    async def join(self, doc_id: int, client_id: str, ws: WebSocket, who: dict):
        async with self.lock:
            self.clients[client_id] = ws
            self.presence[client_id] = who
        await self.broadcast(doc_id, {"type": "presence", "action": "join", "clientId": client_id, "who": who})

    async def leave(self, doc_id: int, client_id: str):
        async with self.lock:
            self.clients.pop(client_id, None)
            self.presence.pop(client_id, None)
        await self.broadcast(doc_id, {"type": "presence", "action": "leave", "clientId": client_id})

    async def broadcast(self, doc_id: int, msg: dict, skip: str | None = None):
        dead = []
        for cid, ws in list(self.clients.items()):
            if cid == skip:
                continue
            try:
                await ws.send_json(msg)
            except Exception:
                dead.append(cid)
        for cid in dead:
            self.clients.pop(cid, None)
            self.presence.pop(cid, None)


_room = Room()


@router.websocket("/ws/{doc_id}")
async def collab_ws(ws: WebSocket, doc_id: int):
    await ws.accept()

    # Auth via query param ?token=...
    token = ws.query_params.get("token") or ""
    try:
        payload = decode_token(token)
        email = payload.get("sub")
    except Exception:
        await ws.send_json({"type": "error", "message": "unauthorized"})
        await ws.close()
        return

    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    if not user:
        await ws.send_json({"type": "error", "message": "user not found"})
        await ws.close()
        return

    # Every connection gets a random color
    import random
    colors = ["#2b579a", "#217346", "#d24726", "#f2c94c", "#6f42c1",
              "#17a2b8", "#e91e63", "#009688", "#ff9800", "#795548"]
    who = {"userId": user.id, "name": user.name or user.email,
           "color": random.choice(colors)}

    import uuid
    client_id = str(uuid.uuid4())[:8]

    await _room.join(doc_id, client_id, ws, who)
    await ws.send_json({"type": "welcome", "clientId": client_id, "who": who,
                        "peers": _room.presence})

    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            msg["from"] = client_id
            if msg.get("type") == "cursor":
                _room.presence[client_id]["cursor"] = msg.get("cursor")
            elif msg.get("type") == "op":
                # Relay to others; server may also persist to Document.data
                pass
            await _room.broadcast(doc_id, msg, skip=client_id)
    except WebSocketDisconnect:
        pass
    finally:
        await _room.leave(doc_id, client_id)