from pydantic import BaseModel

class IncidentCreate(BaseModel):
    message: str
    lat: float
    lng: float


class SOSCreate(BaseModel):
    name: str
    contact: str
    lat: float
    lng: float