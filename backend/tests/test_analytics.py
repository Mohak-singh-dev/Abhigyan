import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.auth import get_current_user
from app.models.base import Base
from app.models.user import User
from app.models.institution import Institution
from app.models.complaint import Complaint
from app.models.overlap import ComplaintOverlap
from app.models.setting import SystemSetting

# In-memory SQLite engine with StaticPool so all connections share the same memory db
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sample Users for Scoping Tests
TEST_ADMIN = User(
    id="u_admin",
    name="System Administrator",
    email="admin@aicte-india.org",
    role="Admin",
    designation="System Admin",
    bureau="All",
    status="Active",
)

TEST_BUREAU_ADMIN_RB = User(
    id="u_ba_rb",
    name="Anita Verma",
    email="anita.verma@aicte-india.org",
    role="BureauAdmin",
    designation="Bureau Head, RB",
    bureau="RB",
    status="Active",
)

TEST_OFFICER_PGRC = User(
    id="u_off_pgrc",
    name="Rajesh Kumar",
    email="rajesh.kumar@aicte-india.org",
    role="Officer",
    designation="Senior Grievance Officer",
    bureau="PGRC",
    status="Active",
)

TEST_COMPLAINANT = User(
    id="u_comp",
    name="Rohit Sharma",
    email="rohit.sharma@student.ac.in",
    role="Complainant",
    designation="Student",
    bureau="PGRC",
    status="Active",
)


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create dummy institution
    inst = Institution(
        id="i1",
        aicte_id="1-10001",
        name="Apex Institute of Technology",
        city="New Delhi",
        state="Delhi",
        type="Engineering",
        approved="2010",
    )
    db.add(inst)

    # Seed system setting
    setting = SystemSetting(
        key="global",
        similarity_threshold=75,
        sla_critical=3,
        sla_high=7,
        sla_medium=14,
        auto_escalate=True,
        email_alerts=True,
    )
    db.add(setting)

    db.commit()
    db.close()

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


def test_admin_dashboard_aggregates(client: TestClient):
    """System Admin retrieves organization-wide aggregates with accurate counts and status definitions."""
    app.dependency_overrides[get_current_user] = lambda: TEST_ADMIN

    db = TestingSessionLocal()
    # Seed complaints:
    # 1. RB - Pending - Critical - Due 2026-10-20 (Overdue relative to 2026-10-25)
    c1 = Complaint(
        id="RB-2026-1001",
        institution_id="i1",
        bureau="RB",
        category="Fee Regulation",
        priority="Critical",
        status="Pending",
        officer="Anita Verma",
        assigned_user_id="u_ba_rb",
        date="2026-10-10",
        due="2026-10-20",
        title="Excess Fee Collection",
        description="Overcharging B.Tech students",
        complainant_user_id="u_other",
        complainant_email="other@test.com",
    )
    # 2. RB - In Progress - High - Due 2026-10-28 (Not overdue relative to 2026-10-25)
    c2 = Complaint(
        id="RB-2026-1002",
        institution_id="i1",
        bureau="RB",
        category="Faculty Norms",
        priority="High",
        status="In Progress",
        officer="Anita Verma",
        assigned_user_id="u_ba_rb",
        date="2026-10-12",
        due="2026-10-28",
        title="Faculty Shortage",
        description="Department has 50% vacancies",
        complainant_user_id="u_other",
        complainant_email="other@test.com",
    )
    # 3. PGRC - Resolved - Medium - Due 2026-10-15 - Resolved on 2026-10-14 (Resolved is never overdue!)
    c3 = Complaint(
        id="PGRC-2026-2001",
        institution_id="i1",
        bureau="PGRC",
        category="Hostel Grievance",
        priority="Medium",
        status="Resolved",
        officer="Rajesh Kumar",
        assigned_user_id="u_off_pgrc",
        date="2026-10-01",
        due="2026-10-15",
        last_action_date="2026-10-14",
        title="Hostel Water Issue",
        description="Drinking water contaminated",
        complainant_user_id="u_comp",
        complainant_email="rohit.sharma@student.ac.in",
    )
    # 4. Approval - Escalated - Low - Due 2026-10-22 (Overdue relative to 2026-10-25)
    c4 = Complaint(
        id="AB-2026-3001",
        institution_id="i1",
        bureau="Approval",
        category="Infrastructure",
        priority="Low",
        status="Escalated",
        officer="Suresh Patel",
        assigned_user_id="u_other_off",
        date="2026-09-20",
        due="2026-10-22",
        title="Lab Setup Incomplete",
        description="Inspection showed non-functional labs",
        complainant_user_id="u_other",
        complainant_email="other@test.com",
    )
    db.add_all([c1, c2, c3, c4])
    db.commit()
    db.close()

    res = client.get("/api/analytics/dashboard?asOfDate=2026-10-25")
    assert res.status_code == 200
    data = res.json()
    kpis = data["kpis"]

    assert kpis["total"] == 4
    assert kpis["pending"] == 1
    assert kpis["inProgress"] == 1
    assert kpis["resolved"] == 1
    assert kpis["escalated"] == 1
    assert kpis["underInvestigation"] == 2  # pending + inProgress
    assert kpis["overdue"] == 2  # c1 (due 10-20, Pending) and c4 (due 10-22, Escalated); c3 is Resolved
    assert kpis["criticalHigh"] == 2  # c1 (Critical), c2 (High)
    assert kpis["resolutionRate"] == 25  # 1 out of 4 = 25%

    # Check bureau breakdown
    breakdown = {b["name"]: b for b in data["bureauBreakdown"]}
    assert breakdown["RB"]["Total"] == 2
    assert breakdown["RB"]["Pending"] == 1
    assert breakdown["RB"]["In Progress"] == 1
    assert breakdown["PGRC"]["Total"] == 1
    assert breakdown["PGRC"]["Resolved"] == 1
    assert breakdown["Approval"]["Total"] == 1
    assert breakdown["Approval"]["Escalated"] == 1

    # Check priority distribution
    prio_map = {p["name"]: p["value"] for p in data["priorityDistribution"]}
    assert prio_map["Critical"] == 1
    assert prio_map["High"] == 1
    assert prio_map["Medium"] == 1
    assert prio_map["Low"] == 1

    # Recent cases
    assert len(data["recentCases"]) == 4


def test_complainant_scoping_restricted_to_own_cases(client: TestClient):
    """Complainants only see aggregate metrics for complaints they submitted."""
    app.dependency_overrides[get_current_user] = lambda: TEST_COMPLAINANT

    db = TestingSessionLocal()
    # Complainant's case
    c1 = Complaint(
        id="PGRC-2026-2001",
        institution_id="i1",
        bureau="PGRC",
        category="Hostel Grievance",
        priority="Medium",
        status="Resolved",
        officer="Rajesh Kumar",
        assigned_user_id="u_off_pgrc",
        date="2026-10-01",
        due="2026-10-15",
        last_action_date="2026-10-14",
        title="Hostel Water Issue",
        description="Drinking water contaminated",
        complainant_user_id="u_comp",
        complainant_email="rohit.sharma@student.ac.in",
    )
    # Another user's case in same bureau
    c2 = Complaint(
        id="PGRC-2026-2002",
        institution_id="i1",
        bureau="PGRC",
        category="Fee Grievance",
        priority="High",
        status="Pending",
        officer="Rajesh Kumar",
        assigned_user_id="u_off_pgrc",
        date="2026-10-02",
        due="2026-10-25",
        title="Unauthorized Fee",
        description="Fee issue",
        complainant_user_id="u_someone_else",
        complainant_email="someone@other.edu",
    )
    # Another bureau case
    c3 = Complaint(
        id="RB-2026-1001",
        institution_id="i1",
        bureau="RB",
        category="Regulatory Norms",
        priority="Critical",
        status="In Progress",
        officer="Anita Verma",
        date="2026-10-03",
        due="2026-10-25",
        title="Infrastructure gap",
        description="RB case",
        complainant_user_id="u_someone_else",
        complainant_email="someone@other.edu",
    )
    db.add_all([c1, c2, c3])
    db.commit()
    db.close()

    res = client.get("/api/analytics/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["kpis"]["total"] == 1
    assert data["kpis"]["resolved"] == 1
    assert data["kpis"]["pending"] == 0
    assert data["kpis"]["pendingOverlaps"] == 0  # Complainants cannot see overlap metrics


def test_officer_scoping_restricted_to_assigned_cases(client: TestClient):
    """Officers only see aggregate metrics for cases explicitly assigned to them."""
    app.dependency_overrides[get_current_user] = lambda: TEST_OFFICER_PGRC

    db = TestingSessionLocal()
    # Assigned to Rajesh Kumar
    c1 = Complaint(
        id="PGRC-2026-2001",
        institution_id="i1",
        bureau="PGRC",
        category="Fee Issue",
        priority="High",
        status="In Progress",
        officer="Rajesh Kumar",
        assigned_user_id="u_off_pgrc",
        date="2026-10-01",
        due="2026-10-25",
        title="Fee Overcharge",
        description="Assigned to Rajesh Kumar",
    )
    # In PGRC but assigned to another officer (different user_id and different name)
    c2 = Complaint(
        id="PGRC-2026-2002",
        institution_id="i1",
        bureau="PGRC",
        category="Library Norms",
        priority="Medium",
        status="Pending",
        officer="Meera Iyer",
        assigned_user_id="u_other",
        date="2026-10-02",
        due="2026-10-25",
        title="Library closed",
        description="Assigned to Meera Iyer",
    )
    # Reassigned away to another officer: officer field still contains 'Rajesh Kumar',
    # but assigned_user_id is 'u_other'. Authoritative ID MUST take precedence over display name!
    c3 = Complaint(
        id="PGRC-2026-2003",
        institution_id="i1",
        bureau="PGRC",
        category="Hostel Grievance",
        priority="Low",
        status="Pending",
        officer="Rajesh Kumar",
        assigned_user_id="u_other",
        date="2026-10-03",
        due="2026-10-25",
        title="Hostel water",
        description="Stale display name test description",
    )
    # Legacy record where assigned_user_id is None, officer is 'Rajesh Kumar'
    c4 = Complaint(
        id="PGRC-2026-2004",
        institution_id="i1",
        bureau="PGRC",
        category="Lab Equipment",
        priority="Low",
        status="Pending",
        officer="Rajesh Kumar",
        assigned_user_id=None,
        date="2026-10-04",
        due="2026-10-25",
        title="Lab equipment",
        description="Legacy unassigned case with officer display name",
    )
    db.add_all([c1, c2, c3, c4])
    db.commit()
    db.close()

    res = client.get("/api/analytics/dashboard")
    assert res.status_code == 200
    data = res.json()
    # Total should be 2: c1 (explicitly assigned u_off_pgrc) + c4 (legacy None with matching officer name)
    # c3 (assigned to u_other) must be excluded even though officer string says 'Rajesh Kumar'
    assert data["kpis"]["total"] == 2
    assert data["kpis"]["inProgress"] == 1  # c1
    assert data["kpis"]["pending"] == 1  # c4
    case_ids = {c["id"] for c in data["recentCases"]}
    assert "PGRC-2026-2001" in case_ids
    assert "PGRC-2026-2004" in case_ids
    assert "PGRC-2026-2003" not in case_ids


def test_bureau_admin_scoping_and_cross_bureau_rejection(client: TestClient):
    """Bureau Admin sees only authorized bureau cases; attempting to query another bureau yields 403 Forbidden."""
    app.dependency_overrides[get_current_user] = lambda: TEST_BUREAU_ADMIN_RB

    db = TestingSessionLocal()
    c_rb = Complaint(
        id="RB-2026-1001",
        institution_id="i1",
        bureau="RB",
        category="Norms",
        priority="High",
        status="Pending",
        officer="Anita Verma",
        date="2026-10-01",
        due="2026-10-20",
        title="RB Case",
        description="Detailed grievance description regarding RB regulations",
    )
    c_pgrc = Complaint(
        id="PGRC-2026-2001",
        institution_id="i1",
        bureau="PGRC",
        category="Ragging",
        priority="Critical",
        status="Pending",
        officer="Rajesh Kumar",
        date="2026-10-01",
        due="2026-10-20",
        title="PGRC Case",
        description="Detailed grievance description regarding PGRC matter",
    )
    db.add_all([c_rb, c_pgrc])
    db.commit()
    db.close()

    # Query without bureau filter (scoped automatically to RB)
    res = client.get("/api/analytics/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["kpis"]["total"] == 1
    assert data["bureauBreakdown"][0]["name"] == "RB"
    assert data["bureauBreakdown"][0]["Total"] == 1

    # Query with matching authorized bureau
    res_rb = client.get("/api/analytics/dashboard?bureau=RB")
    assert res_rb.status_code == 200
    assert res_rb.json()["kpis"]["total"] == 1

    # Attempt to query unauthorized bureau PGRC -> 403 Forbidden
    res_forbidden = client.get("/api/analytics/dashboard?bureau=PGRC")
    assert res_forbidden.status_code == 403
    assert "Restricted: Bureau Admin jurisdiction is RB" in res_forbidden.json()["detail"]


def test_date_range_filters(client: TestClient):
    """Analytics filters respect startDate and endDate on complaint filing date."""
    app.dependency_overrides[get_current_user] = lambda: TEST_ADMIN

    db = TestingSessionLocal()
    c_aug = Complaint(
        id="RB-2026-1001",
        institution_id="i1",
        bureau="RB",
        category="Norms",
        priority="Low",
        status="Resolved",
        officer="Anita Verma",
        date="2026-08-15",
        due="2026-09-15",
        title="August Case",
        description="August case description exceeding minimum length",
    )
    c_sep = Complaint(
        id="RB-2026-1002",
        institution_id="i1",
        bureau="RB",
        category="Norms",
        priority="Medium",
        status="Pending",
        officer="Anita Verma",
        date="2026-09-10",
        due="2026-10-10",
        title="September Case",
        description="September case description exceeding minimum length",
    )
    c_oct = Complaint(
        id="RB-2026-1003",
        institution_id="i1",
        bureau="RB",
        category="Norms",
        priority="High",
        status="In Progress",
        officer="Anita Verma",
        date="2026-10-05",
        due="2026-10-25",
        title="October Case",
        description="October case description exceeding minimum length",
    )
    db.add_all([c_aug, c_sep, c_oct])
    db.commit()
    db.close()

    # Filter for September only
    res = client.get("/api/analytics/dashboard?startDate=2026-09-01&endDate=2026-09-30")
    assert res.status_code == 200
    data = res.json()
    assert data["kpis"]["total"] == 1
    assert data["recentCases"][0]["id"] == "RB-2026-1002"


def test_empty_dataset_handling(client: TestClient):
    """Empty database or filters matching no records return 0 aggregates without throwing errors."""
    app.dependency_overrides[get_current_user] = lambda: TEST_ADMIN

    res_dash = client.get("/api/analytics/dashboard")
    assert res_dash.status_code == 200
    dash_data = res_dash.json()
    assert dash_data["kpis"]["total"] == 0
    assert dash_data["kpis"]["pending"] == 0
    assert dash_data["kpis"]["resolved"] == 0
    assert dash_data["kpis"]["resolutionRate"] == 0
    assert dash_data["recentCases"] == []

    res_rep = client.get("/api/analytics/reports")
    assert res_rep.status_code == 200
    rep_data = res_rep.json()
    assert rep_data["kpis"]["total"] == 0
    assert rep_data["kpis"]["resolved"] == 0
    assert rep_data["kpis"]["resolutionRate"] == 0
    assert rep_data["kpis"]["avgTurnaroundDays"] is None
    assert rep_data["categoryDistribution"] == []
    assert rep_data["monthlyTrends"] == []
    assert "No complaint records match" in rep_data["dataNote"]


def test_reports_analytics_historical_trends_and_turnaround(client: TestClient):
    """Reports analytics calculates real monthly intake/closure and average turnaround days without fake data."""
    app.dependency_overrides[get_current_user] = lambda: TEST_ADMIN

    db = TestingSessionLocal()
    # Case filed in Aug and resolved in Aug (turnaround: 5 days)
    c1 = Complaint(
        id="RB-2026-0001",
        institution_id="i1",
        bureau="RB",
        category="Fee Norms",
        priority="Medium",
        status="Resolved",
        officer="Anita Verma",
        date="2026-08-10",
        due="2026-08-25",
        last_action_date="2026-08-15",
        title="Aug Resolved",
        description="Resolved in 5 days",
    )
    # Case filed in Sep and resolved in Sep (turnaround: 15 days)
    c2 = Complaint(
        id="PGRC-2026-0002",
        institution_id="i1",
        bureau="PGRC",
        category="Hostel Grievance",
        priority="High",
        status="Resolved",
        officer="Rajesh Kumar",
        date="2026-09-01",
        due="2026-09-20",
        last_action_date="2026-09-16",
        title="Sep Resolved",
        description="Resolved in 15 days",
    )
    # Case filed in Oct and still pending
    c3 = Complaint(
        id="AB-2026-0003",
        institution_id="i1",
        bureau="Approval",
        category="Infrastructure",
        priority="Low",
        status="Pending",
        officer="Suresh Patel",
        date="2026-10-05",
        due="2026-11-05",
        title="Oct Pending",
        description="Pending",
    )
    # Seed an overlap to test redundancy rate
    ov = ComplaintOverlap(
        id="ov1",
        complaint_a_id="RB-2026-0001",
        complaint_b_id="PGRC-2026-0002",
        similarity=85,
        reasons=["Duplicate fee grievance"],
        status="linked",
        decision_state="linked",
    )
    db.add_all([c1, c2, c3, ov])
    db.commit()
    db.close()

    res = client.get("/api/analytics/reports")
    assert res.status_code == 200
    data = res.json()

    assert data["kpis"]["total"] == 3
    assert data["kpis"]["resolved"] == 2
    assert data["kpis"]["resolutionRate"] == 67  # 2/3 = 66.67% -> 67%
    # Average turnaround: (5 + 15) / 2 = 10.0 days
    assert data["kpis"]["avgTurnaroundDays"] == 10.0
    # Overlap redundancy rate: 1 linked out of 1 = 100%
    assert data["kpis"]["redundancyPreventedRate"] == 100

    # Monthly trends check: must contain only Aug, Sep, Oct (no fabricated May/Jun/Jul)
    months = [m["monthKey"] for m in data["monthlyTrends"]]
    assert months == ["2026-08", "2026-09", "2026-10"]

    trend_by_month = {m["monthKey"]: m for m in data["monthlyTrends"]}
    assert trend_by_month["2026-08"]["Filed"] == 1
    assert trend_by_month["2026-08"]["Resolved"] == 1

    assert trend_by_month["2026-09"]["Filed"] == 1
    assert trend_by_month["2026-09"]["Resolved"] == 1

    assert trend_by_month["2026-10"]["Filed"] == 1
    assert trend_by_month["2026-10"]["Resolved"] == 0


def test_unauthenticated_analytics_rejected(client: TestClient):
    """Requests without authentication token return 401 Unauthorized."""
    # Temporarily remove default auth override
    app.dependency_overrides.pop(get_current_user, None)

    res_dash = client.get("/api/analytics/dashboard")
    assert res_dash.status_code == 401

    res_rep = client.get("/api/analytics/reports")
    assert res_rep.status_code == 401
