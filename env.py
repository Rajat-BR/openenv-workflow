"""
env.py — FlowEnv Gym-style Environment
========================================
A simple stateless episode environment for workflow sequencing tasks.

Usage
-----
    env = FlowEnv(seed=42)
    obs = env.reset()
    obs, reward, done, info = env.step(["email_api"])
"""

import random
from tasks import tasks
from grader import grade
from reward import compute_reward


class FlowEnv:
    def __init__(self, seed: int | None = None):
        """
        Parameters
        ----------
        seed : int or None
            Optional RNG seed for reproducible task sampling.
        """
        self._rng = random.Random(seed)
        self.current_task: dict | None = None

    # ── Public API ────────────────────────────────────────────────────────────

    def reset(self) -> str:
        """Sample a new task and return its natural-language request."""
        self.current_task = self._rng.choice(tasks)
        return self.current_task["request"]

    def step(self, action) -> tuple:
        """
        Evaluate the agent's proposed workflow.

        Parameters
        ----------
        action : any — the agent's proposed list of API calls

        Returns
        -------
        obs    : None      (terminal state; no next observation)
        reward : float     (shaped reward from compute_reward)
        done   : bool      (always True — single-step episodes)
        info   : dict      {score, correct_workflow, agent_action}
        """
        if self.current_task is None:
            raise RuntimeError("Call env.reset() before env.step().")

        correct = self.current_task["correct_workflow"]
        score   = grade(correct, action)
        reward  = compute_reward(score)

        info = {
            "score":            score,
            "correct_workflow": correct,
            "agent_action":     action,
        }
        return None, reward, True, info

    # ── Helpers ───────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        task = self.current_task["request"] if self.current_task else "None"
        return f"FlowEnv(current_task={task!r})"
    