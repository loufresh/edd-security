
from ..celery_app import celery
import requests, time
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (EDD Security Starter)"}

@celery.task(name="automation.scrape_prices")
def scrape_prices(params: dict):
    urls = params.get("urls", [])
    selector = params.get("selector", "title")
    delay = params.get("delay", 1)
    out = []
    for url in urls:
        r = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        el = soup.select_one(selector)
        out.append({"url": url, "value": el.get_text(strip=True) if el else None})
        time.sleep(delay)
    return {"items": out}

@celery.task(name="automation.build_report")
def build_report(params: dict):
    import csv, io, base64
    rows = params.get("rows", [])
    buf = io.StringIO()
    cols = rows[0].keys() if rows else ["url","value"]
    w = csv.DictWriter(buf, fieldnames=list(cols))
    w.writeheader()
    for r in rows: w.writerow(r)
    return {"csv_base64": base64.b64encode(buf.getvalue().encode()).decode(), "rows": len(rows)}
