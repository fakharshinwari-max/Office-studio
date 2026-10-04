"""Document CRUD routes (shared by Writer, Sheets, Slides)."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Document, Version, User
from ..auth import get_current_user

router = APIRouter(prefix="/api/docs", tags=["docs"])


class DocIn(BaseModel):
    kind: str          # word|sheets|slides
    name: str = "Untitled"
    data: dict = {}


class DocOut(BaseModel):
    id: int
    kind: str
    name: str
    data: dict
    updated_at: datetime
    class Config:
        from_attributes = True


def _owned(doc_id: int, user: User, db: Session) -> Document:
    d = db.query(Document).filter(Document.id == doc_id, Document.owner_id == user.id).first()
    if not d:
        raise HTTPException(404, "Document not found")
    return d


@router.get("", response_model=list[DocOut])
def list_docs(kind: str | None = Query(None), user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    q = db.query(Document).filter(Document.owner_id == user.id)
    if kind:
        q = q.filter(Document.kind == kind)
    return q.order_by(Document.updated_at.desc()).all()


@router.post("", response_model=DocOut)
def create_doc(body: DocIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    d = Document(owner_id=user.id, kind=body.kind, name=body.name, data=body.data)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


@router.get("/{doc_id}", response_model=DocOut)
def get_doc(doc_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _owned(doc_id, user, db)


@router.put("/{doc_id}", response_model=DocOut)
def update_doc(doc_id: int, body: DocIn, user: User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    d = _owned(doc_id, user, db)
    d.name = body.name
    d.data = body.data
    d.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(d)
    return d


@router.delete("/{doc_id}")
def delete_doc(doc_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    d = _owned(doc_id, user, db)
    db.delete(d)
    db.commit()
    return {"ok": True}


# ---------- Versions ----------

@router.get("/{doc_id}/versions")
def list_versions(doc_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _owned(doc_id, user, db)
    versions = db.query(Version).filter(Version.document_id == doc_id).order_by(Version.created_at.desc()).all()
    return [{"id": v.id, "label": v.label, "created_at": v.created_at} for v in versions]


@router.post("/{doc_id}/versions")
def snapshot(doc_id: int, label: str = "", user: User = Depends(get_current_user),
             db: Session = Depends(get_db)):
    d = _owned(doc_id, user, db)
    v = Version(document_id=d.id, data=d.data, label=label)
    db.add(v)
    db.commit()
    return {"id": v.id}


@router.post("/{doc_id}/restore/{version_id}")
def restore(doc_id: int, version_id: int, user: User = Depends(get_current_user),
            db: Session = Depends(get_db)):
    d = _owned(doc_id, user, db)
    v = db.query(Version).filter(Version.id == version_id, Version.document_id == doc_id).first()
    if not v:
        raise HTTPException(404, "Version not found")
    d.data = v.data
    db.commit()
    return {"ok": True}