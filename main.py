from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Incident, SOS, Action
from gemini_service import classify_incident
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="disAIster Backend")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# DATABASE DEPENDENCY
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# REQUEST SCHEMAS
# -----------------------------
class IncidentRequest(BaseModel):
    message: str
    lat: float
    lng: float


class SOSRequest(BaseModel):
    name: str
    contact: str
    lat: float
    lng: float


class ActionRequest(BaseModel):
    type: str
    lat: float
    lng: float


# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
def root():
    return {"status": "Backend running successfully"}


# -----------------------------
# AI ANALYSIS
# -----------------------------
@app.post("/analyze")
def analyze_incident(data: IncidentRequest, db: Session = Depends(get_db)):

    ai_result = classify_incident(data.message)

    incident = Incident(
        message=data.message,
        lat=data.lat,
        lng=data.lng,
        disaster_type=ai_result["disaster_type"],
        severity=ai_result["severity"],
        risk_level=ai_result["risk_level"],
        confidence=ai_result["confidence"],
        medical_needed=ai_result["medical_needed"],
        satellite_verified=ai_result["satellite_verified"],
        timestamp=datetime.utcnow()
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return ai_result


# -----------------------------
# GET RECENT INCIDENTS (Last 24 Hours)
# -----------------------------
@app.get("/incidents")
def get_incidents(db: Session = Depends(get_db)):

    last_24_hours = datetime.utcnow() - timedelta(hours=24)

    incidents = db.query(Incident).filter(
        Incident.timestamp >= last_24_hours
    ).order_by(Incident.timestamp.desc()).all()

    return incidents


# -----------------------------
# SOS
# -----------------------------
@app.post("/sos")
def trigger_sos(data: SOSRequest, db: Session = Depends(get_db)):

    sos = SOS(
        name=data.name,
        contact=data.contact,
        lat=data.lat,
        lng=data.lng,
        timestamp=datetime.utcnow()
    )

    db.add(sos)
    db.commit()

    return {"message": "SOS received successfully"}


# -----------------------------
# QUICK ACTIONS (Drone / Aid / etc)
# -----------------------------
@app.post("/action")
def trigger_action(data: ActionRequest, db: Session = Depends(get_db)):

    action = Action(
        action_type=data.type,
        lat=data.lat,
        lng=data.lng,
        timestamp=datetime.utcnow()
    )

    db.add(action)
    db.commit()

    return {"message": f"{data.type.capitalize()} deployed successfully"}


# -----------------------------
# DANGER ZONE CHECK
# -----------------------------
@app.get("/is-user-in-danger")
def is_user_in_danger(lat: float, lng: float, db: Session = Depends(get_db)):

    recent_incidents = db.query(Incident).order_by(
        Incident.timestamp.desc()
    ).limit(20).all()

    for incident in recent_incidents:

        # Rough distance calculation (~km)
        distance = math.sqrt(
            (incident.lat - lat) ** 2 +
            (incident.lng - lng) ** 2
        )

        # 0.05 ≈ ~5km radius approx
        if distance < 0.05 and incident.severity >= 7:
            return {
                "in_danger": True,
                "severity": incident.risk_level
            }

    return {"in_danger": False}
