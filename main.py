from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Incident, SOS
from gemini_service import classify_incident
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math

Base.metadata.create_all(bind=engine)

app = FastAPI()

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

class ActionRequest(BaseModel):
    type: str
    lat: float
    lng: float

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/analyze")
def analyze(data: IncidentRequest, db: Session = Depends(get_db)):
    ai = classify_incident(data.message)

    incident = Incident(
        message=data.message,
        lat=data.lat,
        lng=data.lng,
        disaster_type=ai["disaster_type"],
        severity=ai["severity"],
        risk_level=ai["risk_level"],
        confidence=ai["confidence"],
        medical_needed=ai["medical_needed"],
        satellite_verified=ai["satellite_verified"],
        timestamp=datetime.utcnow()
    )

    db.add(incident)
    db.commit()
    return ai

@app.get("/incidents")
def get_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.timestamp.desc()).all()

@app.post("/sos")
def sos(data: SOSRequest, db: Session = Depends(get_db)):
    db.add(SOS(
        name=data.name,
        contact=data.contact,
        lat=data.lat,
        lng=data.lng,
        timestamp=datetime.utcnow()
    ))
    db.commit()
    return {"message": "SOS received"}

@app.post("/action")
def action(data: ActionRequest):
    return {"message": f"{data.type} initiated"}

@app.get("/is-user-in-danger")
def danger(lat: float, lng: float, db: Session = Depends(get_db)):
    incidents = db.query(Incident).all()

    for i in incidents:
        dist = math.sqrt((i.lat - lat)**2 + (i.lng - lng)**2)
        if dist < 0.05 and i.severity >= 7:
            return {"in_danger": True}

    return {"in_danger": False}
