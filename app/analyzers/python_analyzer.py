"""
Python Code Analyzer - Clones a Python repository and runs Radon (complexity)
and Bandit (security) analysis on the source code.
"""
import os
import json
import shutil
import tempfile
import subprocess
from typing import Any


def _run_command(cmd: list[str], cwd: str) -> tuple[int, str, str]:
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, timeout=120
    )
    return result.returncode, result.stdout, result.stderr


def analyze_python_code(clone_url: str, default_branch: str = "main") -> dict[str, Any]:
    results: dict[str, Any] = {
        "is_python": True,
        "complexity": {},
        "security": {},
        "findings": [],
        "score": 0.0,
        "metrics": {}
    }

    tmpdir = tempfile.mkdtemp(prefix="repo_analyzer_")
    try:
        # Shallow clone
        returncode, stdout, stderr = _run_command(
            ["git", "clone", "--depth", "1", "--branch", default_branch, clone_url, tmpdir],
            cwd=os.path.dirname(tmpdir)
        )
        if returncode != 0:
            # try default
            returncode, _, stderr = _run_command(
                ["git", "clone", "--depth", "1", clone_url, tmpdir],
                cwd=os.path.dirname(tmpdir)
            )
            if returncode != 0:
                results["findings"].append({
                    "severity": "error", "category": "python_analysis",
                    "title": "Could not clone repository",
                    "description": stderr[:500]
                })
                results["is_python"] = False
                return results

        # Check if there are .py files
        py_files = []
        for root, _, files in os.walk(tmpdir):
            for f in files:
                if f.endswith(".py"):
                    py_files.append(os.path.join(root, f))
            # Skip .git
            if ".git" in root.split(os.sep):
                continue

        if not py_files:
            results["is_python"] = False
            results["findings"].append({
                "severity": "info", "category": "python_analysis",
                "title": "Not a Python Repository",
                "description": "No .py files found in the repository."
            })
            return results

        results["metrics"]["python_file_count"] = len(py_files)

        # --- Radon Complexity ---
        rc, radon_out, _ = _run_command(
            ["python", "-m", "radon", "cc", ".", "--json", "-a"],
            cwd=tmpdir
        )
        if rc == 0 and radon_out.strip():
            try:
                radon_data = json.loads(radon_out)
                all_complexities = []
                for fpath, funcs in radon_data.items():
                    for func in funcs:
                        all_complexities.append(func.get("complexity", 0))

                if all_complexities:
                    avg_cc = sum(all_complexities) / len(all_complexities)
                    max_cc = max(all_complexities)
                    results["complexity"] = {
                        "average_cyclomatic_complexity": round(avg_cc, 2),
                        "max_cyclomatic_complexity": max_cc,
                        "function_count": len(all_complexities)
                    }
                    results["metrics"]["avg_cyclomatic_complexity"] = round(avg_cc, 2)
                    results["metrics"]["max_cyclomatic_complexity"] = max_cc

                    if avg_cc > 10:
                        results["findings"].append({
                            "severity": "error", "category": "complexity",
                            "title": "High Average Cyclomatic Complexity",
                            "description": f"Average CC is {avg_cc:.1f} (threshold: 10).",
                            "recommendation": "Refactor complex functions to reduce branching."
                        })
                    elif avg_cc > 6:
                        results["findings"].append({
                            "severity": "warning", "category": "complexity",
                            "title": "Moderate Cyclomatic Complexity",
                            "description": f"Average CC is {avg_cc:.1f} (ideal: <6).",
                            "recommendation": "Consider simplifying complex functions."
                        })
            except json.JSONDecodeError:
                pass

        # --- Bandit Security ---
        rc, bandit_out, _ = _run_command(
            ["python", "-m", "bandit", "-r", ".", "-f", "json", "-q"],
            cwd=tmpdir
        )
        if bandit_out.strip():
            try:
                bandit_data = json.loads(bandit_out)
                metrics = bandit_data.get("metrics", {}).get("_totals", {})
                issues = bandit_data.get("results", [])
                high_issues = [i for i in issues if i.get("issue_severity") == "HIGH"]
                medium_issues = [i for i in issues if i.get("issue_severity") == "MEDIUM"]

                results["security"] = {
                    "total_issues": len(issues),
                    "high_severity": len(high_issues),
                    "medium_severity": len(medium_issues),
                }
                results["metrics"]["security_high_issues"] = len(high_issues)
                results["metrics"]["security_medium_issues"] = len(medium_issues)
                results["metrics"]["security_total_issues"] = len(issues)

                if high_issues:
                    results["findings"].append({
                        "severity": "critical", "category": "security",
                        "title": f"{len(high_issues)} High-Severity Security Issues Found",
                        "description": f"Bandit found {len(high_issues)} HIGH severity security issues.",
                        "recommendation": "Review and fix high-severity security vulnerabilities immediately."
                    })
                if medium_issues:
                    results["findings"].append({
                        "severity": "warning", "category": "security",
                        "title": f"{len(medium_issues)} Medium-Severity Security Issues Found",
                        "description": f"Bandit found {len(medium_issues)} MEDIUM severity issues.",
                        "recommendation": "Review medium-severity security findings."
                    })
            except json.JSONDecodeError:
                pass

        # Score: complexity (50) + security (50)
        score = 0.0
        cc = results.get("complexity", {})
        avg = cc.get("average_cyclomatic_complexity", 0)
        if avg == 0:
            score += 50
        elif avg <= 3:
            score += 50
        elif avg <= 6:
            score += 40
        elif avg <= 10:
            score += 25
        else:
            score += 0

        sec = results.get("security", {})
        h = sec.get("high_severity", 0)
        m = sec.get("medium_severity", 0)
        if h == 0 and m == 0:
            score += 50
        elif h == 0:
            score += 30 - min(m * 2, 20)
        else:
            score += max(0, 20 - h * 5)

        results["score"] = round(min(score, 100), 1)

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return results
