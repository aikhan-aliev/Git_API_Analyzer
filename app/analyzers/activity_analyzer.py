"""
Activity Analyzer - Uses GitHub commit/push data to assess project health.
Looks at recent commit cadence, open issues, and last-push date.
"""
import httpx
from datetime import datetime, timezone, timedelta
from typing import Any


def analyze_activity(owner: str, repo: str, headers: dict, repo_metadata: dict) -> dict[str, Any]:
    results: dict[str, Any] = {
        "total_commits_sample": 0,
        "recent_commits_30d": 0,
        "recent_commits_90d": 0,
        "days_since_last_push": None,
        "open_issues": repo_metadata.get("open_issues_count", 0),
        "has_recent_activity": False,
        "findings": [],
        "score": 0.0,
        "metrics": {}
    }

    now = datetime.now(timezone.utc)

    # Compute days since last push
    pushed_at_str = repo_metadata.get("pushed_at")
    if pushed_at_str:
        pushed_at = datetime.fromisoformat(pushed_at_str.replace("Z", "+00:00"))
        days_since = (now - pushed_at).days
        results["days_since_last_push"] = days_since
        results["has_recent_activity"] = days_since < 90

    # Fetch last 100 commits (GitHub max per page)
    since_90d = (now - timedelta(days=90)).isoformat()
    try:
        resp = httpx.get(
            f"https://api.github.com/repos/{owner}/{repo}/commits",
            params={"per_page": 100, "since": since_90d},
            headers=headers, timeout=15.0
        )
        if resp.status_code == 200:
            commits = resp.json()
            results["total_commits_sample"] = len(commits)
            since_30d = now - timedelta(days=30)
            recent_30 = [
                c for c in commits
                if "commit" in c and "committer" in c["commit"]
                and c["commit"]["committer"].get("date")
                and datetime.fromisoformat(
                    c["commit"]["committer"]["date"].replace("Z", "+00:00")
                ) > since_30d
            ]
            results["recent_commits_30d"] = len(recent_30)
            results["recent_commits_90d"] = len(commits)
    except Exception as e:
        results["findings"].append({
            "severity": "info", "category": "activity",
            "title": "Could not fetch commit history",
            "description": str(e)
        })

    # Score: combine recency (50%), commit volume (30%), open issues health (20%)
    score = 0.0

    # Recency score (50 pts)
    days = results.get("days_since_last_push")
    if days is not None:
        if days < 30:
            score += 50
        elif days < 90:
            score += 35
        elif days < 180:
            score += 20
        elif days < 365:
            score += 10

    # Commit volume score (30 pts)
    c90 = results["recent_commits_90d"]
    if c90 >= 30:
        score += 30
    elif c90 >= 10:
        score += 20
    elif c90 >= 3:
        score += 10

    # Open issues penalty (20 pts available - deduct for high open issue count)
    oi = results["open_issues"]
    if oi == 0:
        score += 20
    elif oi < 10:
        score += 15
    elif oi < 50:
        score += 10
    elif oi < 200:
        score += 5

    results["score"] = round(min(score, 100), 1)

    # Findings
    if days is not None and days > 365:
        results["findings"].append({
            "severity": "error", "category": "activity",
            "title": "Repository Appears Abandoned",
            "description": f"No pushes in {days} days.",
            "recommendation": "Archive or update the repository if still relevant."
        })
    elif days is not None and days > 90:
        results["findings"].append({
            "severity": "warning", "category": "activity",
            "title": "Low Recent Activity",
            "description": f"Last push was {days} days ago.",
            "recommendation": "Consider increasing commit frequency."
        })

    if results["recent_commits_90d"] < 3 and days is not None and days < 365:
        results["findings"].append({
            "severity": "warning", "category": "activity",
            "title": "Very Few Commits in Last 90 Days",
            "description": f"Only {results['recent_commits_90d']} commits in the last 90 days.",
            "recommendation": "Increase development pace or assess if project is stagnant."
        })

    results["metrics"] = {
        "days_since_last_push": results["days_since_last_push"],
        "commits_last_30d": results["recent_commits_30d"],
        "commits_last_90d": results["recent_commits_90d"],
        "open_issues": results["open_issues"],
    }

    return results
