from __future__ import annotations


def probability_to_score(probability: float) -> int:
    """Convert default probability to a 0-100 risk score."""
    p = max(0.0, min(1.0, float(probability)))
    return int(round(p * 100))


def score_to_band(score: int) -> str:
    """Map a risk score to a business-friendly category.

    PDF allows Low / Medium / High / Very High examples but does not mandate exact thresholds.
    These thresholds are recommendations, not PDF official rules.
    """
    if score < 25:
        return 'Low Risk'
    if score < 50:
        return 'Medium Risk'
    if score < 75:
        return 'High Risk'
    return 'Very High Risk'


def risk_summary(probability: float) -> dict:
    score = probability_to_score(probability)
    band = score_to_band(score)
    return {
        'default_probability': float(probability),
        'risk_score': score,
        'risk_band': band,
    }
