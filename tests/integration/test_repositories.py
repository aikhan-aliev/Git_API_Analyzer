from unittest.mock import patch

def test_register_repository(client):
    client.post("/api/v1/auth/register", json={"email": "repo@example.com", "password": "password123"})
    login_res = client.post("/api/v1/auth/login", data={"username": "repo@example.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    mock_metadata = {
        "owner": {"login": "testowner"},
        "name": "testrepo",
        "full_name": "testowner/testrepo",
        "html_url": "https://github.com/testowner/testrepo",
        "clone_url": "https://github.com/testowner/testrepo.git",
        "default_branch": "main",
        "description": "Test Repo",
        "language": "Python",
        "stargazers_count": 10,
        "forks_count": 2,
        "open_issues_count": 1,
        "private": False,
        "archived": False
    }

    with patch("app.services.repository_service.GitHubService.fetch_repo_metadata", return_value=mock_metadata):
        response = client.post(
            "/api/v1/repositories",
            json={"repository_url_or_name": "testowner/testrepo"},
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "testowner/testrepo"
        assert data["github_owner"] == "testowner"
        assert "id" in data

def test_get_repositories(client):
    client.post("/api/v1/auth/register", json={"email": "repo2@example.com", "password": "password123"})
    login_res = client.post("/api/v1/auth/login", data={"username": "repo2@example.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/repositories", headers=headers)
    assert response.status_code == 200
    assert response.json() == []
