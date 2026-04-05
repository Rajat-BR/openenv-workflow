"""
app.py — HTTP service for OpenEnv: API Workflow Orchestration.
Exposes reset(), step(), state() as REST endpoints.
Runs on port 7860 for HuggingFace Spaces compatibility.
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from environment import APIWorkflowEnv, Action
from tasks import TASKS

app = FastAPI(
    title="FlowForge: API Workflow Orchestration",
    description="An OpenEnv environment where agents must orchestrate correct API workflows.",
    version="1.0.0",
)

env = APIWorkflowEnv()

SAFE_ERROR_RESPONSE = {
    "observation": {
        "message": "bad request",
        "task_description": "",
        "available_apis": [],
        "step_count": 0,
    },
    "reward": {"score": 0.0},
    "done": False,
    "info": {"error": "malformed input"},
}


@app.get("/")
def root():
    return {
        "status": "ok",
        "environment": "APIWorkflowEnv",
        "version": "1.0.0",
        "endpoints": ["/reset", "/step", "/state", "/tasks", "/health"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reset")
def reset():
    obs = env.reset()
    return obs.model_dump()


@app.post("/step")
async def step(request: Request):
    # Parse body manually so malformed JSON / wrong types never cause a 422/500
    try:
        body = await request.json()
    except Exception:
        body = {}

    # Coerce workflow to a list regardless of what arrives
    raw_workflow = body.get("workflow", []) if isinstance(body, dict) else []
    if not isinstance(raw_workflow, list):
        raw_workflow = []

    action = Action(workflow=raw_workflow)

    try:
        obs, reward, done, info = env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward":      reward.model_dump(),
            "done":        done,
            "info":        info,
        }
    except Exception as e:
        err = dict(SAFE_ERROR_RESPONSE)
        err["info"] = {"error": str(e)}
        return JSONResponse(content=err)


@app.get("/state")
def state():
    return env.state()


@app.get("/tasks")
def get_tasks():
    return [
        {
            "id":          t["id"],
            "difficulty":  t["difficulty"],
            "description": t["description"],
            "user_input":  t["user_input"],
        }
        for t in TASKS
    ]

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()