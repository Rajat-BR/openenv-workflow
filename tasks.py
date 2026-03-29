"""
tasks.py — Exactly 3 task definitions: easy, medium, hard.
Uses only the 5 allowed APIs:
  weather_api, flight_api, calendar_api, email_api, database_api
"""

from typing import List, Dict

easy_task: Dict = {
    "id": "easy",
    "difficulty": "easy",
    "description": "Check the weather for a city. Single API, one parameter.",
    "user_input": "What is the weather in Paris?",
    "expected_workflow": [
        {"api": "weather_api", "params": {"city": "Paris"}},
    ],
    "required_apis_in_order": ["weather_api"],
    "required_param_keys": {"weather_api": ["city"]},
}

medium_task: Dict = {
    "id": "medium",
    "difficulty": "medium",
    "description": "Book a flight then email the confirmation. Two steps, ordered dependency.",
    "user_input": (
        "Book a flight from New York to London "
        "and email john@example.com the confirmation."
    ),
    "expected_workflow": [
        {"api": "flight_api", "params": {"from_city": "New York", "to_city": "London"}},
        {"api": "email_api",  "params": {"to": "john@example.com", "subject": "Flight Confirmation"}},
    ],
    "required_apis_in_order": ["flight_api", "email_api"],
    "required_param_keys": {
        "flight_api": ["from_city", "to_city"],
        "email_api":  ["to", "subject"],
    },
}

hard_task: Dict = {
    "id": "hard",
    "difficulty": "hard",
    "description": (
        "Book a flight, schedule a meeting, store trip details in the database, "
        "then email the full plan. Four steps with strict ordering."
    ),
    "user_input": (
        "Book a flight from NYC to Paris, schedule a meeting on 2024-12-01 at 10:00, "
        "store the trip details in the database, "
        "and email alice@company.com the full plan."
    ),
    "expected_workflow": [
        {"api": "flight_api",   "params": {"from_city": "NYC", "to_city": "Paris"}},
        {"api": "calendar_api", "params": {"date": "2024-12-01", "time": "10:00"}},
        {"api": "database_api", "params": {"data": {"trip": "Paris", "meeting": "10am"}}},
        {"api": "email_api",    "params": {"to": "alice@company.com", "subject": "Trip Plan"}},
    ],
    "required_apis_in_order": ["flight_api", "calendar_api", "database_api", "email_api"],
    "required_param_keys": {
        "flight_api":   ["from_city", "to_city"],
        "calendar_api": ["date", "time"],
        "database_api": ["data"],
        "email_api":    ["to", "subject"],
    },
}

TASKS: List[Dict] = [easy_task, medium_task, hard_task]