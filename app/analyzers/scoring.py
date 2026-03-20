"""
Scoring Service - Aggregates scores from all analyzers into an overall risk report.
"""


RISK_LEVELS = [
    (80, "low"),
    (60, "moderate"),
    (40, "elevated"),
    (0, "high"),
]


def get_risk_level(score: float) -> str:
    for threshold, level in RISK_LEVELS:
        if score >= threshold:
            return level
    return "high"


def compute_overall_score(
    structure_score: float,
    activity_score: float,
    contributor_score: float,
    python_score: float | None,
) -> dict:
    """
    Weighted score computation.
    Weights:
      - Structure:    20%
      - Activity:     30%
      - Contributors: 30%
      - Python:       20% (only if it's a Python repo; else redistributed)
    """
    if python_score is not None:
        weights = {
            "structure": 0.20,
            "activity": 0.30,
            "contributor": 0.30,
            "python": 0.20,
        }
        weighted = (
            structure_score * weights["structure"]
            + activity_score * weights["activity"]
            + contributor_score * weights["contributor"]
            + python_score * weights["python"]
        )
        component_scores = {
            "maintainability_score": structure_score,
            "activity_score": activity_score,
            "collaboration_score": contributor_score,
            "security_score": python_score,
            "sustainability_score": (activity_score + contributor_score) / 2,
        }
    else:
        weights = {
            "structure": 0.25,
            "activity": 0.375,
            "contributor": 0.375,
        }
        weighted = (
            structure_score * weights["structure"]
            + activity_score * weights["activity"]
            + contributor_score * weights["contributor"]
        )
        component_scores = {
            "maintainability_score": structure_score,
            "activity_score": activity_score,
            "collaboration_score": contributor_score,
            "security_score": None,
            "sustainability_score": (activity_score + contributor_score) / 2,
        }

    overall = round(weighted, 1)
    return {
        "overall_score": overall,
        "overall_risk_level": get_risk_level(overall),
        **component_scores,
    }
