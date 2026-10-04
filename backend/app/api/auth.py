"""
AUTH API ROUTE: User Registration, Login & Profile Retrieval
============================================================
Exposes POST /api/auth/register, POST /api/auth/login, and GET /api/auth/me.
"""

from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import User, UserProfile
from backend.app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=4, description="User password")


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Registers a new user and creates their default profile."""
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    new_user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        role="user",
        is_active=True
    )
    db.add(new_user)
    db.flush()

    # Create default user profile
    profile = UserProfile(
        user_id=new_user.id,
        diet_type="none",
        allergies="[]",
        daily_calorie_target=600.0,
        preferred_cuisines="Sri Lankan"
    )
    db.add(profile)
    db.commit()

    token = create_access_token({"sub": str(new_user.id), "email": new_user.email})
    return AuthResponse(access_token=token, user_id=new_user.id, email=new_user.email)


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Logs in an existing user and returns a signed JWT."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return AuthResponse(access_token=token, user_id=user.id, email=user.email)
