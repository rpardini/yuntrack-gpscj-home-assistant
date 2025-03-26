def gpscj_login_and_get_device_position(username: str, password: str, user_id: str, device_id: str):
    """Fake implementation of the function for testing."""
    import random
    from datetime import datetime, timedelta

    return {
        "latitude": 52.37 + random.uniform(-0.01, 0.01),
        "longitude": 4.89 + random.uniform(-0.01, 0.01),
        "battery": random.randint(0, 100),
        "gps_signal": random.randint(-120, 0),
        "lte_signal": random.randint(-120, 0),
        "connection_time": (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat() + "Z",
        "location_time": (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat() + "Z",
        "stoppage_time": (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat() + "Z",
        "stop_minutes": random.randint(0, 60),
    }
