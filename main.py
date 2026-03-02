from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Incident, SOS
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

Base.metadata.create_all(bind=engine)

app = FastAPI(title="disAIster Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class IncidentRequest(BaseModel):
    message: str
    lat: float
    lng: float

class SOSRequest(BaseModel):
    name: str
    contact: str
    lat: float
    lng: float

@app.get("/")
def root():
    return {"status": "Backend running"}

@app.post("/analyze")
def analyze_incident(data: IncidentRequest, db: Session = Depends(get_db)):

    disaster_types = ["flood", "fire", "earthquake", "cyclone"]
    disaster_type = random.choice(disaster_types)
    severity = random.randint(4, 9)

    risk_level = (
        "HIGH" if severity >= 7 else
        "MEDIUM" if severity >= 5 else
        "LOW"
    )

    confidence = random.randint(70, 95)

    incident = Incident(
        message=data.message,
        lat=data.lat,
        lng=data.lng,
        disaster_type=disaster_type,
        severity=severity,
        risk_level=risk_level,
        confidence=confidence,
        medical_needed="Yes" if severity >= 7 else "No",
        satellite_verified=True,
        timestamp=datetime.utcnow()
    )

    db.add(incident)
    db.commit()

    return {
        "disaster_type": disaster_type,
        "severity": severity,
        "risk_level": risk_level,
        "confidence": confidence
    }

@app.get("/incidents")
def get_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.timestamp.desc()).all()

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

    return {"message": "SOS received"}
