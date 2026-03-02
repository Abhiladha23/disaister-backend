def calculate_risk(severity: int, confidence: float, report_count: int):
    """
    Confidence-weighted risk model.
    """

    weighted_score = severity * confidence * report_count

    if weighted_score >= 20:
        return "CRITICAL"
    elif weighted_score >= 12:
        return "HIGH"
    elif weighted_score >= 6:
        return "MEDIUM"
    else:
        return "LOW"