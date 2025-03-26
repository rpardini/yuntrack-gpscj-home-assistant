def gpscj_login_and_get_device_position(username: str, password: str, user_id: str, device_id: str):
    """Fake implementation of the function for testing."""
    import random
    return {
        "latitude": 52.37 + random.uniform(-0.01, 0.01),
        "longitude": 4.89 + random.uniform(-0.01, 0.01),
    }
