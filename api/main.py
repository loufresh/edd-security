
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import jobs, alerts, integrations, auth, webhooks, events, runs
from api.db import engine
from api.models_db import Base
import os

# Si existe la base SQLite, la borra al iniciar
if os.path.exists("eddsec.db"):
    os.remove("eddsec.db")
    print(">>> eddsec.db borrado, se recreará vacío")

app = FastAPI(title="EDD Security API", version="0.5.0")
Base.metadata.create_all(bind=engine)

# CORS for local dashboard & quick demos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080","*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(runs.router, prefix="/runs", tags=["runs"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(events.router, prefix="/events", tags=["events"])

@app.get("/")
def root():
    return {"name": "EDD Security API", "ok": True, "version": "0.5.0"}
