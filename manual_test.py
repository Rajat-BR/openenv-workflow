from environment import APIWorkflowEnv , Action


env = APIWorkflowEnv()

def run_test(name, action):
    print(f"\n=== {name} ===")
    env.reset()
    try:
        obs, reward, done, info = env.step(Action(**action))
        print("Reward:", reward)
        print("Done:", done)
        print("Info:", info)
    except Exception as e:
        print("Handled Error:", e)
        print("Reward: 0.0")
    

run_test("Perfect EASY", {
    "workflow": [
        {"api": "weather_api", "params": {"city": "Paris"}}
    ]
})

run_test("Missing API", {
    "workflow": [
        {"api": "flight_api", "params": {"from_city": "NY", "to_city": "Paris"}}
    ]
})

run_test("Wrong Order", {
    "workflow": [
        {"api": "email_api", "params": {}},
        {"api": "flight_api", "params": {}}
    ]
})

run_test("Extra API", {
    "workflow": [
        {"api": "flight_api", "params": {}},
        {"api": "email_api", "params": {}},
        {"api": "weather_api", "params": {}}
    ]
})

run_test("Invalid API", {
    "workflow": [
        {"api": "random_api", "params": {}}
    ]
})

run_test("Wrong Params", {
    "workflow": [
        {"api": "flight_api", "params": {"from_city": "NY"}}
    ]
})

run_test("Garbage Input", {
    "workflow": "nonsense"
})

run_test("Empty Workflow", {
    "workflow": []
})