"""
inference.py — Test Runner
===========================
Runs a fixed suite of test actions against every task in the task list
so every combination is evaluated deterministically (no random sampling).

Test categories
---------------
  ✅ Perfect match          — exact correct APIs in exact order
  ⚠️  Partial / wrong order — right APIs but different order or incomplete
  ❌ Invalid / garbage      — unknown API names, wrong types, empty input
  🔀 Mixed                  — some valid + some garbage tokens
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tasks import tasks
from grader import grade, VALID_APIS
from reward import compute_reward

# ── Test action suite ─────────────────────────────────────────────────────────
TEST_ACTIONS = [
    # --- Perfect matches (depend on the current task) ---
    ["email_api"],
    ["calendar_api"],
    ["flight_api"],
    ["calendar_api", "email_api"],
    ["flight_api", "calendar_api", "email_api"],
    ["flight_api", "email_api"],
    ["flight_api", "calendar_api"],

    # --- Wrong order ---
    ["email_api", "calendar_api"],
    ["email_api", "flight_api", "calendar_api"],

    # --- Incomplete (subset of correct) ---
    ["email_api", "calendar_api"],   # missing flight for 3-step task

    # --- Extra valid-but-unneeded APIs ---
    ["email_api", "calendar_api", "flight_api"],  # too many for single-step tasks

    # --- Garbage: unknown API names ---
    ["weather_api"],
    ["sms_api", "push_api"],
    ["cows and hen"],

    # --- Mixed: valid + garbage ---
    ["email_api", "weather_api"],
    ["calendar_api", "unknown_api", "email_api"],

    # --- Duplicate valid APIs ---
    ["email_api", "email_api"],
    ["calendar_api", "calendar_api", "email_api"],

    # --- Non-string elements inside list ---
    [None, "email_api"],
    [123, "calendar_api"],
    ["email_api", {"key": "val"}],

    # --- Completely invalid formats ---
    "just a string",
    42,
    None,
    {},
    [],
]

# ── Helper ────────────────────────────────────────────────────────────────────
def _fmt_action(action) -> str:
    if isinstance(action, list):
        return "[" + ", ".join(repr(a) for a in action) + "]"
    return repr(action)

# ── Run tests for every task ──────────────────────────────────────────────────
def run_all():
    separator = "=" * 72

    for task in tasks:
        correct = task["correct_workflow"]
        print(separator)
        print(f"TASK   : {task['request']}")
        print(f"CORRECT: {correct}")
        print(separator)
        print(f"{'Action':<48} {'Score':>6}  {'Reward':>7}  {'Tag'}")
        print("-" * 72)

        for action in TEST_ACTIONS:
            score  = grade(correct, action)
            reward = compute_reward(score)

            # Tag the result
            if score == 1.0:
                tag = "✅ PERFECT"
            elif score >= 0.8:
                tag = "🟢 GOOD"
            elif score >= 0.5:
                tag = "🟡 PARTIAL"
            elif score > 0.0:
                tag = "🟠 WEAK"
            else:
                tag = "❌ ZERO"

            action_str = _fmt_action(action)
            if len(action_str) > 46:
                action_str = action_str[:43] + "..."

            print(f"{action_str:<48} {score:>6.4f}  {reward:>7.4f}  {tag}")

        print()

    print(separator)
    print("All test cases complete.")
    print(separator)


if __name__ == "__main__":
    run_all()