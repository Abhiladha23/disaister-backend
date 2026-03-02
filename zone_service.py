active_zones = []

def create_zone(incident_id, lat, lng, severity):
    radius = severity * 500  # scalable impact radius

    zone = {
        "incident_id": incident_id,
        "center_lat": lat,
        "center_lng": lng,
        "radius": radius,
        "severity": severity
    }

    active_zones.append(zone)
    return zone

def get_zones():
    return active_zones