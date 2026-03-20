"""
Contributor Analyzer - Checks contributor diversity, Bus Factor, and collaboration health.
"""
import httpx
from typing import Any


def analyze_contributors(owner: str, repo: str, headers: dict) -> dict[str, Any]:
    results: dict[str, Any] = {
        "total_contributors": 0,
        "top_contributor_pct": None,
        "bus_factor": 0,
        "findings": [],
        "score": 0.0,
        "metrics": {}
    }

    try:
        resp = httpx.get(
            f"https://api.github.com/repos/{owner}/{repo}/contributors",
            params={"per_page": 100, "anon": "false"},
            headers=headers, timeout=15.0
        )
        if resp.status_code != 200:
            return results

        contributors = resp.json()
        if not isinstance(contributors, list) or not contributors:
            return results

        results["total_contributors"] = len(contributors)
        total_commits = sum(c.get("contributions", 0) for c in contributors)

        if total_commits > 0:
            top_pct = contributors[0].get("contributions", 0) / total_commits * 100
            results["top_contributor_pct"] = round(top_pct, 1)

            # Bus Factor: number of contributors responsible for >= 50% of commits
            cumulative = 0
            bus_factor = 0
            for c in contributors:
                cumulative += c.get("contributions", 0)
                bus_factor += 1
                if cumulative / total_commits >= 0.5:
                    break
            results["bus_factor"] = bus_factor

    except Exception as e:
        results["findings"].append({
            "severity": "info", "category": "contributor",
            "title": "Could not fetch contributors",
            "description": str(e)
        })
        return results

    # Score (100 pts)
    score = 0.0

    # Contributor count (40 pts)
    n = results["total_contributors"]
    if n >= 10:
        score += 40
    elif n >= 5:
        score += 30
    elif n >= 3:
        score += 20
    elif n >= 2:
        score += 10

    # Bus factor (40 pts)
    bf = results["bus_factor"]
    if bf >= 5:
        score += 40
    elif bf >= 3:
        score += 30
    elif bf >= 2:
        score += 20
    elif bf == 1:
        score += 5

    # Top contributor dominance penalty (20 pts)
    top_pct = results["top_contributor_pct"] or 100
    if top_pct < 40:
        score += 20
    elif top_pct < 60:
        score += 15
    elif top_pct < 80:
        score += 8

    results["score"] = round(min(score, 100), 1)

    # Findings
    if results["bus_factor"] == 1:
        results["findings"].append({
            "severity": "critical", "category": "contributor",
            "title": "Bus Factor of 1 (Single Point of Failure)",
            "description": "One contributor accounts for >50% of all commits.",
            "recommendation": "Encourage more contributors to make commits to critical areas."
        })
    elif results["bus_factor"] < 3:
        results["findings"].append({
            "severity": "warning", "category": "contributor",
            "title": "Low Bus Factor",
            "description": f"Bus factor is {results['bus_factor']}.",
            "recommendation": "Broaden contributor base to reduce single-person dependency."
        })

    if results["total_contributors"] == 1:
        results["findings"].append({
            "severity": "warning", "category": "contributor",
            "title": "Solo Project",
            "description": "Only one contributor detected.",
            "recommendation": "Consider inviting collaborators to improve sustainability."
        })

    results["metrics"] = {
        "total_contributors": results["total_contributors"],
        "bus_factor": results["bus_factor"],
        "top_contributor_commit_pct": results["top_contributor_pct"],
    }

    return results
