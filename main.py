from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Incident, SOS, Action, MonitoredLocation
from gemini_service import classify_incident
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math

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


class ActionRequest(BaseModel):
    type: str
    lat: float
    lng: float


class MonitorRequest(BaseModel):
    name: str
    lat: float
    lng: float


@app.get("/")
def root():
    return {"status": "Backend running"}


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


@app.get("/incidents")
def get_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.timestamp.desc()).all()


@app.post("/sos")
def trigger_sos(data: SOSRequest, db: Session = Depends(get_db)):
    sos = SOS(**data.dict(), timestamp=datetime.utcnow())
    db.add(sos)
    db.commit()
    return {"message": "SOS recorded"}


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
    return {"message": f"{data.type} executed"}


@app.post("/monitor")
def add_monitor(data: MonitorRequest, db: Session = Depends(get_db)):
    location = MonitoredLocation(**data.dict(), timestamp=datetime.utcnow())
    db.add(location)
    db.commit()
    return {"message": "Location added"}


@app.get("/monitor")
def get_monitors(db: Session = Depends(get_db)):
    monitors = db.query(MonitoredLocation).all()
    incidents = db.query(Incident).all()

    result = []

    for m in monitors:
        risk = "LOW"
        for i in incidents:
            distance = math.sqrt((i.lat - m.lat)**2 + (i.lng - m.lng)**2)
            if distance < 0.1 and i.severity >= 7:
                risk = "HIGH"

        result.append({
            "id": m.id,
            "name": m.name,
            "lat": m.lat,
            "lng": m.lng,
            "risk": risk
        })

    return result


@app.delete("/clear")
def clear(db: Session = Depends(get_db)):
    db.query(Incident).delete()
    db.query(SOS).delete()
    db.query(Action).delete()
    db.query(MonitoredLocation).delete()
    db.commit()
    return {"message": "Database cleared"}
