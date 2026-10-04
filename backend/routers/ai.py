"""Auth routes."""
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from ..database import get_db
from ..models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: str = ""


class RefreshIn(BaseModel):
    refresh_token: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=TokenOut)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, "Email already registered")
    if len(body.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    user = User(email=body.email, name=body.name, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenOut(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )


@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return TokenOut(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )


@router.post("/refresh", response_model=TokenOut)
def refresh(payload: RefreshIn | None = Body(default=None)):
    token = payload.refresh_token if payload else None
    if not token:
        raise HTTPException(401, "Refresh token is required")
    decoded = decode_token(token)
    if decoded.get("type") != "refresh":
        raise HTTPException(401, "Invalid refresh token")
    return TokenOut(
        access_token=create_access_token(decoded["sub"]),
        refresh_token=create_refresh_token(decoded["sub"]),
    )
