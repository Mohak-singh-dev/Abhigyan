import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.database import get_db
from app.models.complaint import Complaint
from app.models.timeline import ComplaintTimeline
from app.models.user import User
from app.auth import get_current_user

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
