"""
tasks.py — Task Definitions
============================
Each task has:
  request          : natural-language description shown to the agent
  correct_workflow : ordered list of API calls that solve the request
"""

tasks = [
    {
        "request": "Send an email",
        "correct_workflow": ["email_api"]
    },
    {
        "request": "Schedule a meeting and send an email",
        "correct_workflow": ["calendar_api", "email_api"]
    },
    {
        "request": "Book a flight, schedule a meeting, and send a confirmation email",
        "correct_workflow": ["flight_api", "calendar_api", "email_api"]
    },
    {
        "request": "Book a flight and send an email",
        "correct_workflow": ["flight_api", "email_api"]
    },
    {
        "request": "Schedule a meeting",
        "correct_workflow": ["calendar_api"]
    },
    {
        "request": "Book a flight",
        "correct_workflow": ["flight_api"]
    },
    {
        "request": "Book a flight and schedule a follow-up meeting",
        "correct_workflow": ["flight_api", "calendar_api"]
    },
]