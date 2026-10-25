import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.complaint import Complaint
from app.models.timeline import ComplaintTimeline
from app.models.institution import Institution
from app.auth import (
    hash_password,
    create_access_token,
    get_current_user,
)

# Test mock data
TEST_PASSWORD = "ValidSecurePass@2026"
TEST_HASH = hash_password(TEST_PASSWORD)

USER_ADMIN = User(
    id="u1",
    name="Dr. S. Mehta",
    email="member-sec@aicte-india.org",
    role="Admin",
    designation="Member Secretary & System Admin",
    bureau="All",
    avatar_text="SM",
    phone="+91 11 2958 1000",
    status="Active",
    department="Executive Administration",
    password_hash=TEST_HASH,
)

USER_BUREAU_ADMIN = User(
    id="u1b",
    name="Dr. Priya Nair",
    email="priya.nair@aicte-india.org",
    role="BureauAdmin",
    designation="Bureau Chief, PGRC",
    bureau="PGRC",
    avatar_text="PN",
    phone="+91 11 2958 1020",
    status="Active",
    department="Public Grievance Redressal Cell",
    password_hash=TEST_HASH,
)

USER_OFFICER_PGRC = User(
    id="u2",
    name="Rajesh Kumar",
    email="rajesh.kumar@aicte-india.org",
    role="Officer",
    designation="Senior Grievance Officer, PGRC",
    bureau="PGRC",
    avatar_text="RK",
    phone="+91 11 2958 1042",
    status="Active",
    department="PGRC Scrutiny Cell",
    password_hash=TEST_HASH,
)

USER_OFFICER_RB = User(
    id="u3",
    name="Anita Verma",
    email="anita.verma@aicte-india.org",
    role="Officer",
    designation="Director & Bureau Chief, RB",
    bureau="RB",
    avatar_text="AV",
    phone="+91 11 2958 1077",
    status="Active",
    department="Regulation Bureau",
    password_hash=TEST_HASH,
)

USER_COMPLAINANT = User(
    id="u0",
    name="Rohit Sharma",
    email="rohit.sharma@student.edu.in",
    role="Complainant",
    designation="Citizen Complainant",
    bureau="PGRC",
    avatar_text="RS",
    phone="+91 98765 43210",
    status="Active",
    department="Citizen",
    password_hash=TEST_HASH,
)

USER_INACTIVE = User(
    id="u_inactive",
    name="Inactive Officer",
    email="inactive@aicte-india.org",
    role="Officer",
    designation="Case Officer",
    bureau="Approval",
    avatar_text="IO",
    phone="+91 11 2958 0000",
    status="Inactive",
    department="Approval",
    password_hash=TEST_HASH,
)

USER_NO_PASSWORD = User(
    id="u_nopass",
    name="Legacy Officer",
    email="nopass@aicte-india.org",
    role="Officer",
    designation="Case Officer",
    bureau="Approval",
    avatar_text="LO",
    phone="+91 11 2958 0001",
    status="Active",
    department="Approval",
    password_hash=None,
)

ALL_TEST_USERS = [
    USER_ADMIN,
    USER_BUREAU_ADMIN,
    USER_OFFICER_PGRC,
    USER_OFFICER_RB,
    USER_COMPLAINANT,
    USER_INACTIVE,
    USER_NO_PASSWORD,
]

SAMPLE_COMPLAINT_PGRC = Complaint(
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
    title='Students report compulsory development charges exceeding fee norm',
    description='A group of third-year B.Tech students submitted a formal grievance regarding excessive fees.',
    complainant_type="Student",
    complainant_name="Rohit Sharma",
    complainant_email="rohit.sharma@student.edu.in",
    remarks=None,
    next_action="Examine counter affidavit",
    last_action_date="2026-10-05",
    created_at=datetime(2026, 10, 2, 10, 0, 0),
    updated_at=datetime(2026, 10, 2, 10, 0, 0),
)

SAMPLE_COMPLAINT_RB = Complaint(
    id="RB-2026-0141",
    institution_id="i1",
    institution_permanent_id="1-4821039",
    bureau="RB",
    category="Regulatory Compliance",
    priority="Critical",
    officer="Anita Verma",
    assigned_user_id="u3",
    status="Pending",
    date="2026-09-28",
    due="2026-10-12",
    title="Regulatory non-compliance in infrastructure",
    description="Inspection report notes severe non-compliance with required laboratories and workshop equipment.",
    complainant_type="Parent",
    complainant_name="Sunil Gupta",
    complainant_email="sunil.gupta@example.com",
    remarks=None,
    next_action="Issue formal show cause notice to management",
    last_action_date="2026-09-28",
    created_at=datetime(2026, 9, 28, 9, 0, 0),
    updated_at=datetime(2026, 9, 28, 9, 0, 0),
)

SAMPLE_COMPLAINT_RB_IN_PROGRESS = Complaint(
    id="RB-2026-0152",
    institution_id="i2",
    institution_permanent_id="1-3390412",
    bureau="RB",
    category="Faculty Norms",
    priority="High",
    officer="Anita Verma",
    assigned_user_id="u3",
    status="In Progress",
    date="2026-10-01",
    due="2026-10-25",
    title="Faculty shortage in CSE",
    description="Severe faculty shortage in Computer Science Department.",
    complainant_type="Whistleblower",
    complainant_name="Anonymous Faculty",
    complainant_email="whistle@example.org",
    remarks=None,
    next_action="Verify biometric logs",
    last_action_date="2026-10-01",
    created_at=datetime(2026, 10, 1, 10, 0, 0),
    updated_at=datetime(2026, 10, 1, 10, 0, 0),
)

ALL_SAMPLE_COMPLAINTS = [
    SAMPLE_COMPLAINT_PGRC,
    SAMPLE_COMPLAINT_RB,
    SAMPLE_COMPLAINT_RB_IN_PROGRESS,
]

class MockAuthDBSession:
    def __init__(self, users=None, complaints=None):
        self.users = list(users if users is not None else ALL_TEST_USERS)
        if complaints is not None:
            self.complaints = list(complaints)
        else:
            self.complaints = [
                Complaint(
                    id=c.id,
                    institution_id=c.institution_id,
                    institution_permanent_id=c.institution_permanent_id,
                    bureau=c.bureau,
                    category=c.category,
                    priority=c.priority,
                    officer=c.officer,
                    assigned_user_id=c.assigned_user_id,
                    status=c.status,
                    date=c.date,
                    due=c.due,
                    title=c.title,
                    description=c.description,
                    complainant_type=c.complainant_type,
                    complainant_name=c.complainant_name,
                    complainant_email=c.complainant_email,
                    remarks=c.remarks,
                    next_action=c.next_action,
                    last_action_date=c.last_action_date,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                )
                for c in ALL_SAMPLE_COMPLAINTS
            ]
        self.timelines = []

    def query(self, model):
        session = self

        class MockQuery:
            def __init__(self, items):
                self._items = items

            def filter(self, *criteria):
                filtered = list(self._items)
                for criterion in criteria:
                    criterion_str = str(criterion).lower()
                    # User filter by id
                    if "users.id =" in criterion_str or "users.id" in criterion_str and "=" in criterion_str:
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            filtered = [u for u in filtered if u.id == str(val)]
                    # User filter by email
                    elif "lower(users.email)" in criterion_str or "users.email =" in criterion_str:
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            filtered = [u for u in filtered if u.email.lower() == str(val).lower()]
                    # User filter by role
                    elif "users.role" in criterion_str:
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            filtered = [u for u in filtered if u.role.lower() == str(val).lower()]
                    # Complaint filter by id
                    elif "complaints.id" in criterion_str:
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            filtered = [c for c in filtered if c.id.lower() == str(val).lower()]
                    # Complaint filter by bureau
                    elif "complaints.bureau" in criterion_str:
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            filtered = [c for c in filtered if c.bureau.lower() == str(val).lower()]
                    # Complaint filter by complainant_email
                    elif "complaints.complainant_email" in criterion_str and "complaints.complainant_name" not in criterion_str:
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            filtered = [c for c in filtered if c.complainant_email and c.complainant_email.lower() == str(val).lower()]
                    # Complaint filter for Complainant (OR of email and name)
                    elif "or_" in criterion_str or ("complainant_email" in criterion_str and "complainant_name" in criterion_str):
                        # Filter to complainant Rohit
                        filtered = [c for c in filtered if (c.complainant_email and "rohit" in c.complainant_email.lower()) or (c.complainant_name and "rohit" in c.complainant_name.lower())]
                return MockQuery(filtered)

            def order_by(self, *args):
                return self

            def offset(self, n):
                return MockQuery(self._items[n:])

            def limit(self, n):
                return MockQuery(self._items[:n])

            def first(self):
                return self._items[0] if self._items else None

            def all(self):
                return list(self._items)

            def count(self):
                return len(self._items)

            def scalar(self):
                return len(self._items)

        if model is User:
            return MockQuery(self.users)
        elif model is Complaint:
            return MockQuery(self.complaints)
        elif model is ComplaintTimeline:
            return MockQuery(self.timelines)
        elif model is Institution:
            return MockQuery([])
        return MockQuery([0])

    def add(self, item):
        if isinstance(item, ComplaintTimeline):
            self.timelines.append(item)
        elif isinstance(item, Complaint):
            self.complaints.append(item)
        elif isinstance(item, User):
            self.users.append(item)

    def commit(self):
        pass

    def rollback(self):
        pass

    def refresh(self, item):
        pass

    def flush(self):
        pass

@pytest.fixture
def auth_mock_db():
    session = MockAuthDBSession()
    def override_get_db():
        yield session
    app.dependency_overrides[get_db] = override_get_db
    yield session
    app.dependency_overrides.pop(get_db, None)

# --- 1. Authentication Tests ---

def test_login_success(client: TestClient, auth_mock_db):
    """
    Test valid credentials return 200, JWT accessToken, expiresIn, and User profile.
    """
    payload = {"email": "member-sec@aicte-india.org", "password": TEST_PASSWORD}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"
    assert data["expiresIn"] > 0
    assert data["user"]["email"] == "member-sec@aicte-india.org"
    assert data["user"]["role"] == "Admin"

def test_login_invalid_password(client: TestClient, auth_mock_db):
    """
    Test invalid password returns 401 Unauthorized.
    """
    payload = {"email": "member-sec@aicte-india.org", "password": "WrongPassword123!"}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_login_nonexistent_email(client: TestClient, auth_mock_db):
    """
    Test unrecognized email returns 401 Unauthorized.
    """
    payload = {"email": "nonexistent@aicte-india.org", "password": TEST_PASSWORD}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_login_inactive_user(client: TestClient, auth_mock_db):
    """
    Test inactive user login returns 403 Forbidden.
    """
    payload = {"email": "inactive@aicte-india.org", "password": TEST_PASSWORD}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 403
    assert "Inactive" in response.json()["detail"]

def test_login_user_without_password_hash(client: TestClient, auth_mock_db):
    """
    Test user with NULL password_hash returns 401 with appropriate guidance.
    """
    payload = {"email": "nopass@aicte-india.org", "password": TEST_PASSWORD}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "no credentials configured" in response.json()["detail"]

# --- 2. Development Demo Login Tests ---

def test_demo_login_by_role(client: TestClient, auth_mock_db):
    """
    Test demo-login resolves active user by role in development.
    """
    payload = {"role": "Officer"}
    response = client.post("/api/auth/demo-login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data
    assert data["user"]["role"] == "Officer"

def test_demo_login_by_user_id(client: TestClient, auth_mock_db):
    """
    Test demo-login resolves active user by specific userId.
    """
    payload = {"userId": "u1b"}
    response = client.post("/api/auth/demo-login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["id"] == "u1b"
    assert data["user"]["role"] == "BureauAdmin"
    assert data["user"]["bureau"] == "PGRC"

def test_demo_login_disabled_when_configured(client: TestClient, auth_mock_db, monkeypatch):
    """
    Test demo-login returns 403 Forbidden when DEMO_AUTH_ENABLED is False or environment is production.
    """
    monkeypatch.setattr(settings, "DEMO_AUTH_ENABLED", False)
    payload = {"role": "Admin"}
    response = client.post("/api/auth/demo-login", json=payload)
    assert response.status_code == 403
    assert "Demo authentication is disabled" in response.json()["detail"]

# --- 3. Token Expiry and Invalid Token Tests ---

def test_unauthenticated_request_rejected(client: TestClient, auth_mock_db):
    """
    Test protected endpoints reject unauthenticated requests with 401 Unauthorized.
    """
    # Explicitly clear dependency override for get_current_user to test real bearer validation
    app.dependency_overrides.pop(get_current_user, None)
    try:
        response = client.get("/api/complaints")
        assert response.status_code == 401
        assert "Authentication token is required" in response.json()["detail"]
    finally:
        app.dependency_overrides[get_current_user] = lambda: USER_ADMIN

def test_invalid_token_rejected(client: TestClient, auth_mock_db):
    """
    Test invalid or forged JWT token returns 401 Unauthorized.
    """
    app.dependency_overrides.pop(get_current_user, None)
    try:
        headers = {"Authorization": "Bearer invalid.forged.token123"}
        response = client.get("/api/complaints", headers=headers)
        assert response.status_code == 401
        assert "Invalid authentication token" in response.json()["detail"]
    finally:
        app.dependency_overrides[get_current_user] = lambda: USER_ADMIN

def test_expired_token_rejected(client: TestClient, auth_mock_db):
    """
    Test expired JWT token returns 401 Unauthorized.
    """
    app.dependency_overrides.pop(get_current_user, None)
    try:
        # Create token that expired 10 minutes ago
        expired_token = create_access_token(
            {"sub": USER_ADMIN.id, "email": USER_ADMIN.email, "role": USER_ADMIN.role},
            expires_delta=timedelta(minutes=-10)
        )
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/complaints", headers=headers)
        assert response.status_code == 401
        assert "Session has expired" in response.json()["detail"]
    finally:
        app.dependency_overrides[get_current_user] = lambda: USER_ADMIN

def test_auth_me_endpoint_with_valid_token(client: TestClient, auth_mock_db):
    """
    Test GET /api/auth/me returns the profile of the authenticated user.
    """
    app.dependency_overrides.pop(get_current_user, None)
    try:
        token = create_access_token({"sub": USER_OFFICER_PGRC.id, "email": USER_OFFICER_PGRC.email, "role": USER_OFFICER_PGRC.role})
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == USER_OFFICER_PGRC.id
        assert data["role"] == "Officer"
        assert data["name"] == USER_OFFICER_PGRC.name
    finally:
        app.dependency_overrides[get_current_user] = lambda: USER_ADMIN

# --- 4. Role-Based Access Control (RBAC) Tests ---

def test_complainant_cannot_view_other_complainants_complaint(client: TestClient, auth_mock_db):
    """
    Test Complainant is forbidden (403) from accessing another person's complaint.
    """
    app.dependency_overrides[get_current_user] = lambda: USER_COMPLAINANT
    # RB complaint belongs to Sunil Gupta, not Rohit Sharma
    response = client.get(f"/api/complaints/{SAMPLE_COMPLAINT_RB.id}")
    assert response.status_code == 403
    assert "Complainants are only authorized to access complaints submitted by themselves" in response.json()["detail"]

def test_complainant_can_view_own_complaint(client: TestClient, auth_mock_db):
    """
    Test Complainant can access their own complaint.
    """
    app.dependency_overrides[get_current_user] = lambda: USER_COMPLAINANT
    # PGRC complaint belongs to Rohit Sharma
    response = client.get(f"/api/complaints/{SAMPLE_COMPLAINT_PGRC.id}")
    assert response.status_code == 200
    assert response.json()["id"] == SAMPLE_COMPLAINT_PGRC.id

def test_complainant_cannot_update_status(client: TestClient, auth_mock_db):
    """
    Test Complainant cannot update status on any complaint (403 Forbidden).
    """
    app.dependency_overrides[get_current_user] = lambda: USER_COMPLAINANT
    payload = {"status": "Resolved", "remarks": "I want to close my case"}
    response = client.patch(f"/api/complaints/{SAMPLE_COMPLAINT_PGRC.id}/status", json=payload)
    assert response.status_code == 403
    assert "Complainants cannot modify official docket status" in response.json()["detail"]

def test_complainant_cannot_assign_case(client: TestClient, auth_mock_db):
    """
    Test Complainant cannot assign or reassign any case (403 Forbidden).
    """
    app.dependency_overrides[get_current_user] = lambda: USER_COMPLAINANT
    payload = {"userId": "u2"}
    response = client.patch(f"/api/complaints/{SAMPLE_COMPLAINT_PGRC.id}/assign", json=payload)
    assert response.status_code == 403
    assert "Complainants do not hold administrative case assignment permissions" in response.json()["detail"]

def test_officer_cannot_assign_case(client: TestClient, auth_mock_db):
    """
    Test Handling Officer cannot directly reassign cases (403 Forbidden).
    """
    app.dependency_overrides[get_current_user] = lambda: USER_OFFICER_PGRC
    payload = {"userId": "u3"}
    response = client.patch(f"/api/complaints/{SAMPLE_COMPLAINT_PGRC.id}/assign", json=payload)
    assert response.status_code == 403
    assert "Handling Officers cannot directly reassign cases" in response.json()["detail"]

def test_officer_cannot_update_unassigned_other_bureau_case(client: TestClient, auth_mock_db):
    """
    Test Handling Officer in PGRC cannot modify status of an RB Bureau case (403 Forbidden).
    """
    app.dependency_overrides[get_current_user] = lambda: USER_OFFICER_PGRC
    payload = {"status": "In Progress"}
    # RB complaint belongs to RB bureau and officer Anita Verma
    response = client.patch(f"/api/complaints/{SAMPLE_COMPLAINT_RB.id}/status", json=payload)
    assert response.status_code == 403
    assert "neither assigned" in response.json()["detail"]

def test_officer_can_update_status_on_assigned_case(client: TestClient, auth_mock_db):
    """
    Test Handling Officer can update status on their assigned case within permitted transitions.
    """
    app.dependency_overrides[get_current_user] = lambda: USER_OFFICER_PGRC
    payload = {"status": "Resolved", "remarks": "Investigation complete"}
    response = client.patch(f"/api/complaints/{SAMPLE_COMPLAINT_PGRC.id}/status", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "Resolved"

def test_bureau_admin_cross_bureau_access_blocked(client: TestClient, auth_mock_db):
    """
    Test Bureau Admin (PGRC) is forbidden (403) from modifying or assigning RB Bureau cases.
    """
    app.dependency_overrides[get_current_user] = lambda: USER_BUREAU_ADMIN
    # 1. Status update cross-bureau
    status_payload = {"status": "In Progress"}
    response = client.patch(f"/api/complaints/{SAMPLE_COMPLAINT_RB.id}/status", json=status_payload)
    assert response.status_code == 403
    assert "jurisdiction is PGRC" in response.json()["detail"]

    # 2. Case assignment cross-bureau
    assign_payload = {"officer": "Rajesh Kumar"}
    response = client.patch(f"/api/complaints/{SAMPLE_COMPLAINT_RB.id}/assign", json=assign_payload)
    assert response.status_code == 403
    assert "authorized only for PGRC cases" in response.json()["detail"]

def test_bureau_admin_cannot_transfer_to_other_bureau(client: TestClient, auth_mock_db):
    """
    Test Bureau Admin cannot transfer a case to a different Bureau (403 Forbidden).
    """
    app.dependency_overrides[get_current_user] = lambda: USER_BUREAU_ADMIN
    payload = {"bureau": "Approval"}
    response = client.patch(f"/api/complaints/{SAMPLE_COMPLAINT_PGRC.id}/assign", json=payload)
    assert response.status_code == 403
    assert "can only transfer cases originating in their authorized Bureau" in response.json()["detail"]

def test_admin_system_wide_permissions(client: TestClient, auth_mock_db):
    """
    Test System Admin possesses system-wide permissions across Bureaus and assignments.
    """
    app.dependency_overrides[get_current_user] = lambda: USER_ADMIN
    # Status transition on RB case
    status_payload = {"status": "Resolved", "remarks": "Executive Admin direct intervention"}
    response = client.patch(f"/api/complaints/{SAMPLE_COMPLAINT_RB_IN_PROGRESS.id}/status", json=status_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "Resolved"

    # Cross-bureau assignment on RB case
    assign_payload = {"officer": "Anita Verma", "bureau": "RB", "reason": "System administrative reassignment"}
    response = client.patch(f"/api/complaints/{SAMPLE_COMPLAINT_RB.id}/assign", json=assign_payload)
    assert response.status_code == 200

# --- 5. Timeline Actor Integrity Tests ---

def test_timeline_actor_integrity_cannot_be_spoofed(client: TestClient, auth_mock_db):
    """
    Test that client-supplied `by`, `role`, or `userId` in the request body cannot spoof
    the timeline audit record. The actor must be derived strictly from the authenticated token user.
    """
    app.dependency_overrides[get_current_user] = lambda: USER_OFFICER_PGRC
    spoofed_payload = {
        "status": "Resolved",
        "by": "Member Secretary Dr. Mehta",
        "role": "Admin",
        "userId": "u1",
        "remarks": "Fraudulent actor spoof attempt"
    }
    response = client.patch(f"/api/complaints/{SAMPLE_COMPLAINT_PGRC.id}/status", json=spoofed_payload)
    assert response.status_code == 200

    # Inspect the newly created timeline event in the mock session
    latest_event = auth_mock_db.timelines[-1]
    assert latest_event.user_id == USER_OFFICER_PGRC.id
    assert USER_OFFICER_PGRC.name in latest_event.by
    assert latest_event.role == USER_OFFICER_PGRC.role
    assert "Dr. Mehta" not in latest_event.by
    assert latest_event.role != "Admin"
