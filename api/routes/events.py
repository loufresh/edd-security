
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from time import sleep
import json
from api.db import get_db
from api.models_db import Alert
from api.security import get_current_user

router = APIRouter()

def event_stream(db: Session, tenant_id: int):
    last_id = None
    while True:
        q = db.query(Alert).filter(Alert.tenant_id==tenant_id).order_by(Alert.id.desc()).limit(10).all()
        payload = [{"id": a.id, "severity": a.severity, "message": a.message} for a in q]
        yield f"data: {json.dumps(payload)}\n\n"
        sleep(3)

@router.get("/stream")
def stream(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return StreamingResponse(event_stream(db, user.tenant_id), media_type="text/event-stream")
