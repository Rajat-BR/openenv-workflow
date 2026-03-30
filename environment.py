"""
environment.py — OpenEnv-compliant environment: APIWorkflowEnv.

Implements:
  reset()       → Observation
  step(action)  → (Observation, Reward, bool, dict)
  state()       → dict

State tracks:
  - which APIs have succeeded
  - full execution history
  - current task index
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Tuple

from apis import API_REGISTRY, AVAILABLE_APIS
from grader import grade
from tasks import TASKS


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class Action(BaseModel):
    workflow: List[Dict]

class Observation(BaseModel):
    message: str
    task_description: str
    available_apis: List[str]
    step_count: int

class Reward(BaseModel):
    score: float


# ─── Initial State Factory ───────────────────────────────────────────────────

def _fresh_state() -> Dict[str, Any]:
    """Return a clean state dict for a new episode."""
    return {
        "flight_booked":       False,
        "meeting_scheduled":   False,
        "email_sent":          False,
        "data_stored":         False,
        "history": [],
    }


# ─── Environment ──────────────────────────────────────────────────────────────

class APIWorkflowEnv:
    """
    OpenEnv environment: API Workflow Orchestration.

    An agent receives a natural-language task and must submit a structured
    workflow (ordered list of API calls with parameters). The environment
    executes each API, tracks state, and grades the submission.
    """

    def __init__(self):
        self._task_index: int = 0
        self._step_count: int = 0
        self._done: bool = False
        self._last_score: float = 0.0
        self._env_state: Dict[str, Any] = _fresh_state()

    # ── Public Interface ──────────────────────────────────────────────────────

    def reset(self) -> Observation:
        """Reset environment to initial state. Returns first task observation."""
        self._task_index = 0
        self._step_count = 0
        self._done = False
        self._last_score = 0.0
        self._env_state = _fresh_state()
        return self._make_observation()
    

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict]:
        """
        Submit a workflow for the current task.
        Returns (observation, reward, done, info).
        Safe against invalid inputs.
        """
        if self._done:
            obs = Observation(
                message="Episode complete. Call reset() to start a new episode.",
                task_description="",
                available_apis=AVAILABLE_APIS,
                step_count=self._step_count,
            )
            return obs, Reward(score=0.0), True, {"info": "already_done"}


        # Handle invalid input safely
        if not isinstance(action, Action):
            try:
                action = Action(**action)
            except Exception:
                return (
                    self._make_observation(),
                    Reward(score=0.0),
                    False,  # ❗ NOT True
                    {"error": "invalid action format"}
                )

        current_task = TASKS[self._task_index]
        raw_workflow = action.workflow if isinstance(action.workflow, list) else []

        # Execute each API call cumulatively
        api_results = []
        for step in raw_workflow:
            if not isinstance(step, dict):
                api_results.append({"api": "?", "result": {"status": "error", "reason": "malformed step"}})
                continue
            api_name = step.get("api", "")
            params   = step.get("params", {})
            if not isinstance(params, dict):
                params = {}

            fn = API_REGISTRY.get(api_name)
            if fn is None:
                result = {"status": "error", "reason": f"unknown api '{api_name}'"}
            else:
                try:
                    result = fn(params, self._env_state)
                except Exception as e:
                    result = {"status": "error", "reason": str(e)}

            api_results.append({"api": api_name, "result": result})
            self._env_state["history"].append({"api": api_name, "params": params, "result": result})

        score = grade(current_task["expected_workflow"], raw_workflow)
        self._last_score = score
        self._step_count += 1

        completed_task = current_task
        self._task_index += 1
        done = self._task_index >= len(TASKS)
        self._done = done

        # Reset flags for next task but preserve history
        if not done:
            flags = _fresh_state()
            flags["history"] = self._env_state["history"]
            self._env_state = flags

        obs    = self._make_observation()
        reward = Reward(score=score)
        info   = {
            "task_id":     completed_task["id"],
            "difficulty":  completed_task["difficulty"],
            "score":       score,
            "api_results": api_results,
        }

        return obs, reward, done, info

    def state(self) -> Dict:
        """Return current environment state snapshot."""
        task = TASKS[self._task_index] if not self._done else None
        return {
            "task_index":          self._task_index,
            "task_id":             task["id"] if task else None,
            "difficulty":          task["difficulty"] if task else None,
            "step_count":          self._step_count,
            "done":                self._done,
            "last_score":          self._last_score,
            "available_apis":      AVAILABLE_APIS,
            "flight_booked":       self._env_state["flight_booked"],
            "meeting_scheduled":   self._env_state["meeting_scheduled"],
            "email_sent":          self._env_state["email_sent"],
            "data_stored":         self._env_state["data_stored"],
            "history_length":      len(self._env_state["history"]),
        }

    def _make_observation(self) -> Observation:
        if self._done:
            return Observation(
                message="All tasks complete.",
                task_description="",
                available_apis=AVAILABLE_APIS,
                step_count=self._step_count,
            )
        task = TASKS[self._task_index]
        return Observation(
            message=f"Task {self._task_index + 1}/{len(TASKS)}: {task['difficulty'].upper()}",
            task_description=task["user_input"],
            available_apis=AVAILABLE_APIS,
            step_count=self._step_count,
        )
