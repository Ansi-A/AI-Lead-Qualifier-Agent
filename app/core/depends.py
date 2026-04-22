from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .security import SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(request:Request,token: str = Depends(oauth2_scheme)):
    print("RAW HEADER:", request.headers.get("authorization"))
    print("TOKEN:", token)
    print("TOKEN:", token) 
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("PAYLOAD:", payload)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload.get("sub")
    except JWTError as e:
        print("JWT ERROR:", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")
