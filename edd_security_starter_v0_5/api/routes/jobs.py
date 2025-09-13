
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from api.db import get_db
from api.models_db import Job, JobRun
from api.security import get_current_user, require_role, get_api_key
from worker.celery_app import celery
import uuid

router = APIRouter()

class JobIn(BaseModel):
    project_id: Optional[int] = None
    type: str = Field(..., description="Celery task name")
    params: Dict[str, Any] = Field(default_factory=dict)
    schedule: Optional[str] = Field(default=None, description="cron-like (future)")

class RunNowIn(BaseModel):
    task_name: str
    params: Dict[str, Any] = Field(default_factory=dict)
    job_id: Optional[int] = None
    project_id: Optional[int] = None

@router.post("/", dependencies=[Depends(require_role("admin","operator"))])
def create_job(job: JobIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = Job(tenant_id=user.tenant_id, project_id=job.project_id, type=job.type, params=job.params, schedule=job.schedule)
    db.add(obj); db.commit(); db.refresh(obj)
    return {"status": "created", "job": {"id": obj.id, "type": obj.type, "project_id": obj.project_id}}

@router.get("/", dependencies=[Depends(require_role("admin","operator","viewer"))])
def list_jobs(db: Session = Depends(get_db), user=Depends(get_current_user), project_id: Optional[int] = Query(None)):
    q = db.query(Job).filter(Job.tenant_id==user.tenant_id)
    if project_id is not None:
        q = q.filter(Job.project_id==project_id)
    rows = q.order_by(Job.id.desc()).all()
    return {"jobs": [{"id": j.id, "type": j.type, "project_id": j.project_id, "params": j.params} for j in rows]}

@router.post("/run-now")
def run_now(payload: RunNowIn, db: Session = Depends(get_db), user=Depends(get_current_user), api_key=Depends(get_api_key)):
    tenant_id = user.tenant_id if api_key is None else api_key.tenant_id
    job_run_id = str(uuid.uuid4())
    run = JobRun(id=job_run_id, job_id=payload.job_id, project_id=payload.project_id, task_name=payload.task_name, status="queued", tenant_id=tenant_id)
    db.add(run); db.commit()
    try:
        async_result = celery.send_task("core.run_and_record", args=[{
            "task_name": payload.task_name,
            "params": payload.params,
            "job_run_id": job_run_id,
            "tenant_id": tenant_id,
            "project_id": payload.project_id
        }])
        return {"task_id": async_result.id, "job_run_id": job_run_id, "enqueued": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
