"""
grader.py — Workflow Grading System
====================================
Scoring breakdown (max 1.0):
  0.6 × api_score   : F1 of precision & recall over correct APIs (deduped)
  0.4 × order_score : 1.0 perfect order | 0.5 right APIs wrong order | 0.0 otherwise

Penalties (subtracted before clamping):
  -0.15 per unknown / non-string API token
  -0.10 per valid-but-unnecessary API (correct vocab, but not in the required workflow)
  -0.05 per duplicate valid API call
"""

VALID_APIS = {"email_api", "calendar_api", "flight_api"}


def grade(correct: list, agent) -> float:
    """
    Score an agent's proposed workflow against the correct workflow.

    Parameters
    ----------
    correct : list  — ground-truth ordered list of API calls
    agent   : any   — agent's proposed workflow (should be a list of strings)

    Returns
    -------
    float in [0.0, 1.0]
    """

    # ── 1. Format validation ────────────────────────────────────────────────
    if not isinstance(agent, list) or len(agent) == 0:
        return 0.0

    # ── 2. Classify every token in the agent's response ─────────────────────
    valid_agent   = []   # valid API strings, in submission order
    invalid_count = 0    # unknown / non-string tokens
    duplicate_count = 0  # repeated valid API calls

    seen_valid = []      # tracks duplicates while preserving order

    for token in agent:
        if not isinstance(token, str) or token not in VALID_APIS:
            # Garbage token: not a string, or unrecognised API name
            invalid_count += 1
        elif token in seen_valid:
            # Valid API name, but already used — duplicate
            duplicate_count += 1
            valid_agent.append(token)   # still include for order scoring
        else:
            seen_valid.append(token)
            valid_agent.append(token)

    # Deduplicated list (preserves first-occurrence order)
    deduped_agent = list(dict.fromkeys(valid_agent))

    # ── 3. Early exit — no valid APIs at all ────────────────────────────────
    if not deduped_agent:
        # Agent produced zero recognisable APIs; apply garbage penalty and return
        garbage_penalty = min(0.15 * invalid_count, 1.0)
        return 0.0   # penalty cannot raise score above 0

    # ── 4. API coverage score (Precision × Recall → F1) ─────────────────────
    correct_set      = set(correct)
    deduped_set      = set(deduped_agent)

    true_positives   = len(deduped_set & correct_set)          # hits
    false_positives  = len(deduped_set - correct_set)          # valid but unneeded
    false_negatives  = len(correct_set - deduped_set)          # required but missing

    precision = true_positives / len(deduped_set)  if deduped_set  else 0.0
    recall    = true_positives / len(correct_set)  if correct_set  else 0.0

    if precision + recall > 0:
        api_score = (2 * precision * recall) / (precision + recall)   # F1
    else:
        api_score = 0.0

    # ── 5. Order score ───────────────────────────────────────────────────────
    if deduped_agent == correct:
        order_score = 1.0                          # perfect: exact APIs, exact order
    elif deduped_set == correct_set:
        order_score = 0.5                          # all required APIs present, wrong order
    elif true_positives > 0:
        order_score = 0.1 * (true_positives / len(correct))  # partial credit
    else:
        order_score = 0.0                          # nothing useful

    # ── 6. Penalties ─────────────────────────────────────────────────────────
    invalid_penalty   = 0.15 * invalid_count        # garbage / unknown tokens
    extra_api_penalty = 0.10 * false_positives      # valid but unnecessary APIs
    duplicate_penalty = 0.05 * duplicate_count      # repeated valid API calls

    total_penalty = invalid_penalty + extra_api_penalty + duplicate_penalty

    # ── 7. Compose final score ───────────────────────────────────────────────
    score = (0.6 * api_score) + (0.4 * order_score) - total_penalty
    score = round(max(0.0, min(1.0, score)), 4)
    return score