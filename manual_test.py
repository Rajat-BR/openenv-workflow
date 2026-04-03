from environment import APIWorkflowEnv, Action

env = APIWorkflowEnv()


def run_test(name, action, task_index=0):
    print(f"\n=== {name} ===")
    env.reset()
    env._task_index = task_index  # 🔥 critical fix

    try:
        obs, reward, done, info = env.step(Action(**action))
        print("Reward:", reward.score)
        print("Done:", done)
        print("Info:", info)
    except Exception as e:
        print("Handled Error:", e)
        print("Reward: 0.0")


# ───────────────── EASY (task_index = 0) ─────────────────

run_test("Perfect EASY", {
    "workflow": [
        {"api": "calendar_api", "params": {"date": "2026-04-08", "time": "10:00"}}
    ]
}, task_index=0)

run_test("Missing API (EASY)", {
    "workflow": []
}, task_index=0)

run_test("Wrong Order (EASY)", {
    "workflow": [
        {"api": "email_api", "params": {"to": "john@example.com"}},
        {"api": "flight_api", "params": {"from_city": "NY", "to_city": "Paris"}}
    ]
}, task_index=0)

run_test("Extra API (EASY)", {
    "workflow": [
        {"api": "calendar_api", "params": {"date": "2026-04-08", "time": "10:00"}},
        {"api": "flight_api", "params": {"from_city": "NY", "to_city": "Paris"}}
    ]
}, task_index=0)

run_test("Invalid API (EASY)", {
    "workflow": [
        {"api": "random_api", "params": {}}
    ]
}, task_index=0)

run_test("Wrong Params (EASY)", {
    "workflow": [
        {"api": "calendar_api", "params": {"date": "2026-04-08"}}  # missing time
    ]
}, task_index=0)


# ───────────────── MEDIUM (task_index = 1) ─────────────────

run_test("Perfect MEDIUM", {
    "workflow": [
        {"api": "flight_api", "params": {"from_city": "NYC", "to_city": "London"}},
        {"api": "email_api", "params": {"to": "john@example.com"}}
    ]
}, task_index=1)

run_test("Medium Wrong Order", {
    "workflow": [
        {"api": "email_api", "params": {"to": "john@example.com"}},
        {"api": "flight_api", "params": {"from_city": "New York", "to_city": "London"}}
    ]
}, task_index=1)

run_test("Medium Missing Email", {
    "workflow": [
        {"api": "flight_api", "params": {"from_city": "New York", "to_city": "London"}}
    ]
}, task_index=1)

run_test("Medium Extra API", {
    "workflow": [
        {"api": "flight_api", "params": {"from_city": "New York", "to_city": "London"}},
        {"api": "email_api", "params": {"to": "john@example.com"}},
        {"api": "calendar_api", "params": {"date": "2026-04-08", "time": "10:00"}}
    ]
}, task_index=1)


# ───────────────── HARD (task_index = 2) ─────────────────

run_test("Perfect HARD", {
    "workflow": [
        {"api": "flight_api", "params": {"from_city": "NYC", "to_city": "Paris"}},
        {"api": "calendar_api", "params": {"date": "2026-05-01", "time": "10:00"}},
        {"api": "database_api", "params": {
            "data": {
                "destination": "Paris",
                "date": "2026-05-01",
                "time": "10:00"
            }
        }},
        {"api": "email_api", "params": {"to": "alice@company.com"}}
    ]
}, task_index=2)

run_test("Hard Wrong Order", {
    "workflow": [
        {"api": "email_api", "params": {"to": "alice@company.com"}},
        {"api": "flight_api", "params": {"from_city": "NYC", "to_city": "Paris"}},
        {"api": "calendar_api", "params": {"date": "2026-05-01", "time": "10:00"}},
        {"api": "database_api", "params": {
            "data": {
                "destination": "Paris",
                "date": "2026-05-01",
                "time": "10:00"
            }
        }}
    ]
}, task_index=2)

run_test("Hard Missing Step", {
    "workflow": [
        {"api": "flight_api", "params": {"from_city": "NYC", "to_city": "Paris"}},
        {"api": "calendar_api", "params": {"date": "2026-05-01", "time": "10:00"}},
        {"api": "email_api", "params": {"to": "alice@company.com"}}
    ]
}, task_index=2)

run_test("Hard Wrong DB Params", {
    "workflow": [
        {"api": "flight_api", "params": {"from_city": "NYC", "to_city": "Paris"}},
        {"api": "calendar_api", "params": {"date": "2026-05-01", "time": "10:00"}},
        {"api": "database_api", "params": {
            "data": {
                "destination": "Paris"  # missing date/time
            }
        }},
        {"api": "email_api", "params": {"to": "alice@company.com"}}
    ]
}, task_index=2)

print("\n=== Duplicate API Test ===")
workflow = [
    {"api": "flight_api", "params": {"from_city": "NYC", "to_city": "Paris"}},
    {"api": "flight_api", "params": {"from_city": "NYC", "to_city": "Paris"}},
]
obs, reward, done, info = env.step(Action(workflow=workflow))
print("Reward:", reward)

# ───────────────── EDGE CASES ─────────────────

run_test("Garbage Input", {
    "workflow": "nonsense"
})

run_test("Empty Workflow", {
    "workflow": []
})