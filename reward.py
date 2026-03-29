"""
reward.py — Reward Shaping
===========================
Converts a grader score [0, 1] into a shaped reward signal.

Tiers
-----
  score == 1.0          →  +10.0   (perfect)
  score >= 0.8          →  +7.0    (good)
  score >= 0.5          →  +3.0    (partial)
  score >= 0.1          →  +0.5    (attempted, at least one right API)
  score == 0.0          →  -2.0    (completely wrong / garbage)

A small continuous bonus (+score) is added on top of the tier reward so
that agents are still incentivised to maximise within each tier.
"""


def compute_reward(score: float) -> float:
    """
    Map a grader score to a shaped scalar reward.

    Parameters
    ----------
    score : float — value in [0.0, 1.0] from grader.grade()

    Returns
    -------
    float — shaped reward
    """
    if score == 1.0:
        tier_reward = 10.0
    elif score >= 0.8:
        tier_reward = 7.0
    elif score >= 0.5:
        tier_reward = 3.0
    elif score > 0.0:
        tier_reward = 0.5
    else:
        tier_reward = -2.0   # penalise pure garbage / completely wrong answers

    # Continuous bonus so agents still push for higher scores within a tier
    reward = round(tier_reward + score, 4)
    return reward