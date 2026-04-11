"""Tests for the FastAPI server endpoints."""

import pytest
from fastapi.testclient import TestClient
from server.app import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealth:
    def test_health_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestLanding:
    def test_root_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]


class TestReset:
    def test_reset_easy(self, client):
        resp = client.post("/reset", json={"task_id": "easy"})
        assert resp.status_code == 200
        data = resp.json()
        assert "rooms" in data
        assert "teams" in data

    def test_reset_default(self, client):
        resp = client.post("/reset")
        assert resp.status_code == 200


class TestStep:
    def test_step_after_reset(self, client):
        client.post("/reset", json={"task_id": "easy"})
        mapping = {f"T{i}": f"R{(i % 10) + 1}" for i in range(1, 51)}
        resp = client.post("/step", json={
            "task_id": "easy",
            "assignments": mapping,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "reward" in data

    def test_step_without_reset_fails(self, client):
        # fresh app state — should error
        resp = client.post("/step", json={
            "task_id": "nonexistent",
            "assignments": {},
        })
        assert resp.status_code in (400, 422, 500)


class TestTasks:
    def test_list_tasks(self, client):
        resp = client.get("/tasks")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_task_detail(self, client):
        resp = client.get("/tasks/easy")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "easy"
