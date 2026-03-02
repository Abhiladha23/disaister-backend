from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from database import Base
from datetime import datetime


# -----------------------------
# INCIDENT MODEL
# -----------------------------
class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    message = Column(String, nullable=False)

    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)

    disaster_type = Column(String, nullable=False)

    severity = Column(Float, nullable=False)

    risk_level = Column(String, nullable=False)

    confidence = Column(Float, nullable=False)

    medical_needed = Column(String, nullable=False)

    satellite_verified = Column(Boolean, default=False)

    timestamp = Column(DateTime, default=datetime.utcnow)


# -----------------------------
# SOS MODEL
# -----------------------------
class SOS(Base):
    __tablename__ = "sos"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    contact = Column(String, nullable=False)

    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)