from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from database import Base
from datetime import datetime

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    message = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    disaster_type = Column(String)
    severity = Column(Float)
    risk_level = Column(String)
    confidence = Column(Float)
    medical_needed = Column(String)
    satellite_verified = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)

class SOS(Base):
    __tablename__ = "sos"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    contact = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
