import os

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analytics, auth, checklist, clients, documents, firms, portal, signature, voice
from app.db import init_db
from app.services.reminder_engine import run_daily_reminders

app = FastAPI(title="CPAOS - AI Client Onboarding Engine", version="2.0.0")

scheduler = BackgroundScheduler()

origins = [
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
    "http://localhost:5173",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()
    if not scheduler.running:
        scheduler.add_job(run_daily_reminders, "cron", hour=9, minute=0, id="cpaos_daily_reminders")
        scheduler.start()


@app.on_event("shutdown")
def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(firms.router, prefix="/api", tags=["firms"])
app.include_router(clients.router, prefix="/api", tags=["clients"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(checklist.router, prefix="/api", tags=["checklist"])
app.include_router(portal.router, prefix="/api/portal", tags=["portal"])
app.include_router(signature.router, prefix="/api/signature", tags=["signature"])
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])


@app.get("/health")
def health():
    return {"status": "healthy", "product": "CPAOS", "version": "2.0.0"}
