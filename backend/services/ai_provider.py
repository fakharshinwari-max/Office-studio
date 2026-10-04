"""Admin console — user/role management, quotas, audit log, retention."""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import AIUsage, AuditEvent, Document, User

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _require_admin(user: User) -> User:
    if user.role != "admin":
        raise HTTPException(403, "Admin only")
    return user


@router.get("/stats")
def stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_admin(user)
    return {
        "users": db.query(User).count(),
        "documents": db.query(Document).count(),
        "documents_by_kind": dict(db.query(Document.kind, func.count(Document.id)).group_by(Document.kind).all()),
        "ai_calls_30d": db.query(AIUsage).filter(AIUsage.at >= datetime.utcnow() - timedelta(days=30)).count(),
        "storage_mb_used": db.query(func.sum(User.used_mb)).scalar() or 0,
    }


@router.get("/users")
def list_users(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_admin(user)
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "role": u.role,
            "quota_mb": u.quota_mb,
            "used_mb": u.used_mb,
            "locale": u.locale,
            "is_active": u.is_active,
            "last_login": u.last_login,
            "created_at": u.created_at,
        }
        for u in users
    ]


class UserPatch(BaseModel):
    role: str | None = None
    quota_mb: int | None = None
    is_active: bool | None = None


@router.patch("/users/{user_id}")
def patch_user(user_id: int, body: UserPatch, admin: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_admin(admin)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    if body.role is not None:
        user.role = body.role
    if body.quota_mb is not None:
        user.quota_mb = body.quota_mb
    if body.is_active is not None:
        user.is_active = body.is_active
    db.commit()
    return {"ok": True}


@router.get("/audit")
def audit(limit: int = 200, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_admin(user)
    rows = db.query(AuditEvent).order_by(AuditEvent.at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "userId": r.user_id,
            "action": r.action,
            "target": r.target,
            "meta": r.meta,
            "ip": r.ip,
            "at": r.at,
        }
        for r in rows
    ]


@router.delete("/purge-trash")
def purge_trash(days: int = 30, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_admin(user)
    cutoff = datetime.utcnow() - timedelta(days=days)
    n = db.query(Document).filter(Document.deleted_at.is_not(None), Document.deleted_at < cutoff).delete()
    db.commit()
    return {"purged": n}
