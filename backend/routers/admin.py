"""Real-time collaboration — WebSocket + Yjs-style ops relay."""
from __future__ import annotations

import asyncio
import json
import random
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from ..auth import decode_token
from ..config import get_settings
from ..database import SessionLocal
from ..models import User

router = APIRouter(prefix="/api/collab", tags=["collab"])
settings = get_settings()


class Room:
    def __init__(self):
        self.clients: dict[int, dict[str, WebSocket]] = {}
        self.presence: dict[int, dict[str, dict]] = {}
        self.docs: dict[int, dict] = {}
        self.lock = asyncio.Lock()

    async def join(self, doc_id: int, client_id: str, ws: WebSocket, who: dict):
        async with self.lock:
            self.clients.setdefault(doc_id, {})[client_id] = ws
            self.presence.setdefault(doc_id, {})[client_id] = who
        await self.broadcast(doc_id, {"type": "presence", "action": "join", "clientId": client_id, "who": who})

    async def leave(self, doc_id: int, client_id: str):
        async with self.lock:
            doc_clients = self.clients.get(doc_id, {})
            doc_presence = self.presence.get(doc_id, {})
            doc_clients.pop(client_id, None)
            doc_presence.pop(client_id, None)
            if not doc_clients:
                self.clients.pop(doc_id, None)
            if not doc_presence:
                self.presence.pop(doc_id, None)
        await self.broadcast(doc_id, {"type": "presence", "action": "leave", "clientId": client_id})

    async def broadcast(self, doc_id: int, msg: dict, skip: str | None = None):
        dead: list[str] = []
        for client_id, ws in list(self.clients.get(doc_id, {}).items()):
            if client_id == skip:
                continue
            try:
                await ws.send_json(msg)
            except Exception:
                dead.append(client_id)
        for client_id in dead:
            self.clients.get(doc_id, {}).pop(client_id, None)
            self.presence.get(doc_id, {}).pop(client_id, None)


_room = Room()


@router.websocket("/ws/{doc_id}")
async def collab_ws(ws: WebSocket, doc_id: int):
    await ws.accept()

    token = ws.query_params.get("token") or ""
    try:
        payload = decode_token(token)
        email = payload.get("sub")
    except Exception:
        await ws.send_json({"type": "error", "message": "unauthorized"})
        await ws.close()
        return

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
    finally:
        db.close()

    if not user:
        await ws.send_json({"type": "error", "message": "user not found"})
        await ws.close()
        return

    colors = [
        "#2b579a",
        "#217346",
        "#d24726",
        "#f2c94c",
        "#6f42c1",
        "#17a2b8",
        "#e91e63",
        "#009688",
        "#ff9800",
        "#795548",
    ]
    who = {"userId": user.id, "name": user.name or user.email, "color": random.choice(colors)}
    client_id = str(uuid.uuid4())[:8]

    await _room.join(doc_id, client_id, ws, who)
    await ws.send_json({"type": "welcome", "clientId": client_id, "who": who, "peers": _room.presence.get(doc_id, {})})

    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            msg["from"] = client_id
            doc_presence = _room.presence.setdefault(doc_id, {})
            if msg.get("type") == "cursor":
                doc_presence.setdefault(client_id, {})["cursor"] = msg.get("cursor")
            elif msg.get("type") == "op":
                pass
            await _room.broadcast(doc_id, msg, skip=client_id)
    except WebSocketDisconnect:
        pass
    finally:
        await _room.leave(doc_id, client_id)
