import httpx
from fastapi import HTTPException
from pydantic import HttpUrl

class GitHubService:
    def __init__(self, token: str = ""):
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            self.headers["Authorization"] = f"token {token}"

    def parse_input(self, repo_input: str) -> tuple[str, str]:
        # Clean up URL or parse owner/repo
        repo_input = repo_input.strip()
        if repo_input.startswith("http"):
            parts = repo_input.rstrip("/").split("/")
            if len(parts) >= 2:
                return parts[-2], parts[-1]
        elif "/" in repo_input:
            parts = repo_input.split("/")
            if len(parts) == 2:
                return parts[0], parts[1]
        
        raise ValueError("Invalid repository format.")

    def fetch_repo_metadata(self, owner: str, repo: str) -> dict:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = httpx.get(url, headers=self.headers, timeout=10.0)
        
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Repository not found on GitHub")
        elif response.status_code == 403:
            raise HTTPException(status_code=403, detail="GitHub API rate limit exceeded or access denied")
        
        response.raise_for_status()
        return response.json()
