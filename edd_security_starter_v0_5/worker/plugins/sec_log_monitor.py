from ..celery_app import celery
import re, time, datetime as dt, os
from ..tasks_core import push_alert

LOG_PATH = os.getenv("WEB_LOG_PATH", "/var/log/nginx/access.log")
FAILED_PAT = re.compile(r'\s(401|403|404)\s')

@celery.task(name="security.monitor_logs")
def monitor_logs(params: dict):
    win = int(params.get("window_sec", 60))
    th = int(params.get("threshold", 30))
    end = time.time() + win
    fails = 0
    try:
        with open(LOG_PATH, "r", errors="ignore") as f:
            f.seek(0,2)
            while time.time() < end:
                line = f.readline()
                if not line:
                    time.sleep(0.2); continue
                if FAILED_PAT.search(line): fails += 1
    except FileNotFoundError:
        return {"error": f"log file not found: {LOG_PATH}", "alert": False}

    alert = fails >= th
    if alert:
        push_alert.delay({
            "severity": "high",
            "message": f"Spike of failed requests: {fails} in {win}s",
            "metadata": {"window_sec": win, "fails": fails, "threshold": th}
        })

    return {
        "window_sec": win, "fails": fails, "threshold": th,
        "alert": alert,
        "timestamp": dt.datetime.utcnow().isoformat()
    }
