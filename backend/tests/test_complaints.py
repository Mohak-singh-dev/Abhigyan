import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.database import get_db
from app.models.complaint import Complaint
from app.models.institution import Institution
from app.models.user import User

MOCK_INSTITUTION = Institution(
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
)

MOCK_USER = User(
    id="u2",
    name="Rajesh Kumar",
    email="rajesh.kumar@aicte-india.org",
    role="Officer",
    designation="Senior Grievance Officer, PGRC",
    bureau="PGRC",
    avatar_text="RK",
    phone="+91 11 2958 1042",
    status="Active",
    department="PGRC Scrutiny Cell"
)

SAMPLE_COMPLAINTS = [
    Complaint(
        id="PGRC-2026-0873",
        institution_id="i1",
        institution_permanent_id="1-4821039",
        bureau="PGRC",
        category="Fee Regulation",
        priority="High",
        officer="Rajesh Kumar",
        assigned_user_id="u2",
        status="In Progress",
        date="2026-10-02",
        due="2026-10-30",
        title='Students report compulsory "development charges" exceeding fee norm',
        description='A group of third-year B.Tech students submitted a formal grievance stating the 2026-27 fee notice exceeds the approved schedule by Rs 35,000 under mandatory development charges.',
        complainant_type="Student",
        complainant_name="Rohit Sharma",
        complainant_email="rohit.sharma@student.edu.in",
        remarks=None,
        next_action="Examine institution counter-affidavit and verify official registers",
        last_action_date="2026-10-05",
        created_at=datetime(2026, 10, 2, 10, 0, 0),
        updated_at=datetime(2026, 10, 2, 10, 0, 0),
    ),
    Complaint(
        id="RB-2026-0141",
        institution_id="i1",
        institution_permanent_id="1-4821039",
        bureau="RB",
        category="Fee Regulation",
        priority="Critical",
        officer="Anita Verma",
        assigned_user_id="u3",
        status="Pending",
        date="2026-09-28",
        due="2026-10-12",
        title="Excess tuition fee collected above approved regulatory cap",
        description="Parents allege the institute collects tuition roughly 40% above the fee approved by the state Fee Regulatory Committee, with no formal receipts issued for the additional amount.",
        complainant_type="Parent",
        complainant_name="S. Sundaram",
        complainant_email="citizen.grievance@aicte-portal.in",
        remarks=None,
        next_action="Jurisdiction verification and preliminary scrutiny by RB Cell",
        last_action_date="2026-09-28",
        created_at=datetime(2026, 9, 28, 10, 0, 0),
        updated_at=datetime(2026, 9, 28, 10, 0, 0),
    )
]

class MockComplaintQuery:
    def __init__(self, data):
        self.data = list(data)

    def filter(self, *args, **kwargs):
        # Basic filter simulation for unit tests
        return self

    def order_by(self, *args):
        return self

    def offset(self, n):
        self.data = self.data[n:]
        return self

    def limit(self, n):
        self.data = self.data[:n]
        return self

    def count(self):
        return len(self.data)

    def all(self):
        return self.data

    def first(self):
        return self.data[0] if self.data else None

class MockComplaintDBSession:
    def __init__(self, complaints=None, institutions=None, users=None):
        self.complaints = list(complaints) if complaints is not None else list(SAMPLE_COMPLAINTS)
        self.institutions = list(institutions) if institutions is not None else [MOCK_INSTITUTION]
        self.users = list(users) if users is not None else [MOCK_USER]
        self.added = []

    def query(self, model):
        if model == Complaint:
            return MockComplaintQuery(self.complaints)
        elif model == Institution:
            return MockComplaintQuery(self.institutions)
        elif model == User:
            return MockComplaintQuery(self.users)
        return MockComplaintQuery([])

    def add(self, obj):
        self.added.append(obj)
        if isinstance(obj, Complaint):
            self.complaints.append(obj)

    def commit(self):
        pass

    def rollback(self):
        pass

    def flush(self):
        pass

    def refresh(self, obj):
        pass

def test_create_complaint_success(client: TestClient):
    """
    Test successful complaint creation with default officer routing and SLA generation.
    """
    from app.main import app
    session = MockComplaintDBSession()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        payload = {
            "title": "Unapproved collection of laboratory maintenance fee",
            "description": "The institution has issued a circular demanding an unauthorized laboratory maintenance fee of Rs 15,000.",
            "bureau": "PGRC",
            "category": "Fee Regulation",
            "priority": "High",
            "institutionId": "i1",
            "complainantType": "Student",
            "complainantName": "Aman Verma",
            "complainantEmail": "aman@student.edu.in",
        }
        response = client.post("/api/complaints", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["bureau"] == "PGRC"
        assert data["priority"] == "High"
        assert data["institutionId"] == "i1"
        assert data["status"] == "Pending"
        assert data["officer"] == "Rajesh Kumar"
        assert data["id"].startswith("PGRC-2026-")
        assert data["due"] is not None
        assert data["institutionPermanentId"] == "1-4821039"
    finally:
        app.dependency_overrides.clear()

def test_create_complaint_validation_invalid_bureau(client: TestClient):
    """
    Test validation failure when invalid Bureau is submitted.
    """
    payload = {
        "title": "Invalid bureau test case",
        "description": "Testing that an unrecognized bureau triggers Pydantic schema validation error.",
        "bureau": "UNKNOWN_BUREAU",
        "category": "Fee Regulation",
        "priority": "High",
        "institutionId": "i1",
    }
    response = client.post("/api/complaints", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("bureau" in str(e["loc"]).lower() for e in errors)

def test_create_complaint_validation_invalid_priority(client: TestClient):
    """
    Test validation failure when invalid Priority is submitted.
    """
    payload = {
        "title": "Invalid priority test case",
        "description": "Testing that an unrecognized priority triggers schema validation error.",
        "bureau": "PGRC",
        "category": "Fee Regulation",
        "priority": "SuperUrgent",
        "institutionId": "i1",
    }
    response = client.post("/api/complaints", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("priority" in str(e["loc"]).lower() for e in errors)

def test_create_complaint_validation_short_title_and_description(client: TestClient):
    """
    Test validation failure when title or description is too short.
    """
    payload = {
        "title": "Hi",
        "description": "Short",
        "bureau": "PGRC",
        "category": "Fee Regulation",
        "priority": "Low",
        "institutionId": "i1",
    }
    response = client.post("/api/complaints", json=payload)
    assert response.status_code == 422

def test_create_complaint_institution_not_found(client: TestClient):
    """
    Test 400 Bad Request when referenced institution does not exist.
    """
    from app.main import app
    session = MockComplaintDBSession(institutions=[])

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        payload = {
            "title": "Complaint against non-existent institution",
            "description": "This complaint references an invalid institution ID that does not exist in registry.",
            "bureau": "RB",
            "category": "Infrastructure",
            "priority": "Medium",
            "institutionId": "nonexistent_inst_id",
        }
        response = client.post("/api/complaints", json=payload)
        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()

def test_list_complaints(client: TestClient):
    """
    Test listing complaints with paginated response envelope.
    """
    from app.main import app
    session = MockComplaintDBSession(complaints=SAMPLE_COMPLAINTS)

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        response = client.get("/api/complaints?page=1&pageSize=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pageSize" in data
        assert "totalPages" in data
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["id"] == "PGRC-2026-0873"
    finally:
        app.dependency_overrides.clear()

def test_get_complaint_by_id(client: TestClient):
    """
    Test retrieving single complaint by ID (case-insensitive).
    """
    from app.main import app
    session = MockComplaintDBSession(complaints=[SAMPLE_COMPLAINTS[0]])

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        # Test case-insensitive lookup
        response = client.get("/api/complaints/pgrc-2026-0873")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "PGRC-2026-0873"
        assert data["bureau"] == "PGRC"
        assert data["officer"] == "Rajesh Kumar"
    finally:
        app.dependency_overrides.clear()

def test_get_complaint_not_found(client: TestClient):
    """
    Test 404 response when complaint ID does not exist.
    """
    from app.main import app
    session = MockComplaintDBSession(complaints=[])

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        response = client.get("/api/complaints/UNKNOWN-2026-9999")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    finally:
        app.dependency_overrides.clear()
