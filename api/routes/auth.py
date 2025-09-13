
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from api.db import get_db
from api.models_db import User, ApiKey, Tenant, Project, Membership
from api.security import hash_password, verify_password, create_access_token
import secrets

router = APIRouter()

class OrgSignup(BaseModel):
    company_name: str
    email: EmailStr
    password: str

class Login(BaseModel):
    email: EmailStr
    password: str

@router.post("/org-signup")
def org_signup(p: OrgSignup, db: Session = Depends(get_db)):
    # create tenant + default project + admin user
    t = Tenant(name=p.company_name)
    db.add(t); db.commit(); db.refresh(t)
    pr = Project(name="Default", tenant_id=t.id)
    db.add(pr); db.commit()
    u = User(email=p.email, password_hash=hash_password(p.password), role="admin", tenant_id=t.id)
    db.add(u); db.commit(); db.refresh(u)
    db.add(Membership(user_id=u.id, project_id=pr.id, role="admin")); db.commit()
    # API key per tenant
    raw = secrets.token_urlsafe(32)
    db.add(ApiKey(owner_email=u.email, tenant_id=t.id, key_hash=raw)); db.commit()
    token = create_access_token(u.email, u.role, t.id)
    return {"access_token": token, "api_key": raw, "tenant_id": t.id, "project_id": pr.id}

@router.post("/login")
def login(p: Login, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email==p.email).first()
    if not u or not verify_password(p.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(u.email, u.role, u.tenant_id)
    return {"access_token": token, "role": u.role, "tenant_id": u.tenant_id}
