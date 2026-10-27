import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models.user import User
from app.models.complaint import Complaint
from app.auth import (
    get_current_user,
    hash_password,
    create_access_token,
    verify_password,
)

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
    bureau="PGRC",
    avatar_text="IO",
    phone="+91 11 2958 0000",
    status="Inactive",
    department="PGRC",
    password_hash=TEST_HASH,
)

ALL_TEST_USERS = [
    USER_ADMIN,
    USER_BUREAU_ADMIN,
    USER_OFFICER_PGRC,
    USER_OFFICER_RB,
    USER_COMPLAINANT,
    USER_INACTIVE,
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
    title="Students report compulsory development charges",
    description="Formal grievance regarding fee structure.",
    complainant_type="Student",
    complainant_name="Rohit Sharma",
    complainant_email="rohit.sharma@student.edu.in",
    complainant_user_id="u0",
    remarks=None,
    next_action="Examine affidavit",
    last_action_date="2026-10-05",
    created_at=datetime(2026, 10, 2, 10, 0, 0),
    updated_at=datetime(2026, 10, 2, 10, 0, 0),
)

SAMPLE_COMPLAINT_RESOLVED = Complaint(
    id="PGRC-2026-0874",
    institution_id="i1",
    institution_permanent_id="1-4821039",
    bureau="PGRC",
    category="Fee Regulation",
    priority="Low",
    officer="Rajesh Kumar",
    assigned_user_id="u2",
    status="Resolved",
    date="2026-09-01",
    due="2026-09-30",
    title="Resolved complaint",
    description="Already closed inquiry.",
    complainant_type="Student",
    complainant_name="Rohit Sharma",
    complainant_email="rohit.sharma@student.edu.in",
    complainant_user_id="u0",
    remarks=None,
    next_action="None",
    last_action_date="2026-09-20",
    created_at=datetime(2026, 9, 1, 10, 0, 0),
    updated_at=datetime(2026, 9, 20, 10, 0, 0),
)

ALL_SAMPLE_COMPLAINTS = [
    SAMPLE_COMPLAINT_PGRC,
    SAMPLE_COMPLAINT_RESOLVED,
]


class MockUserDBSession:
    """In-memory mock session supporting user management and complaint count queries."""

    def __init__(self, users=None, complaints=None):
        self.users = [
            User(
                id=u.id,
                name=u.name,
                email=u.email,
                role=u.role,
                designation=u.designation,
                bureau=u.bureau,
                avatar_text=u.avatar_text,
                phone=u.phone,
                status=u.status,
                department=u.department,
                password_hash=u.password_hash,
            )
            for u in (users if users is not None else ALL_TEST_USERS)
        ]
        self.complaints = list(complaints if complaints is not None else ALL_SAMPLE_COMPLAINTS)
        self.added = []

    def query(self, model, *args):
        session = self

        class MockQuery:
            def __init__(self, current_items):
                self._items = current_items

            def filter(self, *criteria):
                filtered = list(self._items)
                for criterion in criteria:
                    criterion_str = str(criterion).lower()

                    # User ID inequality (User.id != user.id)
                    if "users.id !=" in criterion_str or "users.id <>" in criterion_str:
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            filtered = [u for u in filtered if u.id != str(val)]

                    # User ID exact match (User.id == id)
                    elif "users.id =" in criterion_str or ("users.id" in criterion_str and "=" in criterion_str):
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            filtered = [u for u in filtered if u.id == str(val)]

                    # User email match
                    elif "users.email" in criterion_str:
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            clean_val = str(val).strip().lower()
                            filtered = [u for u in filtered if u.email.lower() == clean_val]

                    # User role filter
                    elif "users.role" in criterion_str:
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            clean_val = str(val).replace("%", "").strip().lower()
                            filtered = [u for u in filtered if u.role.lower() == clean_val]

                    # User bureau filter
                    elif "users.bureau" in criterion_str and "or_" not in criterion_str:
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            clean_val = str(val).replace("%", "").strip().lower()
                            filtered = [u for u in filtered if u.bureau.lower() == clean_val]

                    # User status filter
                    elif "users.status" in criterion_str:
                        val = getattr(getattr(criterion, "right", None), "value", None)
                        if val is not None:
                            clean_val = str(val).replace("%", "").strip().lower()
                            filtered = [u for u in filtered if (u.status or "").lower() == clean_val]

                    # User search filter with OR
                    elif "or_" in criterion_str and "users." in criterion_str:
                        clauses = getattr(criterion, "clauses", [criterion])
                        terms = []
                        for cl in clauses:
                            v = getattr(getattr(cl, "right", None), "value", None)
                            if v:
                                terms.append(str(v).replace("%", "").strip().lower())
                        search_term = terms[0] if terms else ""
                        if search_term:
                            filtered = [
                                u
                                for u in filtered
                                if (
                                    search_term in u.name.lower()
                                    or search_term in u.email.lower()
                                    or search_term in (u.designation or "").lower()
                                    or search_term in (u.bureau or "").lower()
                                )
                            ]

                    # Complaint filter for active count
                    elif "complaints." in criterion_str:
                        # Status != Resolved
                        if "status !=" in criterion_str or "status <>" in criterion_str or "resolved" in criterion_str:
                            filtered = [c for c in filtered if c.status != "Resolved"]

                        # (Complaint.assigned_user_id == user.id) | (Complaint.officer == user.name)
                        clauses = getattr(criterion, "clauses", [criterion])
                        if clauses and any("assigned_user_id" in str(cl).lower() or "officer" in str(cl).lower() for cl in clauses):
                            targets = []
                            for cl in clauses:
                                v = getattr(getattr(cl, "right", None), "value", None)
                                if v:
                                    targets.append(str(v).strip().lower())
                            if targets:
                                filtered = [
                                    c
                                    for c in filtered
                                    if (
                                        (c.assigned_user_id and c.assigned_user_id.lower() in targets)
                                        or (c.officer and c.officer.lower() in targets)
                                    )
                                ]

                return MockQuery(filtered)

            def order_by(self, *args):
                return self

            def all(self):
                return list(self._items)

            def first(self):
                return self._items[0] if self._items else None

            def count(self):
                return len(self._items)

            def scalar(self):
                return len(self._items)

        if model is User:
            return MockQuery(self.users)
        elif model is Complaint:
            return MockQuery(self.complaints)
        else:
            return MockQuery(self.complaints)

    def add(self, instance):
        self.added.append(instance)
        if isinstance(instance, User):
            self.users.append(instance)

    def commit(self):
        pass

    def refresh(self, instance):
        pass


@pytest.fixture
def mock_session():
    session = MockUserDBSession()
    app.dependency_overrides[get_db] = lambda: session
    yield session
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(autouse=True)
def setup_user_test_env(mock_session):
    """Ensure tests run against real token authentication rather than conftest's default mock."""
    app.dependency_overrides.pop(get_current_user, None)
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def client(mock_session):
    return TestClient(app)


def auth_headers(user: User) -> dict:
    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {"Authorization": f"Bearer {token}"}


# =========================================================================
# 1. Authorization & RBAC on Listing Users (GET /api/users)
# =========================================================================

def test_admin_can_list_users(client, mock_session):
    """System Admin can query the personnel directory with full profiles and activeCasesCount."""
    res = client.get("/api/users", headers=auth_headers(USER_ADMIN))
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= len(ALL_TEST_USERS)

    # Verify attributes and security: password_hash must NEVER be exposed
    for u in data:
        assert "id" in u
        assert "name" in u
        assert "email" in u
        assert "role" in u
        assert "bureau" in u
        assert "designation" in u
        assert "status" in u
        assert "activeCasesCount" in u
        assert "password_hash" not in u
        assert "password" not in u


def test_officer_and_bureau_admin_can_list_users_read_only(client, mock_session):
    """Case Officer and Bureau Administrator have read-only access to view authorized staff directory."""
    res_officer = client.get("/api/users", headers=auth_headers(USER_OFFICER_PGRC))
    assert res_officer.status_code == 200
    assert len(res_officer.json()) > 0

    res_bureau_admin = client.get("/api/users", headers=auth_headers(USER_BUREAU_ADMIN))
    assert res_bureau_admin.status_code == 200
    assert len(res_bureau_admin.json()) > 0


def test_complainant_forbidden_from_listing_users(client, mock_session):
    """Public citizen / Complainant is strictly blocked (403 Forbidden) from accessing staff directory."""
    res = client.get("/api/users", headers=auth_headers(USER_COMPLAINANT))
    assert res.status_code == 403
    assert "Complainants are not permitted" in res.json()["detail"]


def test_unauthenticated_forbidden_from_listing_users(client, mock_session):
    """Unauthenticated requests must receive 401 Unauthorized."""
    res = client.get("/api/users")
    assert res.status_code == 401


# =========================================================================
# 2. Lookup Single User by ID (GET /api/users/{id})
# =========================================================================

def test_get_user_by_id_authorized(client, mock_session):
    """Admin and official staff can retrieve single profile by ID."""
    res = client.get("/api/users/u2", headers=auth_headers(USER_ADMIN))
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "u2"
    assert data["name"] == "Rajesh Kumar"
    assert data["email"] == "rajesh.kumar@aicte-india.org"
    assert "password_hash" not in data
    # activeCasesCount should count non-resolved complaints
    assert data["activeCasesCount"] == 1


def test_get_user_by_id_forbidden_for_complainant(client, mock_session):
    """Complainant cannot lookup official user details."""
    res = client.get("/api/users/u2", headers=auth_headers(USER_COMPLAINANT))
    assert res.status_code == 403


def test_get_user_by_id_not_found(client, mock_session):
    """Querying non-existent user returns 404."""
    res = client.get("/api/users/u_missing_999", headers=auth_headers(USER_ADMIN))
    assert res.status_code == 404


# =========================================================================
# 3. Provisioning Official Users (POST /api/users)
# =========================================================================

def test_admin_create_official_user_success(client, mock_session):
    """System Admin can provision a new official user account with hashed password and generated ID."""
    payload = {
        "name": "Dr. Ramesh Chander",
        "email": "ramesh.chander@aicte-india.org",
        "role": "Officer",
        "bureau": "PGRC",
        "designation": "Scrutiny Officer, Fee Monitoring Cell",
        "phone": "+91 11 2958 1088",
        "password": "SecurePassword@2026",
    }
    res = client.post("/api/users", json=payload, headers=auth_headers(USER_ADMIN))
    assert res.status_code == 201
    data = res.json()
    assert data["id"].startswith("u-")
    assert data["name"] == "Dr. Ramesh Chander"
    assert data["email"] == "ramesh.chander@aicte-india.org"
    assert data["role"] == "Officer"
    assert data["bureau"] == "PGRC"
    assert data["designation"] == "Scrutiny Officer, Fee Monitoring Cell"
    assert data["phone"] == "+91 11 2958 1088"
    assert data["status"] == "Active"
    assert data["avatarText"] == "DC"
    assert "password_hash" not in data
    assert "password" not in data

    # Verify password was securely hashed and stored
    created_user = next(u for u in mock_session.users if u.email == "ramesh.chander@aicte-india.org")
    assert created_user.password_hash is not None
    assert created_user.password_hash != "SecurePassword@2026"
    assert verify_password("SecurePassword@2026", created_user.password_hash)


def test_non_admin_cannot_create_official_users(client, mock_session):
    """Officers, BureauAdmins, and Complainants are strictly forbidden from creating users."""
    payload = {
        "name": "Unauthorized User",
        "email": "unauth@aicte-india.org",
        "role": "Officer",
        "bureau": "PGRC",
        "password": "ValidPassword@2026",
    }
    # Officer attempt
    res = client.post("/api/users", json=payload, headers=auth_headers(USER_OFFICER_PGRC))
    assert res.status_code == 403

    # BureauAdmin attempt
    res = client.post("/api/users", json=payload, headers=auth_headers(USER_BUREAU_ADMIN))
    assert res.status_code == 403

    # Complainant attempt
    res = client.post("/api/users", json=payload, headers=auth_headers(USER_COMPLAINANT))
    assert res.status_code == 403

    # Unauthenticated attempt
    res = client.post("/api/users", json=payload)
    assert res.status_code == 401


def test_create_user_duplicate_email_rejected(client, mock_session):
    """Duplicate email (case-insensitive) is rejected with 409 Conflict."""
    payload = {
        "name": "Duplicate Officer",
        "email": "RAJESH.KUMAR@aicte-india.org",  # already belongs to u2
        "role": "Officer",
        "bureau": "PGRC",
        "password": "ValidPassword@2026",
    }
    res = client.post("/api/users", json=payload, headers=auth_headers(USER_ADMIN))
    assert res.status_code == 409
    assert "already registered" in res.json()["detail"].lower()


def test_create_user_validation_failures(client, mock_session):
    """Validation checks: invalid email, short name, invalid role, invalid bureau, short password."""
    # Missing password rejected (no insecure shared fallback)
    res_nopass = client.post(
        "/api/users",
        json={"name": "Valid Name", "email": "valid@aicte-india.org", "role": "Officer"},
        headers=auth_headers(USER_ADMIN),
    )
    assert res_nopass.status_code == 422

    # Invalid email
    res = client.post(
        "/api/users",
        json={"name": "Valid Name", "email": "not-an-email", "role": "Officer", "password": "ValidPassword@2026"},
        headers=auth_headers(USER_ADMIN),
    )
    assert res.status_code == 422

    # Name too short (< 2 chars)
    res = client.post(
        "/api/users",
        json={"name": "X", "email": "valid@aicte-india.org", "role": "Officer", "password": "ValidPassword@2026"},
        headers=auth_headers(USER_ADMIN),
    )
    assert res.status_code == 422

    # Invalid role
    res = client.post(
        "/api/users",
        json={"name": "Valid Name", "email": "valid@aicte-india.org", "role": "SuperBoss", "password": "ValidPassword@2026"},
        headers=auth_headers(USER_ADMIN),
    )
    assert res.status_code == 422

    # Invalid bureau
    res = client.post(
        "/api/users",
        json={"name": "Valid Name", "email": "valid@aicte-india.org", "role": "Officer", "bureau": "MarsBureau", "password": "ValidPassword@2026"},
        headers=auth_headers(USER_ADMIN),
    )
    assert res.status_code == 422

    # Password too short (< 6 chars)
    res = client.post(
        "/api/users",
        json={"name": "Valid Name", "email": "valid@aicte-india.org", "role": "Officer", "password": "123"},
        headers=auth_headers(USER_ADMIN),
    )
    assert res.status_code == 422


# =========================================================================
# 4. Updating User Accounts & Role Assignment (PATCH /api/users/{id})
# =========================================================================

def test_admin_update_user_role_and_profile(client, mock_session):
    """System Admin can update profile attributes and promote/assign roles."""
    payload = {
        "role": "BureauAdmin",
        "designation": "Director, PGRC Scrutiny Cell",
        "phone": "+91 11 2958 9999",
        "bureau": "PGRC",
    }
    res = client.patch("/api/users/u2", json=payload, headers=auth_headers(USER_ADMIN))
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "u2"
    assert data["role"] == "BureauAdmin"
    assert data["designation"] == "Director, PGRC Scrutiny Cell"
    assert data["phone"] == "+91 11 2958 9999"

    # Verify persistence in session
    user_in_db = next(u for u in mock_session.users if u.id == "u2")
    assert user_in_db.role == "BureauAdmin"
    assert user_in_db.designation == "Director, PGRC Scrutiny Cell"


def test_non_admin_cannot_update_users(client, mock_session):
    """Non-Admins cannot update user records."""
    payload = {"designation": "Hacked Title"}
    res_officer = client.patch("/api/users/u2", json=payload, headers=auth_headers(USER_OFFICER_PGRC))
    assert res_officer.status_code == 403

    res_complainant = client.patch("/api/users/u2", json=payload, headers=auth_headers(USER_COMPLAINANT))
    assert res_complainant.status_code == 403

    res_anon = client.patch("/api/users/u2", json=payload)
    assert res_anon.status_code == 401


def test_update_user_email_conflict(client, mock_session):
    """Updating email to an address that already belongs to another user returns 409 Conflict."""
    payload = {"email": "priya.nair@aicte-india.org"}  # belongs to u1b
    res = client.patch("/api/users/u2", json=payload, headers=auth_headers(USER_ADMIN))
    assert res.status_code == 409
    assert "already exists" in res.json()["detail"].lower()


def test_update_user_password_hashing(client, mock_session):
    """Admin can reset a user's password, which must be hashed with bcrypt."""
    payload = {"password": "NewSecretPassword@2026"}
    res = client.patch("/api/users/u2", json=payload, headers=auth_headers(USER_ADMIN))
    assert res.status_code == 200
    assert "password_hash" not in res.json()

    user_in_db = next(u for u in mock_session.users if u.id == "u2")
    assert verify_password("NewSecretPassword@2026", user_in_db.password_hash)


def test_update_nonexistent_user_returns_404(client, mock_session):
    """Updating non-existent user returns 404."""
    res = client.patch("/api/users/u_does_not_exist", json={"name": "New Name"}, headers=auth_headers(USER_ADMIN))
    assert res.status_code == 404


# =========================================================================
# 5. Duty Status Toggle (PATCH /api/users/{id}/status)
# =========================================================================

def test_admin_toggle_duty_status(client, mock_session):
    """System Admin can change duty status between Active, On Leave, and Inactive."""
    # Set to On Leave
    res = client.patch("/api/users/u2/status", json={"status": "On Leave"}, headers=auth_headers(USER_ADMIN))
    assert res.status_code == 200
    assert res.json()["status"] == "On Leave"

    # Set back to Active
    res2 = client.patch("/api/users/u2/status", json={"status": "Active"}, headers=auth_headers(USER_ADMIN))
    assert res2.status_code == 200
    assert res2.json()["status"] == "Active"


def test_non_admin_cannot_toggle_duty_status(client, mock_session):
    """Non-Admins cannot toggle duty status."""
    res = client.patch(
        "/api/users/u2/status",
        json={"status": "On Leave"},
        headers=auth_headers(USER_OFFICER_PGRC),
    )
    assert res.status_code == 403


def test_invalid_duty_status_rejected(client, mock_session):
    """Invalid duty status is rejected by schema validator with 422."""
    res = client.patch(
        "/api/users/u2/status",
        json={"status": "SuspendedIndefinitely"},
        headers=auth_headers(USER_ADMIN),
    )
    assert res.status_code == 422


# =========================================================================
# 6. Listing Filters (Role, Bureau, Status, Search)
# =========================================================================

def test_list_users_filters(client, mock_session):
    """Query parameters correctly filter the returned users."""
    # Role filter
    res_role = client.get("/api/users?role=Officer", headers=auth_headers(USER_ADMIN))
    assert res_role.status_code == 200
    for u in res_role.json():
        assert u["role"] == "Officer"

    # Bureau filter
    res_bureau = client.get("/api/users?bureau=RB", headers=auth_headers(USER_ADMIN))
    assert res_bureau.status_code == 200
    for u in res_bureau.json():
        assert u["bureau"] == "RB"

    # Status filter
    res_status = client.get("/api/users?status=Inactive", headers=auth_headers(USER_ADMIN))
    assert res_status.status_code == 200
    assert len(res_status.json()) == 1
    assert res_status.json()[0]["id"] == "u_inactive"

    # Search filter
    res_search = client.get("/api/users?search=Anita", headers=auth_headers(USER_ADMIN))
    assert res_search.status_code == 200
    assert any(u["name"] == "Anita Verma" for u in res_search.json())


# =========================================================================
# 7. Public Registration Stays Strictly Complainant
# =========================================================================

def test_public_registration_cannot_escalate_role(client, mock_session):
    """Public registration at /api/auth/register always sets role=Complainant."""
    payload = {
        "name": "Sneaky User",
        "email": "sneaky@example.org",
        "password": "ValidPassword@2026",
        "complainantType": "Student",
        "role": "Admin",  # Client attempts privilege escalation
        "bureau": "All",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["user"]["role"] == "Complainant"
    assert data["user"]["email"] == "sneaky@example.org"


# =========================================================================
# 8. Admin Self-Protection & Lockout Prevention
# =========================================================================

def test_admin_cannot_demote_or_deactivate_self(client, mock_session):
    """System Administrator cannot accidentally revoke their own role or deactivate their own account."""
    # Attempt self-demotion
    res_demote = client.patch(
        f"/api/users/{USER_ADMIN.id}",
        json={"role": "Officer"},
        headers=auth_headers(USER_ADMIN),
    )
    assert res_demote.status_code == 400
    assert "cannot revoke their own administrative privileges" in res_demote.json()["detail"].lower()

    # Attempt self-deactivation
    res_deact = client.patch(
        f"/api/users/{USER_ADMIN.id}/status",
        json={"status": "Inactive"},
        headers=auth_headers(USER_ADMIN),
    )
    assert res_deact.status_code == 400
    assert "cannot deactivate their own" in res_deact.json()["detail"].lower()
