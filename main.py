from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Incident, SOS
from gemini_service import classify_incident
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="disAIster Backend")

# Enable CORS for frontend connection
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


# -----------------------------
# ROOT TEST
# -----------------------------
@app.get("/")
def root():
    return {"status": "Backend running successfully"}


# -----------------------------
# AI ANALYSIS ENDPOINT
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
# GET ALL INCIDENTS
# -----------------------------
@app.get("/incidents")
def get_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.timestamp.desc()).all()


# -----------------------------
# SOS ENDPOINT
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
# DANGER ZONE CHECK
# -----------------------------
@app.get("/is-user-in-danger")
def is_user_in_danger(lat: float, lng: float, db: Session = Depends(get_db)):

    recent_incidents = db.query(Incident).order_by(
        Incident.timestamp.desc()
    ).limit(20).all()

    for incident in recent_incidents:
        distance = ((incident.lat - lat) ** 2 + (incident.lng - lng) ** 2) ** 0.5
        if distance < 0.05 and incident.severity >= 7:
            return {
                "in_danger": True,
                "severity": incident.risk_level
            }

    return {"in_danger": False}