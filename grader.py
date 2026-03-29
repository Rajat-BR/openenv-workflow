"""
grader.py — Proportional partial-credit grader.

Scoring breakdown:
  1. API Selection  (0.4) — correct_api_count / total_expected * 0.4
  2. Order          (0.3) — correct_position_count / total_expected * 0.3
  3. Parameters     (0.3) — correct_param_kv_matches / total_expected_params * 0.3

Penalties (applied after, then clamp to [0.0, 1.0]):
  - Invalid API (not in AVAILABLE_APIS): -0.2 each
  - Extra API   (not in expected set):   -0.1 each
  - Missing API: NOT penalized (already reflected in lower scores above)
"""

from typing import List, Dict


def grade(workflow, task: Dict) -> float:
    """
    Grade a submitted workflow against a task definition.
    Always returns float in [0.0, 1.0]. Never raises.
    """
    # ── Safe input handling ───────────────────────────────────────────────────
    if not isinstance(workflow, list) or len(workflow) == 0:
        return 0.0

    expected: List[Dict] = task.get("expected_workflow", [])
    if not expected:
        return 0.0

    from apis import AVAILABLE_APIS
    known_apis = set(AVAILABLE_APIS)

    # Normalise submitted steps — skip anything not a dict
    submitted: List[Dict] = []
    for step in workflow:
        if isinstance(step, dict) and isinstance(step.get("api"), str):
            submitted.append(step)

    if not submitted:
        return 0.0

    expected_apis = [s["api"] for s in expected]
    submitted_apis = [s["api"] for s in submitted]
    expected_set = set(expected_apis)
    total_expected = len(expected_apis)

    # ── 1. API Selection Score (0.4) ─────────────────────────────────────────
    # How many expected APIs appear at least once in the submission
    correct_api_count = sum(1 for api in expected_apis if api in set(submitted_apis))
    score_api = (correct_api_count / total_expected) * 0.4

    # ── 2. Order Score (0.3) ─────────────────────────────────────────────────
    # How many APIs are at the correct index position
    correct_position_count = 0
    for i, expected_api in enumerate(expected_apis):
        if i < len(submitted_apis) and submitted_apis[i] == expected_api:
            correct_position_count += 1
    score_order = (correct_position_count / total_expected) * 0.3

    # ── 3. Parameter Score (0.3) ─────────────────────────────────────────────
    # For each expected step, find its match in submitted, compare key-value pairs
    total_expected_params = sum(len(s.get("params", {})) for s in expected)
    correct_param_matches = 0

    if total_expected_params > 0:
        # Build lookup: api_name → list of submitted param dicts for that api
        submitted_params_map: Dict[str, List[Dict]] = {}
        for step in submitted:
            api_name = step["api"]
            params = step.get("params", {})
            if not isinstance(params, dict):
                params = {}
            submitted_params_map.setdefault(api_name, []).append(params)

        used_indices: Dict[str, int] = {}  # track which call index we've consumed per api

        for exp_step in expected:
            api_name = exp_step["api"]
            exp_params = exp_step.get("params", {})
            if not isinstance(exp_params, dict):
                continue

            calls = submitted_params_map.get(api_name, [])
            idx = used_indices.get(api_name, 0)
            if idx >= len(calls):
                continue  # no submitted call for this api

            sub_params = calls[idx]
            used_indices[api_name] = idx + 1

            # Count matching key-value pairs
            for key, expected_val in exp_params.items():
                if key in sub_params and sub_params[key] == expected_val:
                    correct_param_matches += 1

        score_params = (correct_param_matches / total_expected_params) * 0.3
    else:
        score_params = 0.3  # no params required → full param credit

    raw_score = score_api + score_order + score_params

    # ── Penalties ─────────────────────────────────────────────────────────────
    # Invalid APIs (not in registry at all)
    invalid_penalty = sum(0.2 for api in submitted_apis if api not in known_apis)

    # Extra APIs (not in the expected set for this task)
    extra_penalty = sum(0.1 for api in submitted_apis if api not in expected_set)

    final_score = raw_score - invalid_penalty - extra_penalty
    return round(max(0.0, min(1.0, final_score)), 4)