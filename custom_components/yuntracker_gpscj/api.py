def gpscj_login_and_get_device_position(username: str, password: str, user_id: str, device_id: str):
    """Fake implementation of the function for testing."""
    import random
    from datetime import datetime, timedelta

    return {
        "baiduLat": -23.793659 + random.uniform(-0.01, 0.01),
        "baiduLng": -45.55398 + random.uniform(-0.01, 0.01),
        "battery": random.randint(0, 100),
        "carNum": "",
        "carStatus": "",
        "course": "0",
        "dataContext": "-0---39-16-0-12-0-4",
        "dataType": "3",
        "deviceUtcDate": (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat() + "Z",
        "distance": random.uniform(0, 20),
        "groupID": -1,
        "gzms": "",
        "icon": "1",
        "id": 2017806,
        "isStop": 1,
        "latitude": -23.793659 + random.uniform(-0.01, 0.01),
        "locationID": "1",
        "longitude": -45.55398 + random.uniform(-0.01, 0.01),
        "model": "198",
        "modelName": "CJPSN",
        "name": "CJPSN-00884",
        "ofl": "0",
        "serverUtcDate": (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat() + "Z",
        "signal_4g": random.randint(-120, 0),
        "signal_gps": random.randint(-120, 0),
        "sn": "2240000884",
        "speed": "0.00",
        "speedLimit": "0.00",
        "state": 1,
        "status": "Stop",
        "stopTime": (datetime.now() - timedelta(days=random.randint(0, 2))).isoformat() + "Z",
        "stopTimeMinute": random.randint(0, 60),
    }
