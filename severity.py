def calculate_severity_and_priority(issue_type, trust_score):
    """
    Returns:
    - base_severity (int)
    - priority (str)
    """

    issue_type = issue_type.lower()

    # Base severity by issue type
    severity_map = {
        "accident": 90,
        "fire": 95,
        "road_block": 80,
        "pothole": 60,
        "garbage": 50,
        "water_leak": 55
    }

    base_severity = severity_map.get(issue_type, 40)

    # Adjust severity using trust score
    if trust_score < 40:
        base_severity -= 20
    elif trust_score < 60:
        base_severity -= 10

    # Clamp severity between 0–100
    base_severity = max(0, min(100, base_severity))

    # Determine priority
    if base_severity >= 85:
        priority = "CRITICAL"
    elif base_severity >= 70:
        priority = "HIGH"
    elif base_severity >= 50:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return base_severity, priority
