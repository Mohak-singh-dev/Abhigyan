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
    verify_password,
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
    complainant_user_id="u0",
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

SAMPLE_COMPLAINT_PGRC_UNASSIGNED = Complaint(
    id="PGRC-2026-0999",
    institution_id="i1",
    institution_permanent_id="1-4821039",
    bureau="PGRC",
    category="Fee Regulation",
    priority="Medium",
    officer="Unassigned",
    assigned_user_id=None,
    status="Pending",
    date="2026-10-05",
    due="2026-11-05",
    title="Unassigned PGRC complaint",
    description="Complaint in PGRC bureau that is not assigned to Rajesh Kumar",
    complainant_type="Student",
    complainant_name="Another Student",
    complainant_email="another@student.edu.in",
    remarks=None,
    next_action="Jurisdiction verification",
    last_action_date="2026-10-05",
    created_at=datetime(2026, 10, 5, 10, 0, 0),
    updated_at=datetime(2026, 10, 5, 10, 0, 0),
)

TEST_INSTITUTION = Institution(
    id="i1",
    aicte_id="1-4821039",
    name="Delhi Institute of Advanced Technology",
    state="Delhi",
    city="New Delhi",
    type="Engineering & Technology",
    approved="Yes",
)

ALL_SAMPLE_COMPLAINTS = [
    SAMPLE_COMPLAINT_PGRC,
    SAMPLE_COMPLAINT_RB,
    SAMPLE_COMPLAINT_RB_IN_PROGRESS,
    SAMPLE_COMPLAINT_PGRC_UNASSIGNED,
]

class MockAuthDBSession:
    def __init__(self, users=None, complaints=None, institutions=None):
        self.users = list(users if users is not None else ALL_TEST_USERS)
        self.institutions = list(institutions if institutions is not None else [TEST_INSTITUTION])
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
                    complainant_user_id=getattr(c, "complainant_user_id", None),
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
                    if "users.id =" in criterion_str or ("users.id" in criterion_str and "=" in criterion_str):
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
                    # User filter by name
                    elif "lower(users.name)" in criterion_str or "users.name" in criterion_str:
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            filtered = [u for u in filtered if u.name.lower() == str(val).lower()]
                    # Institution filter by id
                    elif "institutions.id" in criterion_str:
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            filtered = [i for i in filtered if i.id.lower() == str(val).lower()]
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
                    # Officer filter (OR of officer name and assigned_user_id)
                    elif "complaints.officer" in criterion_str or "complaints.assigned_user_id" in criterion_str:
                        clauses = getattr(criterion, "clauses", [criterion])
                        targets = []
                        for cl in clauses:
                            v = getattr(getattr(cl, "right", None), "value", None)
                            if v:
                                targets.append(str(v).strip().lower())
                        if targets:
                            filtered = [
                                c for c in filtered
                                if hasattr(c, "officer") and (
                                    (c.officer and c.officer.lower() in targets) or
                                    (c.assigned_user_id and c.assigned_user_id.lower() in targets)
                                )
                            ]
                    # Complaint filter by complainant_email alone
                    elif "complaints.complainant_email" in criterion_str and "complaints.complainant_user_id" not in criterion_str and "or_" not in criterion_str and "complaints.complainant_name" not in criterion_str:
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            filtered = [c for c in filtered if c.complainant_email and c.complainant_email.lower() == str(val).lower()]
                    # Complaint filter for Complainant (OR of complainant_user_id and complainant_email)
                    elif "complainant_user_id" in criterion_str or "complainant_email" in criterion_str or "or_" in criterion_str:
                        user_id_val = None
                        email_val = None
                        clauses = getattr(criterion, "clauses", [criterion])
                        for cl in clauses:
                            left_name = str(getattr(cl, "left", "")).lower()
                            val = getattr(getattr(cl, "right", None), "value", None)
                            if val:
                                if "user_id" in left_name:
                                    user_id_val = str(val).strip().lower()
                                elif "email" in left_name:
                                    email_val = str(val).strip().lower()
                        if user_id_val or email_val:
                            filtered = [
                                c for c in filtered
                                if (user_id_val and getattr(c, "complainant_user_id", None) and str(c.complainant_user_id).lower() == user_id_val)
                                or (email_val and getattr(c, "complainant_email", None) and str(c.complainant_email).lower() == email_val)
                            ]
                        else:
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
            return MockQuery(self.institutions)
        return MockQuery([0])

    def add(self, item):
        if isinstance(item, ComplaintTimeline):
            if not getattr(item, "id", None):
                item.id = len(self.timelines) + 1
            if not getattr(item, "created_at", None):
                item.created_at = datetime.now(timezone.utc)
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

def test_officer_cannot_view_or_update_unassigned_same_bureau_case(client: TestClient, auth_mock_db):
    """
    Regression Test: An Officer cannot view, update status, or add remarks to an unassigned case,
    even if the case belongs to the Officer's own Bureau (PGRC).
    """
    app.dependency_overrides[get_current_user] = lambda: USER_OFFICER_PGRC
    unassigned_id = SAMPLE_COMPLAINT_PGRC_UNASSIGNED.id

    # 1. View attempt
    view_res = client.get(f"/api/complaints/{unassigned_id}")
    assert view_res.status_code == 403
    assert "neither assigned" in view_res.json()["detail"]

    # 2. Status update attempt
    status_res = client.patch(f"/api/complaints/{unassigned_id}/status", json={"status": "In Progress"})
    assert status_res.status_code == 403
    assert "neither assigned" in status_res.json()["detail"]

    # 3. Add timeline note attempt
    timeline_res = client.post(f"/api/complaints/{unassigned_id}/timeline", json={"note": "Unauthorized note"})
    assert timeline_res.status_code == 403
    assert "neither assigned" in timeline_res.json()["detail"]

def test_officer_can_view_and_add_timeline_on_assigned_case(client: TestClient, auth_mock_db):
    """
    Regression Test: An Officer can access and add timeline notes to their explicitly assigned case.
    """
    app.dependency_overrides[get_current_user] = lambda: USER_OFFICER_PGRC
    assigned_id = SAMPLE_COMPLAINT_PGRC.id

    # 1. View succeeds
    view_res = client.get(f"/api/complaints/{assigned_id}")
    assert view_res.status_code == 200
    assert view_res.json()["id"] == assigned_id

    # 2. Timeline note succeeds
    timeline_res = client.post(f"/api/complaints/{assigned_id}/timeline", json={"note": "Officer verification in progress."})
    assert timeline_res.status_code == 201
    data = timeline_res.json()
    assert data["complaintId"] == assigned_id
    assert "Rajesh Kumar" in data["by"]
    assert data["note"] == "Officer verification in progress."

def test_complainant_can_add_timeline_on_own_case_but_not_others(client: TestClient, auth_mock_db):
    """
    Regression Test: A Complainant can add supplementary remarks to their own case,
    but is strictly forbidden (403) from accessing or mutating another complainant's docket.
    """
    app.dependency_overrides[get_current_user] = lambda: USER_COMPLAINANT
    own_id = SAMPLE_COMPLAINT_PGRC.id
    other_id = SAMPLE_COMPLAINT_RB.id

    # 1. Own case timeline note succeeds
    own_res = client.post(f"/api/complaints/{own_id}/timeline", json={"note": "Submitted additional fee receipts."})
    assert own_res.status_code == 201
    assert own_res.json()["complaintId"] == own_id
    assert "Rohit Sharma" in own_res.json()["by"]

    # 2. Other case timeline note is denied (403)
    other_res = client.post(f"/api/complaints/{other_id}/timeline", json={"note": "Unauthorized intruder note."})
    assert other_res.status_code == 403
    assert "Complainants are only authorized to access complaints submitted by themselves" in other_res.json()["detail"]

def test_explicit_demo_login_allowed_in_development(client: TestClient, auth_mock_db):
    """
    Test explicit demo login succeeds in permitted development configuration.
    """
    orig_demo = settings.DEMO_AUTH_ENABLED
    orig_env = settings.ENVIRONMENT
    settings.DEMO_AUTH_ENABLED = True
    settings.ENVIRONMENT = "development"
    try:
        response = client.post("/api/auth/demo-login", json={"role": "Officer"})
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "Officer"
        assert data["user"]["name"] == "Rajesh Kumar"
        assert data["accessToken"] is not None
    finally:
        settings.DEMO_AUTH_ENABLED = orig_demo
        settings.ENVIRONMENT = orig_env

def test_demo_login_rejected_when_disabled_or_production(client: TestClient, auth_mock_db):
    """
    Regression Test: POST /api/auth/demo-login is strictly rejected (403 Forbidden)
    when DEMO_AUTH_ENABLED is False or ENVIRONMENT is production.
    """
    orig_demo = settings.DEMO_AUTH_ENABLED
    orig_env = settings.ENVIRONMENT
    try:
        # Case 1: DEMO_AUTH_ENABLED = False
        settings.DEMO_AUTH_ENABLED = False
        settings.ENVIRONMENT = "development"
        res1 = client.post("/api/auth/demo-login", json={"role": "Admin"})
        assert res1.status_code == 403
        assert "Demo authentication is disabled" in res1.json()["detail"]

        # Case 2: ENVIRONMENT = "production"
        settings.DEMO_AUTH_ENABLED = True
        settings.ENVIRONMENT = "production"
        res2 = client.post("/api/auth/demo-login", json={"role": "Admin"})
        assert res2.status_code == 403
        assert "Demo authentication is disabled" in res2.json()["detail"]
    finally:
        settings.DEMO_AUTH_ENABLED = orig_demo
        settings.ENVIRONMENT = orig_env


def test_handling_officer_reassignment_persists_and_synchronizes_access(client: TestClient, auth_mock_db):
    """
    Regression Test (Bug 3):
    1. System Admin reassigns case from Officer A (Rajesh Kumar, u2) to Officer B (Anita Verma, u3).
    2. Backend persists assigned_user_id and officer in database and records timeline event.
    3. Officer B (new assignee) can retrieve the case and view it in their worklist.
    4. Officer A (previous assignee) can NO LONGER access or mutate the case (403 Forbidden).
    5. System Admin retrieves the case and confirms updated handling officer.
    """
    app.dependency_overrides[get_current_user] = lambda: USER_ADMIN
    case_id = SAMPLE_COMPLAINT_PGRC.id

    # 1. System Admin reassigns case from Rajesh Kumar to Anita Verma
    assign_payload = {
        "userId": USER_OFFICER_RB.id,
        "officer": USER_OFFICER_RB.name,
        "reason": "Administrative workload rebalance between PGRC officers."
    }
    assign_res = client.patch(f"/api/complaints/{case_id}/assign", json=assign_payload)
    assert assign_res.status_code == 200
    res_data = assign_res.json()
    assert res_data["officer"] == USER_OFFICER_RB.name
    assert res_data["assignedUserId"] == USER_OFFICER_RB.id

    # Verify persistence in mock database session
    db_case = [c for c in auth_mock_db.complaints if c.id == case_id][0]
    assert db_case.officer == USER_OFFICER_RB.name
    assert db_case.assigned_user_id == USER_OFFICER_RB.id

    # 2. Officer B (Anita Verma) logs in and accesses the case
    app.dependency_overrides[get_current_user] = lambda: USER_OFFICER_RB
    officer_b_get = client.get(f"/api/complaints/{case_id}")
    assert officer_b_get.status_code == 200
    assert officer_b_get.json()["officer"] == USER_OFFICER_RB.name

    # Officer B worklist includes this case
    officer_b_list = client.get("/api/complaints")
    assert officer_b_list.status_code == 200
    b_case_ids = [item["id"] for item in officer_b_list.json()["items"]]
    assert case_id in b_case_ids

    # Officer B can add timeline remarks
    officer_b_note = client.post(
        f"/api/complaints/{case_id}/timeline",
        json={"note": "Anita Verma: Case dossier reviewed and preliminary scrutiny initiated."}
    )
    assert officer_b_note.status_code == 201
    assert "Anita Verma" in officer_b_note.json()["by"]

    # 3. Officer A (Rajesh Kumar) logs in and attempts to access the case
    app.dependency_overrides[get_current_user] = lambda: USER_OFFICER_PGRC
    officer_a_get = client.get(f"/api/complaints/{case_id}")
    assert officer_a_get.status_code == 403
    assert "neither assigned" in officer_a_get.json()["detail"].lower()

    # Officer A worklist excludes this case
    officer_a_list = client.get("/api/complaints")
    assert officer_a_list.status_code == 200
    a_case_ids = [item["id"] for item in officer_a_list.json()["items"]]
    assert case_id not in a_case_ids

    # Officer A cannot add timeline remarks
    officer_a_note = client.post(
        f"/api/complaints/{case_id}/timeline",
        json={"note": "Rajesh Kumar: Attempting unauthorized remark on reassigned case."}
    )
    assert officer_a_note.status_code == 403

    # 4. System Admin sees updated Handling Officer
    app.dependency_overrides[get_current_user] = lambda: USER_ADMIN
    admin_get = client.get(f"/api/complaints/{case_id}")
    assert admin_get.status_code == 200
    assert admin_get.json()["officer"] == USER_OFFICER_RB.name
    assert admin_get.json()["assignedUserId"] == USER_OFFICER_RB.id


def test_officer_and_bureau_admin_assignment_authorization_rules(client: TestClient, auth_mock_db):
    """
    Regression Test:
    - Officer cannot assign or reassign cases (403 Forbidden).
    - Complainant cannot assign cases (403 Forbidden).
    - Bureau Admin cannot assign cases outside authorized Bureau (403 Forbidden).
    - Bureau Admin cannot assign case to officer in another Bureau (403 Forbidden).
    - Bureau Admin can reassign cases within authorized Bureau to active Bureau officer.
    """
    # 1. Officer attempt
    app.dependency_overrides[get_current_user] = lambda: USER_OFFICER_PGRC
    res_officer = client.patch(
        f"/api/complaints/{SAMPLE_COMPLAINT_PGRC.id}/assign",
        json={"userId": "u3", "reason": "Officer self-reassignment attempt"}
    )
    assert res_officer.status_code == 403
    assert "cannot directly reassign cases" in res_officer.json()["detail"].lower()

    # 2. Complainant attempt
    app.dependency_overrides[get_current_user] = lambda: USER_COMPLAINANT
    res_complainant = client.patch(
        f"/api/complaints/{SAMPLE_COMPLAINT_PGRC.id}/assign",
        json={"userId": "u2", "reason": "Complainant assignment attempt"}
    )
    assert res_complainant.status_code == 403

    # 3. Bureau Admin attempts to reassign case originating in another bureau (RB)
    app.dependency_overrides[get_current_user] = lambda: USER_BUREAU_ADMIN
    res_cross_bureau_case = client.patch(
        f"/api/complaints/{SAMPLE_COMPLAINT_RB.id}/assign",
        json={"userId": "u2", "reason": "PGRC Admin managing RB case"}
    )
    assert res_cross_bureau_case.status_code == 403
    assert "authorized only for pgrc" in res_cross_bureau_case.json()["detail"].lower()

    # 4. Bureau Admin attempts to assign PGRC case to an officer in RB bureau (Anita Verma, u3)
    res_cross_officer = client.patch(
        f"/api/complaints/{SAMPLE_COMPLAINT_PGRC.id}/assign",
        json={"userId": USER_OFFICER_RB.id, "reason": "Assigning to RB officer"}
    )
    assert res_cross_officer.status_code == 403
    assert "cannot assign case to officer in rb bureau" in res_cross_officer.json()["detail"].lower()

    # 5. Bureau Admin assigns PGRC case to an officer in PGRC bureau
    res_valid = client.patch(
        f"/api/complaints/{SAMPLE_COMPLAINT_PGRC.id}/assign",
        json={"userId": USER_OFFICER_PGRC.id, "reason": "Valid PGRC reassignment"}
    )
    assert res_valid.status_code == 200
    assert res_valid.json()["officer"] == USER_OFFICER_PGRC.name


# --- 13. Phase 1 Complainant Registration & Ownership Tests ---

def test_registration_success(client: TestClient, auth_mock_db):
    """
    Test public registration succeeds with valid payload:
    - Returns 201 Created with JWT accessToken and tokenType="bearer"
    - User has role='Complainant', bureau='All', status='Active'
    - User is persisted in database with a generated ID starting with 'c-'
    """
    payload = {
        "name": "Pooja Sharma",
        "email": "pooja.sharma@example.com",
        "password": "ValidSecurePassword@2026",
        "phone": "+91 98765 11111",
        "complainantType": "Student",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"
    user_data = data["user"]
    assert user_data["name"] == "Pooja Sharma"
    assert user_data["email"] == "pooja.sharma@example.com"
    assert user_data["role"] == "Complainant"
    assert user_data["bureau"] == "All"
    assert user_data["status"] == "Active"
    assert user_data["id"].startswith("c-")

    # Confirm user is in database
    db_user = [u for u in auth_mock_db.users if u.email == "pooja.sharma@example.com"]
    assert len(db_user) == 1
    assert db_user[0].role == "Complainant"


def test_registration_duplicate_email(client: TestClient, auth_mock_db):
    """
    Test registration rejects duplicate email with 409 Conflict.
    """
    payload = {
        "name": "Another Rohit",
        "email": "rohit.sharma@student.edu.in",  # already exists in seed/mock users
        "password": "Password123!",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


def test_registration_invalid_input(client: TestClient, auth_mock_db):
    """
    Test registration rejects invalid email, short name, and short password with 422.
    """
    # 1. Invalid email
    res1 = client.post("/api/auth/register", json={
        "name": "Valid Name",
        "email": "not-an-email",
        "password": "ValidPassword123!",
    })
    assert res1.status_code == 422

    # 2. Short name (<2 chars)
    res2 = client.post("/api/auth/register", json={
        "name": "X",
        "email": "valid@example.com",
        "password": "ValidPassword123!",
    })
    assert res2.status_code == 422

    # 3. Short password (<6 chars)
    res3 = client.post("/api/auth/register", json={
        "name": "Valid Name",
        "email": "valid@example.com",
        "password": "123",
    })
    assert res3.status_code == 422

    # 4. Invalid complainantType
    res4 = client.post("/api/auth/register", json={
        "name": "Valid Name",
        "email": "valid@example.com",
        "password": "ValidPassword123!",
        "complainantType": "IllegalType",
    })
    assert res4.status_code == 422
    assert "complainanttype" in res4.text.lower()


def test_registration_valid_and_invalid_complainant_types(client: TestClient, auth_mock_db):
    """
    Test registration strictly validates complainantType:
    - Accepts each supported type: Student, Faculty, Parent, Whistleblower, General Public
    - Normalizes case-insensitively and sets appropriate designation
    - Defaults to 'General Public' when omitted
    - Rejects unsupported types (e.g. 'Admin', 'Officer', 'Arbitrary') with 422
    """
    supported_types = ["Student", "Faculty", "Parent", "Whistleblower", "General Public"]
    for i, c_type in enumerate(supported_types):
        res = client.post("/api/auth/register", json={
            "name": f"Valid Type User {i}",
            "email": f"type_user_{i}@example.com",
            "password": "ValidPassword123!",
            "complainantType": c_type,
        })
        assert res.status_code == 201, f"Failed for supported complainantType: {c_type}"
        data = res.json()
        assert data["user"]["designation"] == f"{c_type} Complainant"

    # Default when complainantType is omitted
    res_default = client.post("/api/auth/register", json={
        "name": "Omitted Type User",
        "email": "omitted_type@example.com",
        "password": "ValidPassword123!",
    })
    assert res_default.status_code == 201
    assert res_default.json()["user"]["designation"] == "General Public Complainant"

    # Invalid complainant types should be rejected with 422
    for invalid_type in ["Admin", "Officer", "Hacker", "Corporation"]:
        res_inv = client.post("/api/auth/register", json={
            "name": "Invalid Type User",
            "email": f"inv_{invalid_type.lower()}@example.com",
            "password": "ValidPassword123!",
            "complainantType": invalid_type,
        })
        assert res_inv.status_code == 422


def test_registration_password_hashing(client: TestClient, auth_mock_db):
    """
    Test registered user's password is encrypted with secure bcrypt hash, not stored in plaintext.
    """
    raw_pass = "MySecretPass@999"
    payload = {
        "name": "Hash Check User",
        "email": "hashcheck@example.com",
        "password": raw_pass,
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201

    db_user = [u for u in auth_mock_db.users if u.email == "hashcheck@example.com"][0]
    assert db_user.password_hash != raw_pass
    assert db_user.password_hash.startswith("$2b$") or db_user.password_hash.startswith("$2a$")
    assert verify_password(raw_pass, db_user.password_hash) is True


def test_registration_privilege_escalation_attempt(client: TestClient, auth_mock_db):
    """
    Test server-side enforcement: client attempt to register as Admin or specify bureau is ignored.
    Server MUST assign role='Complainant' and bureau='All'.
    """
    malicious_payload = {
        "name": "Privilege Attacker",
        "email": "attacker@example.com",
        "password": "AttackPassword@123",
        "role": "Admin",
        "bureau": "RB",
        "designation": "System Administrator",
    }
    response = client.post("/api/auth/register", json=malicious_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["role"] == "Complainant"
    assert data["user"]["bureau"] == "All"

    db_user = [u for u in auth_mock_db.users if u.email == "attacker@example.com"][0]
    assert db_user.role == "Complainant"
    assert db_user.bureau == "All"


def test_login_after_registration(client: TestClient, auth_mock_db):
    """
    Test user can register and immediately authenticate via POST /api/auth/login.
    """
    reg_payload = {
        "name": "Auth Flow User",
        "email": "authflow@example.com",
        "password": "FlowPassword@2026",
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201

    # Now login with the newly created account
    login_res = client.post("/api/auth/login", json={
        "email": "authflow@example.com",
        "password": "FlowPassword@2026",
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["user"]["email"] == "authflow@example.com"
    assert login_data["user"]["role"] == "Complainant"
    assert "accessToken" in login_data


def test_complaint_ownership_new_record(client: TestClient, auth_mock_db):
    """
    Test complaint created by authenticated Complainant:
    1. complainant_user_id is set to user's database ID.
    2. Complainant can access their own complaint.
    3. Another complainant receives 403 Forbidden.
    4. Admin or assigned officer can access it.
    """
    new_complainant = User(
        id="c-user-99",
        name="Citizen One",
        email="citizen.one@example.com",
        role="Complainant",
        designation="Citizen",
        bureau="All",
        status="Active",
        password_hash=TEST_HASH,
    )
    auth_mock_db.users.append(new_complainant)

    app.dependency_overrides[get_current_user] = lambda: new_complainant
    try:
        create_res = client.post("/api/complaints", json={
            "title": "Unauthorized fee demand by college",
            "description": "College demanded extra library fee exceeding official norms.",
            "bureau": "PGRC",
            "category": "Fee Regulation",
            "priority": "Medium",
            "institutionId": "i1",
            "complainantType": "Student",
        })
        assert create_res.status_code == 201
        case_data = create_res.json()
        case_id = case_data["id"]
        assert case_data["complainantUserId"] == "c-user-99"
        assert case_data["complainantEmail"] == "citizen.one@example.com"

        # 2. Complainant can access it
        owner_get = client.get(f"/api/complaints/{case_id}")
        assert owner_get.status_code == 200
        assert owner_get.json()["id"] == case_id

        # Complainant list includes it
        owner_list = client.get("/api/complaints")
        assert owner_list.status_code == 200
        assert any(c["id"] == case_id for c in owner_list.json()["items"])

        # 3. Another complainant tries to access it -> 403 Forbidden
        app.dependency_overrides[get_current_user] = lambda: USER_COMPLAINANT  # Rohit Sharma, u0
        other_get = client.get(f"/api/complaints/{case_id}")
        assert other_get.status_code == 403
        assert "access forbidden" in other_get.json()["detail"].lower()

        # Other complainant's list excludes it
        other_list = client.get("/api/complaints")
        assert other_list.status_code == 200
        assert not any(c["id"] == case_id for c in other_list.json()["items"])

        # 4. Admin can access it
        app.dependency_overrides[get_current_user] = lambda: USER_ADMIN
        admin_get = client.get(f"/api/complaints/{case_id}")
        assert admin_get.status_code == 200
    finally:
        app.dependency_overrides[get_current_user] = lambda: USER_ADMIN


def test_complaint_ownership_legacy_record(client: TestClient, auth_mock_db):
    """
    Test backward compatibility for legacy records with complainant_user_id = None:
    - User with matching complainant_email is granted access.
    - User with different email receives 403 Forbidden.
    """
    legacy_case = Complaint(
        id="PGRC-2026-LEGACY1",
        institution_id="i1",
        institution_permanent_id="1-4821039",
        bureau="PGRC",
        category="Fee Regulation",
        priority="Medium",
        officer="Rajesh Kumar",
        assigned_user_id="u2",
        status="In Progress",
        date="2026-09-01",
        due="2026-09-30",
        title="Legacy complaint before user accounts existed",
        description="Legacy complaint with no complainant_user_id attached.",
        complainant_type="Student",
        complainant_name="Rohit Sharma",
        complainant_email="rohit.sharma@student.edu.in",
        complainant_user_id=None,  # Unlinked legacy record
        created_at=datetime(2026, 9, 1, 10, 0, 0),
        updated_at=datetime(2026, 9, 1, 10, 0, 0),
    )
    auth_mock_db.complaints.append(legacy_case)

    # 1. Complainant with matching email (USER_COMPLAINANT: rohit.sharma@student.edu.in)
    app.dependency_overrides[get_current_user] = lambda: USER_COMPLAINANT
    try:
        match_get = client.get(f"/api/complaints/{legacy_case.id}")
        assert match_get.status_code == 200
        assert match_get.json()["id"] == legacy_case.id

        # 2. Complainant with different email (e.g. stranger)
        stranger_user = User(
            id="c-stranger-88",
            name="Stranger User",
            email="stranger@otherdomain.com",
            role="Complainant",
            designation="Citizen",
            bureau="All",
            status="Active",
            password_hash=TEST_HASH,
        )
        auth_mock_db.users.append(stranger_user)
        app.dependency_overrides[get_current_user] = lambda: stranger_user

        stranger_get = client.get(f"/api/complaints/{legacy_case.id}")
        assert stranger_get.status_code == 403
        assert "access forbidden" in stranger_get.json()["detail"].lower()
    finally:
        app.dependency_overrides[get_current_user] = lambda: USER_ADMIN


