
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from api.db import get_db
from api.models_db import Alert
from api.security import get_current_user

router = APIRouter()

@router.get("/")
def list_alerts(db: Session = Depends(get_db), user=Depends(get_current_user), project_id: Optional[int]=Query(None)):
    q = db.query(Alert).filter(Alert.tenant_id==user.tenant_id)
    if project_id is not None:
        q = q.filter(Alert.project_id==project_id)
    rows = q.order_by(Alert.id.desc()).limit(200).all()
    return {"alerts": [{
        "id": a.id, "severity": a.severity, "message": a.message, "metadata": a.metadata, "created_at": a.created_at, "project_id": a.project_id
    } for a in rows]}
