"""
tasks.py — Exactly 3 task definitions: easy, medium, hard.
Uses only the 4 allowed APIs:
    flight_api, calendar_api, email_api, database_api
"""

from typing import List, Dict

easy_task: Dict = {
    "id": "easy",
    "difficulty": "easy",
    "description": "Schedule a meeting.",
    "user_input": "Schedule a meeting on 2026-04-08 at 10:00.",
    "expected_workflow": [
        {"api": "calendar_api", "params": {"date": "2026-04-08", "time": "10:00"}},
    ],
    "required_apis_in_order": ["calendar_api"],
    "required_param_keys": {"calendar_api": ["date", "time"]},
}

medium_task: Dict = {
    "id": "medium",
    "difficulty": "medium",
    "description": "Book a flight and send an email. Two steps, ordered dependency.",
    "user_input": (
        "Book a flight from New York to London "
        "and email john@example.com."
    ),
    "expected_workflow": [
        {"api": "flight_api", "params": {"from_city": "New York", "to_city": "London"}},
        {"api": "email_api",  "params": {"to": "john@example.com"}},
    ],
    "required_apis_in_order": ["flight_api", "email_api"],
    "required_param_keys": {
        "flight_api": ["from_city", "to_city"],
        "email_api":  ["to"],
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
        "Book a flight from NYC to Paris, schedule a meeting on 2026-05-01 at 10:00, "
        "store the destination Paris and meeting on 2026-05-01 at 10:00 in the database, "
        "and email alice@company.com the full plan."
    ),
    "expected_workflow": [
        {"api": "flight_api",   "params": {"from_city": "NYC", "to_city": "Paris"}},
        {"api": "calendar_api", "params": {"date": "2026-05-01", "time": "10:00"}},
        {"api": "database_api", "params": {
            "data": {
                "destination": "Paris",
                "date": "2026-05-01",
                "time": "10:00"
            }
        }},
        {"api": "email_api", "params": {"to": "alice@company.com"}},
    ],
    "required_apis_in_order": ["flight_api", "calendar_api", "database_api", "email_api"],
    "required_param_keys": {
            "flight_api": ["from_city", "to_city"],
            "calendar_api": ["date", "time"],
            "database_api": ["data"],
            "email_api": ["to"]
        }

}

TASKS: List[Dict] = [easy_task, medium_task, hard_task]