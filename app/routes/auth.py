from datetime import datetime, timezone

from fastapi import Depends, APIRouter, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.security import ALGORITHM, SECRET_KEY
from app.core.token import create_access_token
from app.database.db import get_db
from app.models.models import RefreshToken
from app.schemas.user_schemas import UserCreate, UserLogin
from app.schemas.token_schemas import TokenResponse, RefreshTokenRequest
from app.core.hash import hash_password,verify_password,hash_refresh_token
from app.services.auth_service import register_user, authenticate_user, create_tokens
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user.email, user.password)


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    logger.info("login_request", extra={"email": user.email})
    db_user = authenticate_user(db, user.email, user.password)

    if not db_user:
        logger.warning("login_failed", extra={"email": user.email})
        raise HTTPException(status_code=400, detail="invalid credentials")
    logger.info("login_success", extra={"email": user.email, "user_id": db_user.id})
    access, refresh = create_tokens(db_user, db)

    return {"access_token": access, "refresh_token": refresh}


@router.post("/refresh")
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
   
    hashed = hash_refresh_token(data.refresh_token)

    token = db.query(RefreshToken).filter(
        RefreshToken.token == hashed
    ).first()

    if not token:
        logger.warning("refresh_failed", extra={"reason": "invalid_token"})
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if token.expires_at < datetime.now(timezone.utc):
        db.delete(token)
        db.commit()
        raise HTTPException(status_code=401, detail="Token expired")

    access = create_access_token({"sub": str(token.user_id)})

    return {"access_token": access}