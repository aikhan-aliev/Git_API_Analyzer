"""
Repository Structure Analyzer - Uses GitHub API to analyze repo structure.
Checks for presence of essential files and directory organization.
"""
import httpx
from typing import Any

ESSENTIAL_FILES = ["README.md", "LICENSE", ".gitignore"]
CI_PATTERNS = [".github/workflows", ".travis.yml", ".circleci", "Jenkinsfile", "Makefile"]
DEPENDENCY_FILES = [
    "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg",
    "package.json", "Gemfile", "pom.xml", "build.gradle", "Cargo.toml",
    "go.mod"
]
TESTING_PATTERNS = ["test", "tests", "spec", "__tests__", "test_"]


def analyze_structure(owner: str, repo: str, headers: dict) -> dict[str, Any]:
    """Fetch directory tree and check for essential structure indicators."""
    results: dict[str, Any] = {
        "has_readme": False,
        "has_license": False,
        "has_gitignore": False,
        "has_ci": False,
        "has_dependency_file": False,
        "has_tests": False,
        "root_files": [],
        "findings": [],
        "score": 0.0
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
    try:
        resp = httpx.get(url, headers=headers, timeout=15.0)
        resp.raise_for_status()
        root_contents = resp.json()
    except Exception as e:
        results["findings"].append({
            "severity": "error",
            "title": "Could not fetch repository structure",
            "description": str(e),
            "category": "structure"
        })
        return results

    root_names = [item["name"] for item in root_contents if isinstance(item, dict)]
    results["root_files"] = root_names

    # Check essential files
    for fname in root_names:
        lower = fname.lower()
        if lower == "readme.md" or lower == "readme":
            results["has_readme"] = True
        if lower == "license" or lower == "license.md" or lower == "license.txt":
            results["has_license"] = True
        if lower == ".gitignore":
            results["has_gitignore"] = True

    # Check for CI configuration in root
    for ci in CI_PATTERNS:
        if any(ci.lower() in name.lower() for name in root_names):
            results["has_ci"] = True
            break

    # Check .github/workflows separately
    if ".github" in root_names:
        try:
            wf_resp = httpx.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents/.github/workflows",
                headers=headers, timeout=10.0
            )
            if wf_resp.status_code == 200 and wf_resp.json():
                results["has_ci"] = True
        except Exception:
            pass

    # Check for dependency files
    for dep in DEPENDENCY_FILES:
        if dep in root_names:
            results["has_dependency_file"] = True
            break

    # Check for test directories: naive top-level check
    for name in root_names:
        if any(pat in name.lower() for pat in TESTING_PATTERNS):
            results["has_tests"] = True
            break

    # Score: each criterion = 100/6 points
    checks = [
        results["has_readme"], results["has_license"], results["has_gitignore"],
        results["has_ci"], results["has_dependency_file"], results["has_tests"]
    ]
    score = round(sum(checks) / len(checks) * 100, 1)
    results["score"] = score

    # Generate findings
    if not results["has_readme"]:
        results["findings"].append({
            "severity": "warning", "category": "structure",
            "title": "Missing README",
            "description": "No README file found at the repository root.",
            "recommendation": "Add a README.md describing the project purpose, installation, and usage."
        })
    if not results["has_license"]:
        results["findings"].append({
            "severity": "warning", "category": "structure",
            "title": "Missing License",
            "description": "No LICENSE file found.",
            "recommendation": "Add a LICENSE file to clarify terms of use."
        })
    if not results["has_gitignore"]:
        results["findings"].append({
            "severity": "info", "category": "structure",
            "title": "Missing .gitignore",
            "description": "No .gitignore file found.",
            "recommendation": "Add a .gitignore to avoid committing generated files."
        })
    if not results["has_ci"]:
        results["findings"].append({
            "severity": "warning", "category": "structure",
            "title": "No CI/CD Pipeline Detected",
            "description": "No CI/CD configuration found.",
            "recommendation": "Add GitHub Actions, Travis CI, or similar to enforce quality gates."
        })
    if not results["has_tests"]:
        results["findings"].append({
            "severity": "warning", "category": "structure",
            "title": "No Test Directory Detected",
            "description": "No tests/ or test/ directory found at root.",
            "recommendation": "Add a test suite to improve confidence in code correctness."
        })

    return results
