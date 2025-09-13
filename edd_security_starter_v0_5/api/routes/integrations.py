
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def list_integrations():
    return {"integrations": ["google_sheets", "aws_s3 (example)", "slack (example)"]}
