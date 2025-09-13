
from fastapi import APIRouter, Request, Depends, Header
from sqlalchemy.orm import Session
from api.db import get_db
from api.models_db import Alert

router = APIRouter()

@router.post("/ingest")
async def ingest(req: Request, db: Session = Depends(get_db), x_tenant_id: int = Header(...), x_project_id: int | None = Header(default=None)):
    body = await req.json()
    a = Alert(tenant_id=x_tenant_id, project_id=x_project_id, severity=body.get("severity","info"),
              message=body.get("message","webhook"), metadata=body)
    db.add(a); db.commit()
    return {"ok": True, "id": a.id}
