from sqlalchemy.orm import Session
from app.core.hash import hash_password, verify_password,hash_refresh_token
from app.core.token import create_access_token
from app.database.db import get_db
from app.models.models import User, RefreshToken
from datetime import datetime, timedelta, timezone
from fastapi import Depends


def register_user(db: Session, email: str, password: str):
    user = User(email=email, password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print("no user")
        return None
    if not verify_password(password, user.password):
        print("not verified")
        return None
    print(f"""returning user{user}""")
    return user


def create_tokens(user: User, db: Session):
    import secrets
    print("creating the accesstoken")
    print(f"this is {user.id}")
    access_token = create_access_token({"sub": user.id})
    print(f"access token created {access_token}")
    refresh_token = secrets.token_hex(16)
    hashed_token = hash_refresh_token(refresh_token)
    
    db_token = RefreshToken(
        user_id=user.id,
        token=hashed_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return access_token, refresh_token
