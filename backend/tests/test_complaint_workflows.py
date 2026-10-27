import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.database import get_db
from app.models.complaint import Complaint
from app.models.timeline import ComplaintTimeline
from app.models.user import User
from app.models.institution import Institution
from app.auth import get_current_user

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

MOCK_USERS = [
    User(
        id="u2",
        name="Rajesh Kumar",
        email="rajesh.kumar@aicte-india.org",
        role="Officer",
        designation="Senior Grievance Officer, PGRC",
        bureau="PGRC",
        status="Active",
        department="PGRC Scrutiny Cell"
    ),
    User(
        id="u3",
        name="Anita Verma",
        email="anita.verma@aicte-india.org",
        role="Officer",
        designation="Director & Bureau Chief, RB",
        bureau="RB",
        status="Active",
        department="Regulation Bureau"
    ),
    User(
        id="u5",
        name="Suresh Patel",
        email="suresh.patel@aicte-india.org",
        role="Officer",
        designation="Scrutiny Officer, Approval Bureau",
        bureau="Approval",
        status="Active",
        department="Approval Bureau Scrutiny"
    ),
    User(
        id="u_inactive",
        name="Inactive Officer",
        email="inactive@aicte-india.org",
        role="Officer",
        designation="Former Officer",
        bureau="PGRC",
        status="Inactive",
        department="PGRC"
    ),
    User(
        id="u0",
        name="Rohit Sharma",
        email="rohit.sharma@student.edu.in",
        role="Complainant",
        designation="Student",
        bureau="PGRC",
        status="Active",
        department="Citizen"
    )
]

def make_sample_complaints():
    c1 = Complaint(
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
        description='A group of third-year B.Tech students submitted a formal grievance.',
        complainant_type="Student",
        complainant_name="Rohit Sharma",
        complainant_email="rohit.sharma@student.edu.in",
        remarks=None,
        next_action="Examine institution counter-affidavit and verify official registers",
        last_action_date="2026-10-05",
        created_at=datetime(2026, 10, 2, 10, 0, 0),
        updated_at=datetime(2026, 10, 2, 10, 0, 0),
    )
    c2 = Complaint(
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
        description="Parents allege the institute collects tuition roughly 40% above fee approved.",
        complainant_type="Parent",
        complainant_name="S. Sundaram",
        complainant_email="citizen.grievance@aicte-portal.in",
        remarks=None,
        next_action="Jurisdiction verification and preliminary scrutiny by RB Cell",
        last_action_date="2026-09-28",
        created_at=datetime(2026, 9, 28, 10, 0, 0),
        updated_at=datetime(2026, 9, 28, 10, 0, 0),
    )
    c3 = Complaint(
        id="AB-2026-0310",
        institution_id="i3",
        institution_permanent_id="1-5120987",
        bureau="Approval",
        category="Infrastructure",
        priority="Medium",
        officer="Suresh Patel",
        assigned_user_id="u5",
        status="Resolved",
        date="2026-08-14",
        due="2026-09-14",
        title="Laboratory machinery and licensed software shortfall",
        description="Scrutiny committee found deficiencies in CAD software licenses.",
        complainant_type="General Public",
        complainant_name="Verified Whistleblower",
        complainant_email="citizen.grievance@aicte-portal.in",
        remarks="Compliance verified.",
        next_action="Final compliance order signed and archived",
        last_action_date="2026-08-17",
        created_at=datetime(2026, 8, 14, 10, 0, 0),
        updated_at=datetime(2026, 8, 14, 10, 0, 0),
    )
    return [c1, c2, c3]

def make_sample_timelines():
    t1 = ComplaintTimeline(
        id=1,
        complaint_id="PGRC-2026-0873",
        label="Complaint registered and verified on AICTE portal",
        date="2026-10-02 10:00",
        by="System / Portal",
        role="Complainant",
        note="Portal intake verified.",
        user_id=None,
    )
    t2 = ComplaintTimeline(
        id=2,
        complaint_id="PGRC-2026-0873",
        label="Assigned to Rajesh Kumar (PGRC Bureau)",
        date="2026-10-02 11:30",
        by="Dr. S. Mehta (Member Secretary & System Admin)",
        role="Admin",
        note="Initial statutory allocation.",
        user_id="u2",
    )
    t3 = ComplaintTimeline(
        id=3,
        complaint_id="PGRC-2026-0873",
        label="Case status updated to In Progress",
        date="2026-10-05 14:00",
        by="Rajesh Kumar (Handling Officer)",
        role="Officer",
        note="Counter-affidavit requested.",
        user_id="u2",
    )
    return [t1, t2, t3]

class WorkflowMockQuery:
    def __init__(self, data):
        self.data = list(data)

    def filter(self, *args, **kwargs):
        # Allow checking specific criteria for tests
        return self

    def order_by(self, *args):
        # Always order by ID ascending if requested
        self.data = sorted(self.data, key=lambda x: getattr(x, "id", 0))
        return self

    def all(self):
        return self.data

    def first(self):
        return self.data[0] if self.data else None

class WorkflowMockDBSession:
    def __init__(self, complaints=None, timelines=None, users=None, fail_on_add=False):
        self.complaints = list(complaints) if complaints is not None else make_sample_complaints()
        self.timelines = list(timelines) if timelines is not None else make_sample_timelines()
        self.users = list(users) if users is not None else list(MOCK_USERS)
        self.added = []
        self.rolled_back = False
        self.committed = False
        self.fail_on_add = fail_on_add

    def query(self, model):
        if model == Complaint:
            return self._complaint_query()
        elif model == ComplaintTimeline:
            return self._timeline_query()
        elif model == User:
            return self._user_query()
        elif model == Institution:
            return WorkflowMockQuery([MOCK_INSTITUTION])
        return WorkflowMockQuery([])

    def _extract_val(self, arg):
        if hasattr(arg, "right") and hasattr(arg.right, "value"):
            return str(arg.right.value).strip()
        return ""

    def _complaint_query(self):
        session_self = self
        class ComplaintQuery(WorkflowMockQuery):
            def filter(self, *args, **kwargs):
                if args:
                    val = session_self._extract_val(args[0])
                    if val:
                        matched = [c for c in session_self.complaints if c.id.lower() == val.lower()]
                        return WorkflowMockQuery(matched)
                return WorkflowMockQuery(session_self.complaints)
        return ComplaintQuery(self.complaints)

    def _timeline_query(self):
        session_self = self
        class TimelineQuery(WorkflowMockQuery):
            def filter(self, *args, **kwargs):
                if args:
                    val = session_self._extract_val(args[0])
                    if val:
                        matched = [t for t in session_self.timelines if t.complaint_id.lower() == val.lower()]
                        return WorkflowMockQuery(matched)
                return WorkflowMockQuery(session_self.timelines)
        return TimelineQuery(self.timelines)

    def _user_query(self):
        session_self = self
        class UserQuery(WorkflowMockQuery):
            def filter(self, *args, **kwargs):
                if args:
                    val = session_self._extract_val(args[0])
                    if val:
                        matched = [u for u in session_self.users if u.id.lower() == val.lower() or u.name.lower() == val.lower()]
                        return WorkflowMockQuery(matched)
                return WorkflowMockQuery([])
        return UserQuery(self.users)

    def add(self, obj):
        if self.fail_on_add:
            raise RuntimeError("Simulated database failure during transaction")
        self.added.append(obj)
        if isinstance(obj, ComplaintTimeline):
            if not getattr(obj, "id", None):
                obj.id = len(self.timelines) + 1
            self.timelines.append(obj)
        elif isinstance(obj, Complaint):
            self.complaints.append(obj)

    def flush(self):
        pass

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def refresh(self, obj):
        pass

def test_get_complaint_timeline_ordering(client: TestClient):
    """
    Test retrieving timeline events in chronological order.
    """
    from app.main import app
    session = WorkflowMockDBSession()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        response = client.get("/api/complaints/PGRC-2026-0873/timeline")
        assert response.status_code == 200
        events = response.json()
        assert len(events) == 3
        # Chronological order by id/sequence
        assert events[0]["id"] < events[1]["id"] < events[2]["id"]
        assert events[0]["label"] == "Complaint registered and verified on AICTE portal"
        assert events[1]["label"] == "Assigned to Rajesh Kumar (PGRC Bureau)"
        assert events[2]["label"] == "Case status updated to In Progress"
    finally:
        app.dependency_overrides.clear()

def test_update_status_success(client: TestClient):
    """
    Test successful status update from Pending to In Progress with timeline recorded.
    """
    from app.main import app
    session = WorkflowMockDBSession()
    target_complaint = [c for c in session.complaints if c.id == "RB-2026-0141"][0]
    assert target_complaint.status == "Pending"

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    user_anita = [u for u in session.users if u.name == "Anita Verma"][0]
    app.dependency_overrides[get_current_user] = lambda: user_anita
    try:
        payload = {
            "status": "In Progress",
            "remarks": "Investigation notice served to institute management.",
            "by": "Anita Verma",
            "role": "Officer",
            "note": "Formal scrutiny notice dispatched via speed post and registered email."
        }
        response = client.patch(f"/api/complaints/{target_complaint.id}/status", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "In Progress"
        assert data["remarks"] == payload["remarks"]
        assert session.committed is True

        # Check timeline event added
        latest_event = session.timelines[-1]
        assert latest_event.complaint_id == target_complaint.id
        assert "In Progress" in latest_event.label
        assert latest_event.by == "Anita Verma"
        assert latest_event.note == payload["note"]
    finally:
        app.dependency_overrides.clear()

def test_update_status_to_resolved(client: TestClient):
    """
    Test resolving a case from In Progress with proper conclusion label.
    """
    from app.main import app
    session = WorkflowMockDBSession()
    target = [c for c in session.complaints if c.id == "PGRC-2026-0873"][0]
    assert target.status == "In Progress"

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        payload = {
            "status": "Resolved",
            "remarks": "Full refund issued to students; compliance verified.",
            "by": "Rajesh Kumar",
            "role": "Officer"
        }
        response = client.patch(f"/api/complaints/{target.id}/status", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Resolved"

        latest_event = session.timelines[-1]
        assert "Case investigation concluded & Marked Resolved" in latest_event.label
    finally:
        app.dependency_overrides.clear()

def test_update_status_invalid_transition(client: TestClient):
    """
    Test that invalid status transitions (e.g. Pending -> Resolved, or from Resolved) are rejected.
    """
    from app.main import app
    session = WorkflowMockDBSession()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        # 1. Pending cannot jump directly to Resolved
        pending_c = [c for c in session.complaints if c.id == "RB-2026-0141"][0]
        res1 = client.patch(f"/api/complaints/{pending_c.id}/status", json={"status": "Resolved"})
        assert res1.status_code == 400
        assert "not permitted" in res1.json()["detail"].lower()

        # 2. Resolved cannot be reopened
        resolved_c = [c for c in session.complaints if c.id == "AB-2026-0310"][0]
        res2 = client.patch(f"/api/complaints/{resolved_c.id}/status", json={"status": "In Progress"})
        assert res2.status_code == 400
        assert "resolved and closed" in res2.json()["detail"].lower()

        # 3. Transition to same status rejected
        res3 = client.patch(f"/api/complaints/{pending_c.id}/status", json={"status": "Pending"})
        assert res3.status_code == 400
        assert "already in" in res3.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()

def test_update_status_invalid_status_enum(client: TestClient):
    """
    Test validation failure when invalid status enum is passed.
    """
    response = client.patch("/api/complaints/RB-2026-0141/status", json={"status": "Archived"})
    assert response.status_code == 422
    assert "status" in str(response.json()["detail"]).lower()

def test_update_status_missing_complaint(client: TestClient):
    """
    Test 404 when complaint does not exist.
    """
    from app.main import app
    session = WorkflowMockDBSession(complaints=[])

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        response = client.patch("/api/complaints/UNKNOWN-9999/status", json={"status": "In Progress"})
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()

def test_assign_complaint_by_user_id(client: TestClient):
    """
    Test assigning a complaint to an active user by userId.
    """
    from app.main import app
    session = WorkflowMockDBSession()
    target = [c for c in session.complaints if c.id == "PGRC-2026-0873"][0]

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        payload = {
            "userId": "u3",
            "reason": "Regulatory inquiry requires joint jurisdiction by Regulation Bureau."
        }
        response = client.patch(f"/api/complaints/{target.id}/assign", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["officer"] == "Anita Verma"
        assert data["assignedUserId"] == "u3"
        assert data["bureau"] == "RB"

        latest_event = session.timelines[-1]
        assert "reassigned" in latest_event.label.lower()
        assert "Administrative Justification" in latest_event.note
    finally:
        app.dependency_overrides.clear()

def test_assign_complaint_by_officer_name(client: TestClient):
    """
    Test assigning a complaint by officer name string.
    """
    from app.main import app
    session = WorkflowMockDBSession()
    target = [c for c in session.complaints if c.id == "PGRC-2026-0873"][0]

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        payload = {
            "officer": "Suresh Patel",
            "reason": "Assigned to Approval Bureau scrutiny officer."
        }
        response = client.patch(f"/api/complaints/{target.id}/assign", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["officer"] == "Suresh Patel"
        assert data["assignedUserId"] == "u5"
    finally:
        app.dependency_overrides.clear()

def test_assign_complaint_invalid_user(client: TestClient):
    """
    Test assigning to non-existent, inactive, or ineligible users.
    """
    from app.main import app
    session = WorkflowMockDBSession()
    target = [c for c in session.complaints if c.id == "PGRC-2026-0873"][0]

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        # Non-existent userId
        res1 = client.patch(f"/api/complaints/{target.id}/assign", json={"userId": "nonexistent_u"})
        assert res1.status_code == 400
        assert "not found" in res1.json()["detail"].lower()

        # Inactive user
        res2 = client.patch(f"/api/complaints/{target.id}/assign", json={"userId": "u_inactive"})
        assert res2.status_code == 400
        assert "inactive" in res2.json()["detail"].lower()

        # Ineligible role (Complainant)
        res3 = client.patch(f"/api/complaints/{target.id}/assign", json={"userId": "u0"})
        assert res3.status_code == 400
        assert "not eligible" in res3.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()

def test_assign_complaint_invalid_bureau(client: TestClient):
    """
    Test validation failure when invalid Bureau is passed.
    """
    response = client.patch("/api/complaints/PGRC-2026-0873/assign", json={"bureau": "INVALID_BUREAU"})
    assert response.status_code == 422
    assert "bureau" in str(response.json()["detail"]).lower()

def test_status_update_transaction_rollback(client: TestClient):
    """
    Verify transaction rollback when database failure occurs during timeline insertion.
    """
    from app.main import app
    session = WorkflowMockDBSession(fail_on_add=True)
    target = [c for c in session.complaints if c.id == "RB-2026-0141"][0]

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        try:
            res = client.patch(f"/api/complaints/{target.id}/status", json={"status": "In Progress"})
            assert res.status_code == 500
        except RuntimeError:
            pass
        assert session.rolled_back is True
    finally:
        app.dependency_overrides.clear()

def test_assignment_transaction_rollback(client: TestClient):
    """
    Verify transaction rollback when database failure occurs during assignment timeline insertion.
    """
    from app.main import app
    session = WorkflowMockDBSession(fail_on_add=True)
    target = [c for c in session.complaints if c.id == "PGRC-2026-0873"][0]

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        try:
            res = client.patch(f"/api/complaints/{target.id}/assign", json={"userId": "u3"})
            assert res.status_code == 500
        except RuntimeError:
            pass
        assert session.rolled_back is True
    finally:
        app.dependency_overrides.clear()


def test_system_admin_override_status_workflow(client: TestClient):
    """
    Regression Test (Phase 1):
    1. Normal users cannot reopen a Resolved case (400 Bad Request).
    2. System Admin without explicit overrideReason cannot reopen or execute non-permitted transitions (400 Bad Request).
    3. System Admin WITH non-empty overrideReason can reopen or execute extraordinary transition (200 OK).
    4. Timeline audit log captures [Admin Override] label and stores overrideReason verbatim.
    """
    from app.main import app
    session = WorkflowMockDBSession()
    target_resolved = [c for c in session.complaints if c.id == "AB-2026-0310"][0]
    assert target_resolved.status == "Resolved"

    user_admin = User(
        id="u1",
        name="Dr. S. Mehta",
        email="member-sec@aicte-india.org",
        role="Admin",
        designation="Member Secretary & System Admin",
        bureau="All",
        status="Active",
    )
    user_assigned_officer = [u for u in session.users if u.id == "u5"][0]

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        # 1. Assigned Officer attempts to reopen Resolved case -> 400 Bad Request
        app.dependency_overrides[get_current_user] = lambda: user_assigned_officer
        res_officer = client.patch(
            f"/api/complaints/{target_resolved.id}/status",
            json={"status": "In Progress"}
        )
        assert res_officer.status_code == 400
        assert "not permitted" in res_officer.json()["detail"].lower()

        # 2. System Admin attempts without overrideReason -> 400
        app.dependency_overrides[get_current_user] = lambda: user_admin
        res_admin_no_reason = client.patch(
            f"/api/complaints/{target_resolved.id}/status",
            json={"status": "In Progress"}
        )
        assert res_admin_no_reason.status_code == 400
        assert "override" in res_admin_no_reason.json()["detail"].lower()

        # 3. System Admin attempts with blank overrideReason -> 400
        res_admin_blank = client.patch(
            f"/api/complaints/{target_resolved.id}/status",
            json={"status": "In Progress", "overrideReason": "   "}
        )
        assert res_admin_blank.status_code == 400

        # 4. System Admin supplies valid non-empty overrideReason -> 200 OK
        justification = "Case reopened pursuant to High Court writ petition WP-412/2026 instruction."
        res_admin_success = client.patch(
            f"/api/complaints/{target_resolved.id}/status",
            json={
                "status": "In Progress",
                "overrideReason": justification,
                "note": "Notice issued to petitioner and respondent institute."
            }
        )
        assert res_admin_success.status_code == 200
        data = res_admin_success.json()
        assert data["status"] == "In Progress"

        # 5. Check timeline audit record
        latest_event = session.timelines[-1]
        assert "[Admin Override]" in latest_event.label
        assert "Admin Override Reason: " + justification in latest_event.note
    finally:
        app.dependency_overrides.clear()


def test_reassignment_preserves_bureau_and_cross_bureau_transfer(client: TestClient):
    """
    Regression Test (Phase 1):
    1. Ordinary reassignment with preserveBureau=True keeps the complaint's Bureau intact,
       even when the target officer belongs to another bureau.
    2. Cross-bureau transfer with explicit bureau updates the complaint's bureau.
    """
    from app.main import app
    session = WorkflowMockDBSession()
    target_complaint = [c for c in session.complaints if c.id == "PGRC-2026-0873"][0]
    assert target_complaint.bureau == "PGRC"

    user_admin = User(
        id="u1",
        name="Dr. S. Mehta",
        email="member-sec@aicte-india.org",
        role="Admin",
        designation="Member Secretary & System Admin",
        bureau="All",
        status="Active",
    )

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: user_admin
    try:
        # 1. Ordinary reassignment to Anita Verma (RB Bureau) with preserveBureau=True
        res_ordinary = client.patch(
            f"/api/complaints/{target_complaint.id}/assign",
            json={
                "userId": "u3",
                "reason": "Specialized inquiry assigned to Anita Verma",
                "preserveBureau": True,
            }
        )
        assert res_ordinary.status_code == 200
        data_ordinary = res_ordinary.json()
        assert data_ordinary["officer"] == "Anita Verma"
        assert data_ordinary["assignedUserId"] == "u3"
        assert data_ordinary["bureau"] == "PGRC", "Complaint bureau MUST remain PGRC when preserveBureau is True"

        # 2. Explicit cross-bureau transfer to RB bureau
        res_transfer = client.patch(
            f"/api/complaints/{target_complaint.id}/assign",
            json={
                "bureau": "RB",
                "userId": "u3",
                "reason": "Statutory handover from PGRC to Regulation Bureau",
            }
        )
        assert res_transfer.status_code == 200
        data_transfer = res_transfer.json()
        assert data_transfer["bureau"] == "RB", "Complaint bureau MUST update to RB upon explicit transfer"
        assert data_transfer["officer"] == "Anita Verma"
    finally:
        app.dependency_overrides.clear()


def test_unassigned_complaint_assignment_and_status_advance(client: TestClient):
    """
    Regression Test (Phase 1):
    1. An unassigned complaint (officer='Unassigned', assigned_user_id=None) can be assigned
       by Admin or authorized Bureau Admin without errors.
    2. Status update succeeds for an unassigned complaint when authorized.
    """
    from app.main import app
    session = WorkflowMockDBSession()
    unassigned = Complaint(
        id="PGRC-2026-9238",
        institution_id="i1",
        institution_permanent_id="1-4821039",
        bureau="PGRC",
        category="Fee Regulation",
        priority="High",
        officer="Unassigned",
        assigned_user_id=None,
        status="Pending",
        date="2026-10-10",
        due="2026-10-24",
        title="Unassigned grievance pending scrutiny",
        description="Freshly filed grievance waiting for officer assignment.",
        complainant_type="Student",
        complainant_name="Aman Verma",
        complainant_email="aman@student.edu.in",
        created_at=datetime(2026, 10, 10, 10, 0, 0),
        updated_at=datetime(2026, 10, 10, 10, 0, 0),
    )
    session.complaints.append(unassigned)

    user_admin = User(
        id="u1",
        name="Dr. S. Mehta",
        email="member-sec@aicte-india.org",
        role="Admin",
        designation="Member Secretary & System Admin",
        bureau="All",
        status="Active",
    )

    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: user_admin
    try:
        # 1. Assignment succeeds for unassigned complaint
        res_assign = client.patch(
            "/api/complaints/PGRC-2026-9238/assign",
            json={
                "userId": "u2",
                "reason": "First officer allocation from unassigned pool",
                "preserveBureau": True,
            }
        )
        assert res_assign.status_code == 200
        data_assign = res_assign.json()
        assert data_assign["officer"] == "Rajesh Kumar"
        assert data_assign["assignedUserId"] == "u2"

        # 2. Status update succeeds for unassigned complaint when authorized
        res_status = client.patch(
            "/api/complaints/PGRC-2026-9238/status",
            json={"status": "In Progress", "remarks": "Verification commenced"}
        )
        assert res_status.status_code == 200
        data_status = res_status.json()
        assert data_status["status"] == "In Progress"
    finally:
        app.dependency_overrides.clear()


def test_nonexistent_case_returns_404_and_unauthorized_returns_403(client: TestClient):
    """
    Regression Test (Phase 1):
    1. A nonexistent Case ID returns 404 (not 403).
    2. A real but unauthorized Case ID returns 403 Forbidden.
    """
    from app.main import app
    session = WorkflowMockDBSession()

    user_admin = User(
        id="u1",
        name="Dr. S. Mehta",
        email="member-sec@aicte-india.org",
        role="Admin",
        designation="Member Secretary & System Admin",
        bureau="All",
        status="Active",
    )
    user_officer = User(
        id="u2",
        name="Rajesh Kumar",
        email="rajesh.kumar@aicte-india.org",
        role="Officer",
        designation="Senior Grievance Officer, PGRC",
        bureau="PGRC",
        status="Active",
        department="PGRC Scrutiny Cell"
    )

    # 1. Nonexistent Case ID returns 404
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: user_admin
    try:
        res_404 = client.patch(
            "/api/complaints/NONEXISTENT-2026-9999/assign",
            json={"userId": "u2", "reason": "Attempting assignment on nonexistent case"}
        )
        assert res_404.status_code == 404
        assert "was not found" in res_404.json()["detail"]
    finally:
        app.dependency_overrides.clear()

    # 2. Real but unauthorized Case ID returns 403
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: user_officer
    try:
        # Rajesh Kumar (PGRC) tries to assign an RB complaint (RB-2026-0141)
        res_403 = client.patch(
            "/api/complaints/RB-2026-0141/assign",
            json={"userId": "u2", "reason": "Unauthorized assignment attempt"}
        )
        assert res_403.status_code == 403

        # Rajesh Kumar (Officer) tries to update status on an unauthorized complaint (RB-2026-0141)
        res_403_status = client.patch(
            "/api/complaints/RB-2026-0141/status",
            json={"status": "In Progress"}
        )
        assert res_403_status.status_code == 403
        assert "restricted" in res_403_status.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


def test_create_complaint_case_id_consistency_and_validation(client: TestClient):
    """
    Regression Test (Phase 1):
    1. Client-supplied valid Case ID is persisted and returned consistently.
    2. Invalid bureau prefix returns 400 Bad Request.
    3. Duplicate Case ID returns 409 Conflict.
    """
    from app.main import app
    session = WorkflowMockDBSession()

    mock_complainant = User(
        id="u0",
        name="Rohit Sharma",
        email="rohit.sharma@student.edu.in",
        role="Complainant",
        designation="Student",
        bureau="PGRC",
        status="Active",
    )

    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: mock_complainant
    try:
        payload = {
            "id": "PGRC-2026-7788",
            "title": "Consistent Case ID Verification",
            "description": "Testing that client-generated valid Case ID is persisted authoritatively.",
            "bureau": "PGRC",
            "category": "Fee Regulation",
            "priority": "Medium",
            "institutionId": "i1",
            "complainantType": "Student",
            "complainantName": "Rohit Sharma",
            "complainantEmail": "rohit.sharma@student.edu.in",
        }
        res = client.post("/api/complaints", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["id"] == "PGRC-2026-7788"
        assert any(c.id == "PGRC-2026-7788" for c in session.complaints)

        # Invalid prefix
        payload_bad_prefix = {**payload, "id": "INVALID-2026-7799"}
        res_bad = client.post("/api/complaints", json=payload_bad_prefix)
        assert res_bad.status_code == 400
        assert "does not match Bureau prefix" in res_bad.json()["detail"]

        # Duplicate ID
        res_dup = client.post("/api/complaints", json=payload)
        assert res_dup.status_code == 409
        assert "already exists" in res_dup.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_complaint_status_transition_rules_and_admin_reopen(client: TestClient):
    """
    Regression Test (Bug 1 - Case status dropdown & transitions):
    1. Pending allows transitioning to In Progress and Escalated.
    2. Pending -> Resolved directly without Admin override is rejected (400).
    3. In Progress -> Escalated and In Progress -> Resolved are permitted.
    4. Escalated -> In Progress and Escalated -> Resolved are permitted.
    5. Resolved case cannot transition without Admin override.
    6. System Admin can reopen Resolved -> In Progress with non-empty overrideReason.
    7. System Admin attempting reopen without overrideReason is rejected (400).
    8. Non-admin attempting arbitrary transition with overrideReason is rejected (400).
    9. Complainant role cannot update status (403).
    """
    from app.main import app
    session = WorkflowMockDBSession()

    user_admin = User(
        id="u1",
        name="Dr. S. Mehta",
        email="member-sec@aicte-india.org",
        role="Admin",
        designation="Member Secretary & System Admin",
        bureau="All",
        status="Active",
    )
    user_officer = User(
        id="u2",
        name="Rajesh Kumar",
        email="rajesh.kumar@aicte-india.org",
        role="Officer",
        designation="Senior Grievance Officer, PGRC",
        bureau="PGRC",
        status="Active",
    )
    user_complainant = User(
        id="u0",
        name="Rohit Sharma",
        email="rohit.sharma@student.edu.in",
        role="Complainant",
        designation="Student",
        bureau=None,
        status="Active",
    )

    app.dependency_overrides[get_db] = lambda: session

    # 1. Pending -> Escalated is permitted
    app.dependency_overrides[get_current_user] = lambda: user_admin
    try:
        res_pending_esc = client.patch(
            "/api/complaints/RB-2026-0141/status",
            json={"status": "Escalated", "remarks": "Escalated from pending intake"}
        )
        assert res_pending_esc.status_code == 200
        assert res_pending_esc.json()["status"] == "Escalated"

        # 2. Escalated -> In Progress is permitted
        res_esc_prog = client.patch(
            "/api/complaints/RB-2026-0141/status",
            json={"status": "In Progress", "remarks": "Assigned officer resumed investigation"}
        )
        assert res_esc_prog.status_code == 200
        assert res_esc_prog.json()["status"] == "In Progress"

        # 3. In Progress -> Resolved is permitted
        res_prog_res = client.patch(
            "/api/complaints/RB-2026-0141/status",
            json={"status": "Resolved", "remarks": "Full compliance reached"}
        )
        assert res_prog_res.status_code == 200
        assert res_prog_res.json()["status"] == "Resolved"

        # 4. Resolved -> In Progress without overrideReason fails (400)
        res_res_no_override = client.patch(
            "/api/complaints/RB-2026-0141/status",
            json={"status": "In Progress"}
        )
        assert res_res_no_override.status_code == 400
        assert "Resolved" in res_res_no_override.json()["detail"]

        # 5. System Admin can reopen with non-empty overrideReason
        res_admin_reopen = client.patch(
            "/api/complaints/RB-2026-0141/status",
            json={
                "status": "In Progress",
                "overrideReason": "New documentary evidence received from students.",
                "remarks": "Re-opened docket per statutory review order.",
            }
        )
        assert res_admin_reopen.status_code == 200
        assert res_admin_reopen.json()["status"] == "In Progress"

        # 6. Officer cannot perform invalid transition even with overrideReason
        app.dependency_overrides[get_current_user] = lambda: user_officer
        # c1 is In Progress. Trying to set to Pending (not in permitted transitions)
        res_officer_invalid = client.patch(
            "/api/complaints/PGRC-2026-0873/status",
            json={"status": "Pending", "overrideReason": "Officer trying override"}
        )
        assert res_officer_invalid.status_code == 400
        assert "not permitted" in res_officer_invalid.json()["detail"]

        # 7. Complainant cannot update status (403)
        app.dependency_overrides[get_current_user] = lambda: user_complainant
        res_complainant = client.patch(
            "/api/complaints/PGRC-2026-0873/status",
            json={"status": "Resolved"}
        )
        assert res_complainant.status_code == 403
    finally:
        app.dependency_overrides.clear()
