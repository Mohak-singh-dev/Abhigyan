"""
End-to-end integration tests for AI-based complaint classification (Task 3).
Tests:
- POST /api/complaints/classify (preview endpoint without persistence)
- Server-side AI advisory recording during complaint creation (POST /api/complaints)
- Verification that user choices (bureau, category, priority) are NEVER overridden by AI
- Classifier failure and missing artifact resilience during complaint creation
- Backward compatibility for existing records in database queries
"""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.auth import get_current_user
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

MOCK_ADMIN = User(
    id="u1",
    name="Dr. S. Mehta",
    email="member-sec@aicte-india.org",
    role="Admin",
    designation="Member Secretary & System Admin",
    bureau="All",
    status="Active",
)

MOCK_COMPLAINANT = User(
    id="u10",
    name="Aman Verma",
    email="aman.verma@student.edu.in",
    role="Complainant",
    designation="BTech Student",
    bureau="All",
    status="Active",
)


class MockDBSession:
    def __init__(self, complaints=None, institutions=None, users=None):
        self.complaints = list(complaints or [])
        self.institutions = list(institutions or [MOCK_INSTITUTION])
        self.users = list(users or [MOCK_ADMIN])
        self.added = []

    def query(self, model):
        class MockQuery:
            def __init__(self, data):
                self.data = list(data)

            def filter(self, *args, **kwargs):
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

        if model == Complaint:
            return MockQuery(self.complaints)
        elif model == Institution:
            return MockQuery(self.institutions)
        elif model == User:
            return MockQuery(self.users)
        return MockQuery([])

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


def test_classify_endpoint_success(client: TestClient):
    """POST /api/complaints/classify should return advisory predictions without persisting anything."""
    payload = {
        "title": "College charging capitation fee and withholding marksheet",
        "description": "The technical institute demands Rs 50,000 extra donation and refuses to return degree transcripts."
    }
    response = client.post("/api/complaints/classify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["category"] is not None
    assert data["bureau"] is not None
    assert data["priority"] is not None
    assert isinstance(data["confidence"], (float, int))
    assert 0.0 <= data["confidence"] <= 1.0
    assert isinstance(data["needsManualReview"], bool)
    assert "advisory" in data["advisoryNotice"].lower()
    assert data["modelVersion"] is not None


def test_classify_endpoint_preview_only_no_db_modification(client: TestClient):
    """Verify preview endpoint does NOT write to the database."""
    session = MockDBSession()
    app.dependency_overrides[get_db] = lambda: session
    try:
        payload = {
            "title": "Laboratory computers non-functional",
            "description": "All 40 computers in the CAD lab are out of order with broken screens."
        }
        response = client.post("/api/complaints/classify", json=payload)
        assert response.status_code == 200
        # Ensure session.add was never called
        assert len(session.added) == 0
        assert len(session.complaints) == 0
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_classify_endpoint_empty_input(client: TestClient):
    """Empty or whitespace-only inputs should return invalid_input with manual review recommended."""
    payload = {
        "title": "   ",
        "description": "   \n\t  "
    }
    response = client.post("/api/complaints/classify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "invalid_input"
    assert data["needsManualReview"] is True
    assert data["confidence"] == 0.0
    assert "empty_input" in data["reviewReasons"]


def test_classify_endpoint_custom_threshold(client: TestClient):
    """Confidence threshold parameter should be respected."""
    payload = {
        "title": "Delayed convocation certificate",
        "description": "Final degree certificate not received after one year.",
        "confidenceThreshold": 0.999
    }
    response = client.post("/api/complaints/classify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["needsManualReview"] is True
    assert any("low_category_confidence" in r for r in data["reviewReasons"])


def test_classify_endpoint_unauthenticated():
    """Unauthenticated access should be rejected with 401."""
    app.dependency_overrides.pop(get_current_user, None)
    try:
        with TestClient(app) as unauth_client:
            response = unauth_client.post("/api/complaints/classify", json={"title": "Test", "description": "Test description"})
            assert response.status_code == 401
    finally:
        app.dependency_overrides[get_current_user] = lambda: MOCK_ADMIN


def test_create_complaint_integrates_ai_without_overriding_user_choices(client: TestClient):
    """
    CRITICAL REQUIREMENT:
    User choices (bureau, category, priority) must NEVER be overridden by AI predictions.
    AI predictions are recorded strictly in the advisory metadata fields.
    """
    session = MockDBSession()
    app.dependency_overrides[get_db] = lambda: session
    try:
        payload = {
            "title": "Senior students hazing and physically assaulting junior freshers",
            "description": "Hostel seniors barged into room 204, assaulted students, and demanded money.",
            "bureau": "Approval",       # User deliberately picked Approval
            "category": "Curriculum",    # User deliberately picked Curriculum
            "priority": "Low",           # User deliberately picked Low
            "institutionId": "i1",
            "complainantType": "Student",
            "complainantName": "Aman Verma",
            "complainantEmail": "aman@student.edu.in",
        }
        response = client.post("/api/complaints", json=payload)
        assert response.status_code == 201
        data = response.json()

        # 1. User choices MUST remain intact
        assert data["bureau"] == "Approval"
        assert data["category"] == "Curriculum"
        assert data["priority"] == "Low"

        # 2. AI advisory predictions MUST be populated
        assert data["aiClassificationRun"] is True
        assert data["aiPredictedCategory"] is not None
        assert data["aiPredictedBureau"] is not None
        assert data["aiPredictedPriority"] is not None
        assert isinstance(data["aiConfidence"], (float, int))
        assert isinstance(data["aiNeedsManualReview"], bool)
        assert data["aiModelVersion"] is not None
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_create_complaint_graceful_fallback_when_classifier_errors(client: TestClient):
    """
    If the classifier service raises an error or is missing, complaint submission
    must NOT fail. Complaint is created successfully with aiClassificationRun=False.
    """
    session = MockDBSession()
    app.dependency_overrides[get_db] = lambda: session
    try:
        with patch("app.routers.complaints.classify_complaint", side_effect=RuntimeError("Simulated classifier failure")):
            payload = {
                "title": "Tuition fee overcharge",
                "description": "Institute collecting excess fee above state ceiling.",
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
            assert data["bureau"] == "PGRC"
            assert data["category"] == "Fee Regulation"
            assert data["aiClassificationRun"] is False
            assert data["aiNeedsManualReview"] is True
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_get_complaint_backward_compatibility_for_existing_records(client: TestClient):
    """
    Existing complaints in database that have NULL in AI columns
    should serialize without error.
    """
    legacy_complaint = Complaint(
        id="AB-2026-9999",
        institution_id="i1",
        bureau="Approval",
        category="Infrastructure",
        priority="Medium",
        status="Pending",
        officer="Suresh Patel",
        date="2026-10-01",
        due="2026-10-15",
        title="Roof leakage in library",
        description="Rainwater leaking through reading room ceiling.",
        # AI fields left as default None / False
        ai_predicted_category=None,
        ai_predicted_bureau=None,
        ai_predicted_priority=None,
        ai_confidence=None,
        ai_needs_manual_review=False,
        ai_model_version=None,
        ai_classification_run=False,
    )
    session = MockDBSession(complaints=[legacy_complaint])
    app.dependency_overrides[get_db] = lambda: session
    try:
        response = client.get(f"/api/complaints/{legacy_complaint.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "AB-2026-9999"
        assert data["aiPredictedCategory"] is None
        assert data["aiClassificationRun"] is False
    finally:
        app.dependency_overrides.pop(get_db, None)
