from datetime import datetime

active_sos_requests = []

def create_sos(lat: float, lng: float, message: str):
    sos = {
        "lat": lat,
        "lng": lng,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "priority": "MAX",
        "status": "PENDING"
    }

    active_sos_requests.append(sos)
    return sos

def get_all_sos():
    return active_sos_requests