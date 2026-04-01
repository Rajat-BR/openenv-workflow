from typing import List, Dict, Tuple, Optional


def _normalise(token: str) -> str:
    return token.strip().lower()


def _lcs_length(a: List[str], b: List[str]) -> int:
    m, n = len(a), len(b)
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            curr[j] = (
                prev[j - 1] + 1 if a[i - 1] == b[j - 1]
                else max(prev[j], curr[j - 1])
            )
        prev, curr = curr, [0] * (n + 1)
    return prev[n]


def _dep_satisfaction(agent_seq: List[str], dependencies: List[Tuple[str, str]]) -> float:
    if not dependencies:
        return 1.0
    pos = {api: i for i, api in enumerate(agent_seq)}
    satisfied = sum(
        1 for a, b in dependencies
        if a not in pos or b not in pos or pos[a] < pos[b]
    )
    return satisfied / len(dependencies)


def _param_score(submitted: List[Dict], expected: List[Dict]) -> float:
    total_expected_kv = sum(len(s.get("params", {})) for s in expected)
    if total_expected_kv == 0:
        return 1.0

    sub_params_map: Dict[str, List[Dict]] = {}
    for step in submitted:
        raw_name = step.get("api", "")
        if not isinstance(raw_name, str):
            continue
        norm_name = _normalise(raw_name)
        params = step.get("params", {})
        if not isinstance(params, dict):
            params = {}
        sub_params_map.setdefault(norm_name, []).append(params)

    used: Dict[str, int] = {}
    correct_kv = 0

    for exp_step in expected:
        exp_api = _normalise(exp_step["api"])
        exp_params = exp_step.get("params", {})

        calls = sub_params_map.get(exp_api, [])
        idx = used.get(exp_api, 0)
        if idx >= len(calls):
            continue

        sub_p = calls[idx]
        used[exp_api] = idx + 1

        for key, expected_val in exp_params.items():
            if key in sub_p and sub_p[key] == expected_val:
                correct_kv += 1

    return correct_kv / total_expected_kv


# ── FIXED FUNCTION ────────────────────────────────────────────────────────────

def grade(correct: List[Dict], workflow: List[Dict], dependencies: Optional[List[Tuple[str, str]]] = None) -> float:
    """
    FIXED: Now takes (correct_workflow, agent_workflow)
    """

    # ✅ FIX 1: remove task dependency
    expected: List[Dict] = correct

    # ✅ FIX 2: remove task-based dependencies
    if dependencies is None:
        dependencies = []

    # ── 1. Validate input ─────────────────────────────────────
    if not isinstance(workflow, list) or len(workflow) == 0:
        return 0.0
    if not expected:
        return 0.0

    from apis import AVAILABLE_APIS
    known_apis = set(AVAILABLE_APIS)
    correct_apis = [_normalise(s["api"]) for s in expected]
    correct_set = set(correct_apis)

    valid_agent = []
    invalid_count = 0
    duplicate_count = 0
    seen_valid = []

    valid_submitted_steps = []

    for step in workflow:
        if not isinstance(step, dict):
            invalid_count += 1
            continue

        raw_name = step.get("api", "")
        if not isinstance(raw_name, str):
            invalid_count += 1
            continue

        norm = _normalise(raw_name)

        if norm not in known_apis:
            invalid_count += 1
        elif norm in seen_valid:
            duplicate_count += 1
            valid_agent.append(norm)
            valid_submitted_steps.append(step)
        else:
            seen_valid.append(norm)
            valid_agent.append(norm)
            valid_submitted_steps.append(step)

    deduped_agent = list(dict.fromkeys(valid_agent))

    if not deduped_agent:
        return 0.0

    deduped_set = set(deduped_agent)
    true_positives = len(deduped_set & correct_set)

    if true_positives == 0:
        return 0.0

    # ── API score ─────────────────────────────────────────────
    false_positives = len(deduped_set - correct_set)

    precision = true_positives / len(deduped_set)
    recall = true_positives / len(correct_set)

    api_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    # ── Order score ───────────────────────────────────────────
    if deduped_agent == correct_apis:
        order_score = 1.0
    elif deduped_set == correct_set:
        dep_sat = _dep_satisfaction(deduped_agent, dependencies)
        order_score = 0.9 * (0.7 + 0.3 * dep_sat)
    else:
        agent_hits = [t for t in deduped_agent if t in correct_set]
        lcs = _lcs_length(agent_hits, correct_apis)
        lcs_ratio = lcs / len(correct_apis)
        dep_sat = _dep_satisfaction(deduped_agent, dependencies)
        order_score = 0.85 * (0.7 * lcs_ratio + 0.3 * dep_sat)

    # ── Efficiency ────────────────────────────────────────────
    n_correct = len(correct_apis)
    n_agent = len(deduped_agent)
    efficiency_score = true_positives / n_correct

    # ── Params ────────────────────────────────────────────────
    score_params = _param_score(valid_submitted_steps, expected)

    # ── Penalties ─────────────────────────────────────────────
    invalid_penalty = 0.08 * invalid_count
    extra_api_penalty = 0.05 * false_positives
    duplicate_penalty = 0.03 * duplicate_count

    total_penalty = invalid_penalty + extra_api_penalty + duplicate_penalty

    # ── Final ────────────────────────────────────────────────
    score = (
        0.40 * api_score +
        0.30 * order_score +
        0.20 * efficiency_score +
        0.10 * score_params -
        total_penalty
    )

    return round(max(0.0, min(1.0, score)), 4)