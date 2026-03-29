"""
apis.py — Exactly 5 simulated APIs.
Each takes (params: dict, state: dict) -> dict.
No real API calls. No randomness. Fully deterministic.
"""

from typing import Dict


def _ok(data: Dict) -> Dict:
    return {"status": "success", **data}

def _fail(reason: str) -> Dict:
    return {"status": "error", "reason": reason}


def weather_api(params: Dict, state: Dict) -> Dict:
    city = params.get("city", "")
    if not city or not isinstance(city, str):
        return _fail("Missing or invalid 'city' parameter")
    weather_map = {
        "paris":    {"condition": "Sunny",  "temp_c": 18, "humidity": 60},
        "london":   {"condition": "Rainy",  "temp_c": 11, "humidity": 85},
        "new york": {"condition": "Cloudy", "temp_c": 15, "humidity": 72},
        "tokyo":    {"condition": "Clear",  "temp_c": 22, "humidity": 55},
        "nyc":      {"condition": "Cloudy", "temp_c": 15, "humidity": 72},
    }
    weather = weather_map.get(city.lower(), {"condition": "Clear", "temp_c": 20, "humidity": 65})
    return _ok({"city": city, **weather})


def flight_api(params: Dict, state: Dict) -> Dict:
    from_city = params.get("from_city", "")
    to_city   = params.get("to_city", "")
    if not from_city or not isinstance(from_city, str):
        return _fail("Missing 'from_city'")
    if not to_city or not isinstance(to_city, str):
        return _fail("Missing 'to_city'")
    if from_city.lower() == to_city.lower():
        return _fail("'from_city' and 'to_city' cannot be the same")
    booking_id = f"FL-{abs(hash(from_city + to_city)) % 9000 + 1000}"
    state["flight_booked"] = True
    return _ok({"booking_id": booking_id, "from": from_city, "to": to_city})


def calendar_api(params: Dict, state: Dict) -> Dict:
    date = params.get("date", "")
    time = params.get("time", "")
    if not date or not isinstance(date, str):
        return _fail("Missing 'date'")
    if not time or not isinstance(time, str):
        return _fail("Missing 'time'")
    event_id = f"CAL-{abs(hash(date + time)) % 9000 + 1000}"
    state["meeting_scheduled"] = True
    return _ok({"event_id": event_id, "date": date, "time": time})


def email_api(params: Dict, state: Dict) -> Dict:
    to      = params.get("to", "")
    subject = params.get("subject", "")
    if not to or not isinstance(to, str):
        return _fail("Missing 'to'")
    if not subject or not isinstance(subject, str):
        return _fail("Missing 'subject'")
    if len(state.get("history", [])) == 0:
        return _fail("Cannot send email as the very first action")
    msg_id = f"EM-{abs(hash(to + subject)) % 9000 + 1000}"
    state["email_sent"] = True
    return _ok({"message_id": msg_id, "to": to, "subject": subject})


def database_api(params: Dict, state: Dict) -> Dict:
    data = params.get("data")
    if data is None:
        return _fail("Missing 'data'")
    if not isinstance(data, dict):
        return _fail("'data' must be a dict")
    state["data_stored"] = True
    return _ok({"stored": True, "keys": list(data.keys())})


API_REGISTRY = {
    "weather_api":  weather_api,
    "flight_api":   flight_api,
    "calendar_api": calendar_api,
    "email_api":    email_api,
    "database_api": database_api,
}

AVAILABLE_APIS = list(API_REGISTRY.keys())