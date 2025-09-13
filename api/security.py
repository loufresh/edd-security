
import os, time
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from api.db import get_db
from api.models_db import User, ApiKey, Membership

SECRET = os.getenv("JWT_SECRET", "change_me")
ALGO = "HS256"
ACCESS_MIN = int(os.getenv("ACCESS_TOKEN_MIN", "120"))
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd.hash(p)

def verify_password(p: str, h: str) -> bool:
    return pwd.verify(p, h)

def create_access_token(sub: str, role: str, tenant_id: int):
    now = int(time.time())
    payload = {"sub": sub, "role": role, "tenant_id": tenant_id, "iat": now, "exp": now + ACCESS_MIN*60}
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def decode_token(token: str):
    return jwt.decode(token, SECRET, algorithms=[ALGO])

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ",1)[1]
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    user = db.query(User).filter(User.email==email, User.tenant_id==tenant_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(*roles):
    def _inner(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return _inner

def require_project_role(project_id: int, *roles):
    def _inner(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        m = db.query(Membership).filter(Membership.user_id==user.id, Membership.project_id==project_id).first()
        if not m or m.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient project role")
        return user
    return _inner

def get_api_key(x_api_key: Optional[str] = Header(None), db: Session = Depends(get_db)) -> ApiKey | None:
    if not x_api_key: return None
    row = db.query(ApiKey).filter(ApiKey.key_hash==x_api_key).first()
    return row
