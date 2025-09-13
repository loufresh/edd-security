
from .celery_app import celery
import datetime as dt, os, traceback, requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models_db import JobRun, Alert, Base, Job  # shared models
from api.db import DATABASE_URL  # DSN
from .notifier import notify_all

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)

# Optional: webhook URL per job via env map JSON {"<job_id>":"https://..."}
JOB_WEBHOOKS = {}
try:
    import json
    JOB_WEBHOOKS = json.loads(os.getenv("JOB_WEBHOOKS_JSON","{}"))
except Exception:
    JOB_WEBHOOKS = {}

@celery.task(name="core.run_and_record")
def run_and_record(ctx: dict):
    task_name = ctx["task_name"]
    params = ctx.get("params", {})
    job_run_id = ctx["job_run_id"]
    tenant_id = ctx.get("tenant_id")
    project_id = ctx.get("project_id")

    db = SessionLocal()
    try:
        result = celery.tasks[task_name].apply(args=[params]).get()

        # Persist success
        run = db.get(JobRun, job_run_id)
        if run:
            run.status = "success"
            run.output = result
            run.finished_at = dt.datetime.utcnow()
            db.add(run); db.commit()

        # Outgoing webhook if configured at env or job param
        _send_job_webhook(db, run, result)

        return result
    except Exception as e:
        run = db.get(JobRun, job_run_id)
        if run:
            run.status = "error"
            run.error_text = str(e)
            run.finished_at = dt.datetime.utcnow()
            db.add(run); db.commit()
        return {"error": str(e), "trace": traceback.format_exc()}
    finally:
        db.close()

def _send_job_webhook(db, run: JobRun, payload):
    try:
        job = db.get(Job, run.job_id) if run and run.job_id else None
        url = None
        if job and isinstance(job.params, dict):
            url = job.params.get("webhook_url")
        if not url and run and str(run.job_id) in JOB_WEBHOOKS:
            url = JOB_WEBHOOKS[str(run.job_id)]
        if url:
            try:
                requests.post(url, json={"job_run_id": run.id, "status": run.status, "output": run.output}, timeout=10)
            except Exception:
                pass
    except Exception:
        pass

@celery.task(name="core.push_alert")
def push_alert(payload: dict):
    db = SessionLocal()
    try:
        a = Alert(tenant_id=payload.get("tenant_id"),
                  project_id=payload.get("project_id"),
                  severity=payload.get("severity","low"),
                  message=payload.get("message","alert"),
                  metadata=payload.get("metadata"))
        db.add(a); db.commit()
        notify_all(f"[EDD Security] {a.severity.upper()} — {a.message}")
        return {"id": a.id}
    finally:
        db.close()
