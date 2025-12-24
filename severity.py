def get_base_severity(issue_type):
    """
    Returns base severity score based on issue type
    """

    issue_severity_map = {
        "accident": 90,
        "road_block": 80,
        "pothole": 60,
        "garbage": 40,
        "streetlight": 30,
        "other": 20
    }

    return issue_severity_map.get(issue_type, 20)
