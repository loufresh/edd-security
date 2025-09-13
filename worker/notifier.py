
import os, requests, smtplib
from email.mime.text import MIMEText

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# WhatsApp via Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM","whatsapp:+14155238886")
WHATSAPP_TO = os.getenv("WHATSAPP_TO")
# Email
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT","587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

def send_slack(text: str):
    if not SLACK_WEBHOOK_URL: return {"skipped": "no webhook"}
    try:
        r = requests.post(SLACK_WEBHOOK_URL, json={"text": text}, timeout=10)
        return {"ok": r.ok, "status": r.status_code}
    except Exception as e:
        return {"error": str(e)}

def send_telegram(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: return {"skipped": "no telegram config"}
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
        return {"ok": r.ok, "status": r.status_code}
    except Exception as e:
        return {"error": str(e)}

def send_whatsapp(text: str):
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and WHATSAPP_TO): return {"skipped": "no twilio config"}
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    data = {"From": TWILIO_WHATSAPP_FROM, "To": WHATSAPP_TO, "Body": text}
    try:
        r = requests.post(url, data=data, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=10)
        return {"ok": r.ok, "status": r.status_code}
    except Exception as e:
        return {"error": str(e)}

def send_email(subject: str, body: str):
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and EMAIL_TO): return {"skipped": "no smtp config"}
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_TO
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, [EMAIL_TO], msg.as_string())
        return {"ok": True}
    except Exception as e:
        return {"error": str(e)}

def notify_all(text: str):
    out = {"slack": send_slack(text), "telegram": send_telegram(text), "whatsapp": send_whatsapp(text), "email": send_email("EDD Security Alert", text)}
    return out
