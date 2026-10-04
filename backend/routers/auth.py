"""Auth routes."""
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..auth import hash_password, verify_password, create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: str = ""


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
    u = User(email=body.email, name=body.name, password_hash=hash_password(body.password))
    db.add(u)
    db.commit()
    db.refresh(u)
    return TokenOut(access_token=create_access_token(u.email),
                    refresh_token=create_refresh_token(u.email))


@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == form.username).first()
    if not u or not verify_password(form.password, u.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return TokenOut(access_token=create_access_token(u.email),
                    refresh_token=create_refresh_token(u.email))


@router.post("/refresh", response_model=TokenOut)
def refresh(refresh_token: str = Body(..., embed=True)):
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid refresh token")
    return TokenOut(access_token=create_access_token(payload["sub"]),
                    refresh_token=create_refresh_token(payload["sub"]))