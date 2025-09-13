
from ..celery_app import celery

@celery.task(name="integrations.google_sheets.append_rows")
def gsheet_append_rows(params: dict):
    import json
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    info = json.loads(params["service_account_json"])
    creds = service_account.Credentials.from_service_account_info(info, scopes=[
        "https://www.googleapis.com/auth/spreadsheets"
    ])
    svc = build("sheets","v4", credentials=creds)
    body = {"values": params["values"]}
    res = svc.spreadsheets().values().append(
        spreadsheetId=params["spreadsheet_id"],
        range=params["range"],
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    return {"updated": res.get("updates",{})}
