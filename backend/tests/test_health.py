from fastapi.testclient import TestClient
from app.database import get_db

class DummyDBSuccess:
    def execute(self, stmt):
        class DummyScalar:
            def scalar(self):
                return 1
        return DummyScalar()

class DummyDBFailure:
    def execute(self, stmt):
        raise RuntimeError("Simulated connection timeout")

def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Abhigyan Complaint Monitoring API"
    assert "health" in data

def test_health_endpoint_success(client: TestClient):
    def override_db():
        yield DummyDBSuccess()

    from app.main import app
    app.dependency_overrides[get_db] = override_db
    try:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
    finally:
        app.dependency_overrides.clear()

def test_health_endpoint_db_failure(client: TestClient):
    def override_db():
        yield DummyDBFailure()

    from app.main import app
    app.dependency_overrides[get_db] = override_db
    try:
        response = client.get("/api/health")
        assert response.status_code == 503
        data = response.json()
        assert "Database connection error" in data["detail"]
    finally:
        app.dependency_overrides.clear()
