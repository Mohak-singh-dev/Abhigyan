from fastapi.testclient import TestClient
from app.database import get_db
from app.models.institution import Institution

SAMPLE_INSTITUTIONS = [
    Institution(
        id="i1",
        aicte_id="1-4821039",
        name="Sunrise Institute of Technology",
        city="Pune",
        state="Maharashtra",
        type="Engineering",
        approved="2009",
        contact_email="principal@sunrise-tech.edu.in",
        contact_phone="+91 20 2748 9901",
        risk_level="High"
    ),
    Institution(
        id="i2",
        aicte_id="1-3390412",
        name="Bharat College of Engineering",
        city="Lucknow",
        state="Uttar Pradesh",
        type="Engineering",
        approved="2004",
        contact_email="director@bharatengg.ac.in",
        contact_phone="+91 522 289 1102",
        risk_level="Moderate"
    )
]

class MockInstitutionQuery:
    def __init__(self, data):
        self.data = list(data)

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args):
        return self

    def all(self):
        return self.data

    def first(self):
        return self.data[0] if self.data else None

class MockDBSession:
    def __init__(self, institutions=None):
        self.institutions = institutions if institutions is not None else SAMPLE_INSTITUTIONS

    def query(self, model):
        if model == Institution:
            return MockInstitutionQuery(self.institutions)
        return MockInstitutionQuery([])

def test_list_institutions(client: TestClient):
    def override_db():
        yield MockDBSession(SAMPLE_INSTITUTIONS)

    from app.main import app
    app.dependency_overrides[get_db] = override_db
    try:
        response = client.get("/api/institutions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "i1"
        assert data[0]["aicteId"] == "1-4821039"
        assert data[0]["name"] == "Sunrise Institute of Technology"
    finally:
        app.dependency_overrides.clear()

def test_get_institution_by_id(client: TestClient):
    def override_db():
        yield MockDBSession([SAMPLE_INSTITUTIONS[0]])

    from app.main import app
    app.dependency_overrides[get_db] = override_db
    try:
        response = client.get("/api/institutions/i1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "i1"
        assert data["city"] == "Pune"
        assert data["state"] == "Maharashtra"
    finally:
        app.dependency_overrides.clear()

def test_get_institution_not_found(client: TestClient):
    def override_db():
        yield MockDBSession([])

    from app.main import app
    app.dependency_overrides[get_db] = override_db
    try:
        response = client.get("/api/institutions/nonexistent-id")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    finally:
        app.dependency_overrides.clear()
