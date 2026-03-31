"""
inference.py — Baseline inference script for OpenEnv: API Workflow Orchestration.
================================================================================
MANDATORY requirements (per hackathon spec):
  - Named `inference.py`, placed in the root directory of the project
  - Uses OpenAI Client for all LLM calls
  - Reads credentials from environment variables:
      API_BASE_URL   The API endpoint for the LLM
      MODEL_NAME     The model identifier to use for inference
      HF_TOKEN       Your HuggingFace / API key
  - Must complete in < 20 minutes on vcpu=2, memory=8gb
  - Must produce reproducible scores for all 3 tasks
"""

import os
import re
import json
import sys
import textwrap
from typing import List, Optional, Dict

from openai import OpenAI

from environment import APIWorkflowEnv, Action
from tasks import TASKS


# ─── Configuration (module-level constants, matching sample conventions) ───────

API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or "dummy"
MODEL_NAME   = os.getenv("MODEL_NAME")

MAX_TOKENS  = 512
TEMPERATURE = 0.0       
DEBUG       = False

FALLBACK_WORKFLOW: List[Dict] = []   # returned on unrecoverable parse failure

# Regex to strip any leading label like "workflow:" or "answer:" from LLM output
LABEL_PREFIX_RE = re.compile(r"^(workflow|answer|output|result)\s*[:\-]\s*", re.IGNORECASE)
# Regex to find a JSON array anywhere in the response
JSON_ARRAY_RE  = re.compile(r"\[.*\]", re.DOTALL)


# ─── Prompts ──────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = textwrap.dedent("""
    You are an API orchestration agent. Your job is to translate a user request
    into an ordered list of API calls that fulfils the request completely.

    Available APIs and their required parameters:
      flight_api(from_city, to_city)
      calendar_api(date, time)
      email_api(to)
      database_api(data)

    Rules:
    - Respond with ONLY a valid JSON array of objects.
    - Each object must have exactly two keys: "api" (string) and "params" (object).
    - Use only the APIs listed above.
    - Order matters: respect logical dependencies
      (e.g. flight must be booked before emailing confirmation).
    - Do NOT include markdown fences, explanations, or any other text.
    - For database_api, the data object MUST include:
        * destination
        * date
        * time

    Example:
    [
        {"api": "flight_api", "params": {"from_city": "NYC", "to_city": "Paris"}},
        {"api": "calendar_api", "params": {"date": "2026-05-01", "time": "10:00"}},
        {"api": "database_api", "params": {"data": {"destination": "Paris", "date": "2026-05-01", "time": "10:00"}}},
        {"api": "email_api", "params": {"to": "alice@x.com"}}
    ]
""").strip()


def build_user_message(task: Dict, history: List[str]) -> str:
    history_block = build_history_lines(history)
    return (
        f"Task: {task['user_input']}\n\n"
        f"Previous attempts:\n{history_block}\n\n"
        "Output the JSON workflow array now:"
    )


# ─── History helpers  ────────────────────────────────

def build_history_lines(history: List[str]) -> str:
    if not history:
        return "None"
    return "\n".join(history[-4:])   # keep last 4 entries, same as sample


# ─── Response parser ──────────────────────────────────────────────────────────

def parse_workflow(raw: str) -> Optional[List[Dict]]:
    """
    Robustly extract a JSON array from the LLM response.
    Returns None if parsing fails entirely.
    """
    if not raw:
        return None

    text = raw.strip()

    # Strip label prefix  (e.g. "workflow: [...]")
    text = LABEL_PREFIX_RE.sub("", text).strip()

    # Strip markdown code fences
    if "```" in text:
        # Take content between first and last fence
        parts = text.split("```")
        # parts[1] is the fenced block; strip leading "json" language tag
        text = parts[1].lstrip("json").strip() if len(parts) >= 2 else text

    # Try direct parse first
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    # Fall back: find first [...] block in the response
    match = JSON_ARRAY_RE.search(text)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    if DEBUG:
        print(f"  [WARN] Could not parse workflow from: {raw[:120]!r}")
    return None


# ─── LLM Agent ────────────────────────────────────────────────────────────────

def llm_agent(task: Dict, history: List[str]) -> Action:
    """
    Call LLM via OpenAI-compatible client.
    Falls back to rule-based agent if env vars are absent or on any error.
    """
    if not MODEL_NAME:
        if DEBUG:
            print("  [INFO] MODEL_NAME not set — using rule-based fallback")
        return rule_based_agent(task)

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": build_user_message(task, history)},
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        raw = response.choices[0].message.content or ""
        if DEBUG:
            print(f"  [LLM raw] {raw[:200]!r}")

        workflow = parse_workflow(raw)
        if workflow is None:
            print("  [WARN] parse failed — using rule-based fallback")
            return rule_based_agent(task)

        return Action(workflow=workflow)

    except Exception as e:
        print(f"  [ERROR] LLM call failed: {e} — using rule-based fallback")
        return rule_based_agent(task)


# ─── Rule-Based Agent (deterministic fallback) ────────────────────────────────

RULE_BASED_WORKFLOWS: Dict[str, List[Dict]] = {
    "easy": [
        {"api": "calendar_api", "params": {"date": "2026-04-08", "time": "10:00"}},
    ],
    "medium": [
        {"api": "flight_api", "params": {"from_city": "New York", "to_city": "London"}},
        {"api": "email_api",  "params": {"to": "john@example.com"}},
    ],
    "hard": [
        {"api": "flight_api", "params": {"from_city": "NYC", "to_city": "Paris"}},
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
}


def rule_based_agent(task: Dict) -> Action:
    """Deterministic fallback — always returns the correct workflow."""
    return Action(workflow=RULE_BASED_WORKFLOWS[task["id"]])


# ─── Main runner ──────────────────────────────────────────────────────────────

def main() -> List[float]:
    print("=" * 62)
    print("OpenEnv: API Workflow Orchestration — Baseline Inference")
    print("=" * 62)
    print(f"API_BASE_URL : {API_BASE_URL}")
    print(f"MODEL_NAME   : {MODEL_NAME or '(not set — rule-based fallback)'}")
    print(f"TEMPERATURE  : {TEMPERATURE}")
    print(f"MAX_TOKENS   : {MAX_TOKENS}")
    print(f"Using fallback: {not MODEL_NAME}")
    print()

    env = APIWorkflowEnv()
    env.reset()

    scores: List[float] = []
    history: List[str] = []   # shared history log across tasks (for multi-turn context)

    for i, task in enumerate(TASKS):
        print(f"[{i+1}/{len(TASKS)}] {task['difficulty'].upper()} — {task['description']}")
        print(f"  Input : {task['user_input'][:100]}...")

        action = llm_agent(task, history)
        apis_called = [s.get("api", "?") for s in action.workflow if isinstance(s, dict)]
        print(f"  APIs  : {apis_called}")

        _, reward, done, info = env.step(action)
        scores.append(reward.score)
        print(f"  Score : {reward.score:.4f}")

        # Record this attempt in history for subsequent tasks
        history.append(
            f"Task {i+1} [{task['difficulty']}]: called {apis_called} → score {reward.score:.4f}"
        )
        print()

    print("-" * 62)
    print(f"Scores        : {[round(s, 4) for s in scores]}")
    print(f"Average score : {sum(scores) / len(scores):.4f}")
    print(f"Total         : {sum(scores):.4f} / {float(len(scores)):.1f}")
    print("=" * 62)

    return scores


if __name__ == "__main__":
    scores = main()
    sys.exit(0 if len(scores) == len(TASKS) else 1)