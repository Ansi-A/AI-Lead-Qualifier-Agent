from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from .security import SECRET_KEY, ALGORITHM
from app.core.hash import hash_refresh_token


# creating
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token():
    import secrets
    token =secrets.token_hex(16)
    hashed_token = hash_refresh_token(token)
    return hashed_token
    
