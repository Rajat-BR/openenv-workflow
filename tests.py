"""
tests.py — Internal test suite for OpenEnv: API Workflow Orchestration.

Run with:  python tests.py

Tests:
  - perfect workflow → ~1.0
  - missing step → lower score
  - wrong order → penalized
  - invalid API → penalized
  - empty input → safe, score 0
  - garbage input → safe handling
  - state management after reset
  - done-guard after episode ends
"""

import sys


def run_tests():
    from environment import APIWorkflowEnv, Action
    from grader import grade
    from tasks import easy_task, medium_task, hard_task

    passed = 0
    failed = 0

    def check(name, condition, got=None):
        nonlocal passed, failed
        if condition:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name}  [got: {got}]")
            failed += 1

    print("\n── Grader Unit Tests ──────────────────────────────────────────")

    # Perfect workflows → 1.0
    perfect_easy = [{"api": "weather_api", "params": {"city": "Paris"}}]
    check("Easy perfect → 1.0", grade(perfect_easy, easy_task) == 1.0,
          grade(perfect_easy, easy_task))

    perfect_medium = [
        {"api": "flight_api",  "params": {"from_city": "New York", "to_city": "London", "passenger": "John"}},
        {"api": "email_api",   "params": {"to": "john@example.com", "subject": "Flight Confirmation"}},
    ]
    check("Medium perfect → 1.0", grade(perfect_medium, medium_task) == 1.0,
          grade(perfect_medium, medium_task))

    perfect_hard = [
        {"api": "flight_api",   "params": {"from_city": "New York", "to_city": "Paris", "passenger": "Alice"}},
        {"api": "hotel_api",    "params": {"hotel": "Le Grand", "guest": "Alice", "city": "Paris"}},
        {"api": "calendar_api", "params": {"title": "Business Trip to Paris", "time": "Monday 9am"}},
        {"api": "invoice_api",  "params": {"amount": 2500, "client": "Alice"}},
        {"api": "payment_api",  "params": {"amount": 2500}},
        {"api": "email_api",    "params": {"to": "alice@company.com", "subject": "Trip Details"}},
    ]
    check("Hard perfect → 1.0", grade(perfect_hard, hard_task) == 1.0,
          grade(perfect_hard, hard_task))

    # Missing step → lower score
    missing_step = [{"api": "flight_api", "params": {"from_city": "New York", "to_city": "London"}}]
    s = grade(missing_step, medium_task)
    check("Medium missing email → score < 1.0", s < 1.0, s)
    check("Medium missing email → score > 0.0", s > 0.0, s)

    # Wrong order → penalized vs correct order
    wrong_order = [
        {"api": "email_api",  "params": {"to": "john@example.com", "subject": "Confirmation"}},
        {"api": "flight_api", "params": {"from_city": "New York", "to_city": "London"}},
    ]
    correct_order_score = grade(perfect_medium, medium_task)
    wrong_order_score   = grade(wrong_order, medium_task)
    check("Wrong order scores less than correct order",
          wrong_order_score < correct_order_score,
          f"correct={correct_order_score}, wrong={wrong_order_score}")

    # Invalid API → penalized
    invalid_api = [
        {"api": "fake_api",   "params": {}},
        {"api": "flight_api", "params": {"from_city": "New York", "to_city": "London"}},
    ]
    s_invalid = grade(invalid_api, medium_task)
    s_no_invalid = grade([{"api": "flight_api", "params": {"from_city": "New York", "to_city": "London"}}], medium_task)
    check("Invalid API penalizes score", s_invalid <= s_no_invalid,
          f"with_invalid={s_invalid}, without={s_no_invalid}")

    # Empty input → 0.0, no crash
    check("Empty workflow → 0.0", grade([], medium_task) == 0.0)
    check("None-like workflow → 0.0", grade(None, medium_task) == 0.0)  # type: ignore

    # Garbage input → safe, score in [0,1]
    garbage = [{"api": 123, "params": "bad"}, None, "string_step"]  # type: ignore
    s_garb = grade(garbage, medium_task)
    check("Garbage input → score in [0,1]", 0.0 <= s_garb <= 1.0, s_garb)

    # Scores always in [0, 1]
    for wf in [perfect_easy, perfect_medium, perfect_hard, missing_step, wrong_order, garbage]:
        s = grade(wf, hard_task)
        check(f"Score in [0,1] for workflow len={len(wf)}", 0.0 <= s <= 1.0, s)

    print("\n── Environment Tests ──────────────────────────────────────────")

    env = APIWorkflowEnv()
    obs = env.reset()
    check("reset() returns Observation", hasattr(obs, "message"))
    check("reset() message contains EASY", "EASY" in obs.message, obs.message)
    check("reset() task_description non-empty", len(obs.task_description) > 0)

    s = env.state()
    check("state() has task_index=0", s["task_index"] == 0, s["task_index"])
    check("state() has done=False", s["done"] is False)
    check("state() has flight_booked=False", s["flight_booked"] is False)

    # Step with perfect easy workflow
    action_easy = Action(workflow=perfect_easy)
    obs2, reward2, done2, info2 = env.step(action_easy)
    check("step() returns Observation", hasattr(obs2, "message"))
    check("step() returns Reward with score", hasattr(reward2, "score"))
    check("step() easy perfect score == 1.0", reward2.score == 1.0, reward2.score)
    check("step() done=False after task 1", done2 is False)

    # Step with perfect medium workflow
    action_medium = Action(workflow=perfect_medium)
    obs3, reward3, done3, info3 = env.step(action_medium)
    check("step() medium perfect score == 1.0", reward3.score == 1.0, reward3.score)
    check("step() done=False after task 2", done3 is False)

    # Step with perfect hard workflow
    action_hard = Action(workflow=perfect_hard)
    obs4, reward4, done4, info4 = env.step(action_hard)
    check("step() hard perfect score == 1.0", reward4.score == 1.0, reward4.score)
    check("step() done=True after task 3", done4 is True)
    check("final obs message = 'All tasks complete.'", "All tasks" in obs4.message, obs4.message)

    # done-guard: extra step after finish
    obs5, reward5, done5, _ = env.step(Action(workflow=[]))
    check("step() after done returns score=0", reward5.score == 0.0)
    check("step() after done still done=True", done5 is True)

    # reset clears state
    env.reset()
    s2 = env.state()
    check("state after reset has task_index=0", s2["task_index"] == 0)
    check("state after reset has done=False", s2["done"] is False)
    check("state after reset history_length=0", s2["history_length"] == 0)

    # state() reflects flight_booked after flight_api runs
    env2 = APIWorkflowEnv()
    env2.reset()
    env2.step(Action(workflow=[
        {"api": "weather_api", "params": {"city": "Paris"}}
    ]))  # easy task done
    env2.step(Action(workflow=[
        {"api": "flight_api", "params": {"from_city": "New York", "to_city": "London", "passenger": "John"}},
        {"api": "email_api",  "params": {"to": "x@x.com", "subject": "hi"}},
    ]))  # medium task — flight_api runs → sets flight_booked
    # After medium task, state resets for hard task — but history preserved
    s3 = env2.state()
    check("After medium step, history_length > 0", s3["history_length"] > 0, s3["history_length"])

    # Edge: malformed action step
    env3 = APIWorkflowEnv()
    env3.reset()
    try:
        obs_e, rew_e, _, _ = env3.step(Action(workflow=[None, 42, {"api": "weather_api", "params": {"city": "Paris"}}]))  # type: ignore
        check("Malformed steps in workflow → no crash, score in [0,1]", 0.0 <= rew_e.score <= 1.0, rew_e.score)
    except Exception as ex:
        check("Malformed steps in workflow → no crash", False, str(ex))

    print("\n── API Unit Tests ─────────────────────────────────────────────")

    from apis import (weather_api, flight_api, hotel_api, calendar_api,
                      crm_api, invoice_api, payment_api, email_api)

    st = lambda: {"flight_booked": False, "hotel_booked": False, "invoice_created": False,
                  "meeting_scheduled": False, "history": []}

    # weather_api
    r = weather_api({"city": "Paris"}, st())
    check("weather_api valid → success", r["status"] == "success", r)
    r = weather_api({}, st())
    check("weather_api missing city → error", r["status"] == "error", r)

    # flight_api
    r = flight_api({"from_city": "NYC", "to_city": "London", "passenger": "Alice"}, st())
    check("flight_api valid → success", r["status"] == "success", r)
    r = flight_api({"from_city": "NYC", "to_city": "NYC"}, st())
    check("flight_api same city → error", r["status"] == "error", r)
    r = flight_api({"from_city": "NYC"}, st())
    check("flight_api missing to_city → error", r["status"] == "error", r)

    # calendar_api — travel title without flight booked
    s_cal = st()
    r = calendar_api({"title": "Business Trip", "time": "Monday"}, s_cal)
    check("calendar_api travel without flight → error", r["status"] == "error", r)
    s_cal["flight_booked"] = True
    r = calendar_api({"title": "Business Trip", "time": "Monday"}, s_cal)
    check("calendar_api travel with flight → success", r["status"] == "success", r)

    # invoice_api — bad amount
    r = invoice_api({"amount": -100, "client": "x"}, st())
    check("invoice_api negative amount → error", r["status"] == "error", r)
    r = invoice_api({"amount": "bad"}, st())
    check("invoice_api non-numeric amount → error", r["status"] == "error", r)

    # payment_api — without invoice
    r = payment_api({"amount": 100}, st())
    check("payment_api without invoice → error", r["status"] == "error", r)
    s_pay = st()
    s_pay["invoice_created"] = True
    r = payment_api({"amount": 100}, s_pay)
    check("payment_api with invoice → success", r["status"] == "success", r)

    # email_api — first action (empty history)
    r = email_api({"to": "a@b.com", "subject": "hi"}, st())
    check("email_api first action → error", r["status"] == "error", r)
    s_em = st()
    s_em["history"] = [{"api": "flight_api"}]
    r = email_api({"to": "a@b.com", "subject": "hi"}, s_em)
    check("email_api after prior step → success", r["status"] == "success", r)

    # ── Summary ──────────────────────────────────────────────────────────────
    total = passed + failed
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} passed", "✓" if failed == 0 else "✗")
    if failed:
        print(f"FAILED: {failed} test(s)")
    print('='*60)
    return failed == 0


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
