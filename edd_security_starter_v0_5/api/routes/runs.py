
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from api.db import get_db
from api.models_db import JobRun
from api.security import get_current_user

router = APIRouter()

@router.get("/")
def list_runs(db: Session = Depends(get_db),
              user=Depends(get_current_user),
              project_id: Optional[int]=Query(None),
              limit: int = Query(50, le=200)):
    q = db.query(JobRun).filter(JobRun.tenant_id==user.tenant_id)
    if project_id is not None:
        q = q.filter(JobRun.project_id==project_id)
    rows = q.order_by(JobRun.created_at.desc()).limit(limit).all()
    return {"runs": [{
        "id": r.id, "task_name": r.task_name, "status": r.status,
        "created_at": r.created_at, "finished_at": r.finished_at,
        "job_id": r.job_id, "project_id": r.project_id, "output": r.output, "error_text": r.error_text
    } for r in rows]}
