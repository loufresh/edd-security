
from ..celery_app import celery
import boto3, os, base64, io

@celery.task(name="integrations.s3.put_object")
def s3_put_object(params: dict):
    """Upload a small text/CSV file to S3.
    params = {bucket, key, content (base64 or str), region, aws_access_key_id, aws_secret_access_key}
    """
    content = params.get("content","")
    if isinstance(content, str) and not content.startswith("data:") and not _looks_b64(content):
        data = content.encode()
    else:
        data = base64.b64decode(content.split(",")[-1]) if isinstance(content,str) else content

    s3 = boto3.client(
        "s3",
        region_name=params.get("region","us-east-1"),
        aws_access_key_id=params.get("aws_access_key_id"),
        aws_secret_access_key=params.get("aws_secret_access_key"),
    )
    s3.put_object(Bucket=params["bucket"], Key=params["key"], Body=data)
    return {"bucket": params["bucket"], "key": params["key"]}

def _looks_b64(s: str) -> bool:
    try:
        base64.b64decode(s, validate=True)
        return True
    except Exception:
        return False
