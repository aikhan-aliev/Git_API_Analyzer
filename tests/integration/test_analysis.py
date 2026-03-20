from unittest.mock import patch

def test_trigger_analysis(client):
    client.post("/api/v1/auth/register", json={"email": "analysis@example.com", "password": "password123"})
    login_res = client.post("/api/v1/auth/login", data={"username": "analysis@example.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    mock_metadata = {
        "owner": {"login": "testowner"}, "name": "testrepo",
        "full_name": "testowner/testrepo", "html_url": "https://github.com/testowner/testrepo",
        "clone_url": "https://github.com/testowner/testrepo.git", "default_branch": "main",
        "description": "Test Repo", "language": "Python", "stargazers_count": 10,
        "forks_count": 2, "open_issues_count": 1, "private": False, "archived": False
    }

    with patch("app.services.repository_service.GitHubService.fetch_repo_metadata", return_value=mock_metadata):
        repo_res = client.post("/api/v1/repositories", json={"repository_url_or_name": "testowner/testrepo"}, headers=headers)
        repo_id = repo_res.json()["id"]

    with patch("app.workers.tasks.run_analysis_job.delay") as mock_delay:
        response = client.post(f"/api/v1/analysis/repositories/{repo_id}/analyze", headers=headers)
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "pending"
        assert data["repository_id"] == repo_id
        assert "id" in data
        mock_delay.assert_called_once()
        job_id = data["id"]

    status_response = client.get(f"/api/v1/analysis/jobs/{job_id}", headers=headers)
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "pending"
