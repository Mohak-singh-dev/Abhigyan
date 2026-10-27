"""
Backend unit & integration tests for Phase 3:
- Persistent System Settings API & Database Backing
- Authorized System Admin can save, reload, and reset settings
- Unauthorized roles (Officer, Complainant, Bureau Admin) cannot modify settings
- Settings persist across reloads and authenticated sessions
- Validation guards (bounds, SLA hierarchy) prevent invalid state
- Similarity threshold dynamically filters open candidates in /api/overlaps
- Historical decisions (linked, dismissed, deferred) remain intact regardless of threshold
- SLA days setting dynamically calculates due dates for newly created complaints
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.auth import get_current_user
from app.models.user import User
from app.models.setting import SystemSetting
from app.database import SessionLocal

SYSTEM_ADMIN = User(
    id="u1",
    name="Dr. S. Mehta",
    email="member-sec@aicte-india.org",
    role="Admin",
    bureau="All",
    status="Active",
)

RB_BUREAU_ADMIN = User(
    id="u-rb-admin",
    name="RB Admin",
    email="rb-admin@aicte-india.org",
    role="BureauAdmin",
    bureau="RB",
    status="Active",
)

OFFICER_USER = User(
    id="u2",
    name="Rajesh Kumar",
    email="rajesh.kumar@aicte-india.org",
    role="Officer",
    bureau="PGRC",
    status="Active",
)

COMPLAINANT_USER = User(
    id="u0",
    name="Rohit Sharma",
    email="rohit.sharma@student.edu.in",
    role="Complainant",
    bureau=None,
    status="Active",
)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def reset_settings_fixture():
    """Ensure database settings are in clean default state before and after each test."""
    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter(SystemSetting.key == "global").first()
        if not setting:
            setting = SystemSetting(
                key="global",
                similarity_threshold=75,
                sla_critical=3,
                sla_high=7,
                sla_medium=14,
                auto_escalate=True,
                email_alerts=True,
                updated_by="Test Initialization",
                updated_at=datetime.now(timezone.utc),
            )
            db.add(setting)
        else:
            setting.similarity_threshold = 75
            setting.sla_critical = 3
            setting.sla_high = 7
            setting.sla_medium = 14
            setting.auto_escalate = True
            setting.email_alerts = True
            setting.updated_by = "Test Reset"
            setting.updated_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()

    yield

    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter(SystemSetting.key == "global").first()
        if setting:
            setting.similarity_threshold = 75
            setting.sla_critical = 3
            setting.sla_high = 7
            setting.sla_medium = 14
            setting.auto_escalate = True
            setting.email_alerts = True
            db.commit()
    finally:
        db.close()


def test_get_settings_authorized_roles(client):
    """All authenticated roles can read settings to align SLA and threshold interfaces."""
    for user in [SYSTEM_ADMIN, RB_BUREAU_ADMIN, OFFICER_USER, COMPLAINANT_USER]:
        app.dependency_overrides[get_current_user] = lambda u=user: u
        resp = client.get("/api/settings")
        assert resp.status_code == 200, f"Role {user.role} should be able to read settings"
        data = resp.json()
        assert data["similarity_threshold"] == 75
        assert data["similarityThreshold"] == 75
        assert data["sla_critical"] == 3
        assert data["sla_high"] == 7
        assert data["sla_medium"] == 14
        assert data["auto_escalate"] is True
        assert data["email_alerts"] is True
    app.dependency_overrides.clear()


def test_system_admin_update_settings_persists(client):
    """System Admin can update settings, which persist and reflect across sessions."""
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN
    payload = {
        "similarityThreshold": 80,
        "slaCritical": 2,
        "slaHigh": 6,
        "slaMedium": 12,
        "autoEscalate": False,
        "emailAlerts": True,
    }
    update_resp = client.put("/api/settings", json=payload)
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["similarity_threshold"] == 80
    assert updated_data["similarityThreshold"] == 80
    assert updated_data["sla_critical"] == 2
    assert updated_data["sla_high"] == 6
    assert updated_data["sla_medium"] == 12
    assert updated_data["auto_escalate"] is False
    assert updated_data["updated_by"] == "Dr. S. Mehta"

    # Reload from fresh GET request
    get_resp = client.get("/api/settings")
    assert get_resp.status_code == 200
    persisted = get_resp.json()
    assert persisted["similarity_threshold"] == 80
    assert persisted["sla_critical"] == 2
    assert persisted["sla_high"] == 6
    assert persisted["sla_medium"] == 12
    assert persisted["auto_escalate"] is False
    app.dependency_overrides.clear()


def test_unauthorized_roles_cannot_modify_settings(client):
    """Non-System Admin roles (Officer, Complainant, Bureau Admin) receive 403 Forbidden."""
    unauthorized_users = [OFFICER_USER, COMPLAINANT_USER, RB_BUREAU_ADMIN]
    payload = {"similarityThreshold": 88}

    for user in unauthorized_users:
        app.dependency_overrides[get_current_user] = lambda u=user: u
        resp = client.put("/api/settings", json=payload)
        assert resp.status_code == 403, f"{user.role} should be rejected with 403"
        assert "Only System Administrator" in resp.json()["detail"]

        # Ensure database was not modified
        app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN
        check_resp = client.get("/api/settings")
        assert check_resp.json()["similarity_threshold"] == 75

    app.dependency_overrides.clear()


def test_settings_validation_bounds_and_hierarchy(client):
    """Validation prevents out-of-bounds values and invalid SLA hierarchies."""
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN

    # 1. Similarity threshold below 50
    resp_low_sim = client.put("/api/settings", json={"similarityThreshold": 45})
    assert resp_low_sim.status_code in (400, 422)

    # 2. Similarity threshold above 95
    resp_high_sim = client.put("/api/settings", json={"similarityThreshold": 99})
    assert resp_high_sim.status_code in (400, 422)

    # 3. SLA hierarchy conflict: Critical >= High
    resp_hier_1 = client.put("/api/settings", json={"slaCritical": 8, "slaHigh": 7})
    assert resp_hier_1.status_code == 400
    assert "Critical severity SLA window must be shorter" in resp_hier_1.json()["detail"]

    # 4. SLA hierarchy conflict: High >= Medium
    resp_hier_2 = client.put("/api/settings", json={"slaHigh": 15, "slaMedium": 14})
    assert resp_hier_2.status_code == 400
    assert "High priority SLA window must be shorter" in resp_hier_2.json()["detail"]

    # Ensure authorative values did not change
    get_resp = client.get("/api/settings")
    assert get_resp.json()["similarity_threshold"] == 75
    assert get_resp.json()["sla_critical"] == 3
    assert get_resp.json()["sla_high"] == 7
    assert get_resp.json()["sla_medium"] == 14
    app.dependency_overrides.clear()


def test_similarity_threshold_filters_open_candidates_dynamically(client):
    """
    Changing the threshold filters open candidates in /api/overlaps dynamically,
    while historical decisions (linked, dismissed, deferred) remain intact.
    """
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN

    # 1. At default threshold (75%):
    resp_default = client.get("/api/overlaps?status=open")
    assert resp_default.status_code == 200
    open_overlaps = resp_default.json()
    # All returned open candidates must be >= 75
    for o in open_overlaps:
        assert o["similarity"] >= 75, f"Overlap {o['id']} ({o['similarity']}%) is below threshold 75%"

    # 2. Set threshold to 90% (Strict)
    client.put("/api/settings", json={"similarityThreshold": 90})
    resp_strict = client.get("/api/overlaps?status=open")
    assert resp_strict.status_code == 200
    strict_open = resp_strict.json()
    assert len(strict_open) > 0
    for o in strict_open:
        assert o["similarity"] >= 90, f"Overlap {o['id']} ({o['similarity']}%) is below strict threshold 90%"

    # 3. Verify that historical decisions (e.g. linked o2 with similarity 88% < 90%) remain visible and intact!
    resp_linked = client.get("/api/overlaps?status=linked")
    assert resp_linked.status_code == 200
    linked = resp_linked.json()
    linked_ids = [o["id"] for o in linked]
    assert "o2" in linked_ids or "o4" in linked_ids, "Historical linked overlaps must NOT be wiped by threshold"
    o2_record = next((o for o in linked if o["id"] == "o2"), None)
    if o2_record:
        assert o2_record["similarity"] == 88, "Historical linked similarity must be preserved"

    # 4. include_below_threshold=True allows inspection of below-threshold candidates
    resp_all_candidates = client.get("/api/overlaps?status=open&include_below_threshold=true")
    assert resp_all_candidates.status_code == 200
    assert len(resp_all_candidates.json()) >= len(strict_open)

    app.dependency_overrides.clear()


def test_threshold_90_percent_with_91_pending_88_unreviewed_and_88_historical(client):
    """
    Regression Test (Bug 2 - Similarity threshold filtering & counts):
    - With threshold 90%, a 91% Pending Review candidate remains eligible.
    - An 88% unreviewed candidate does NOT appear in the active review queue.
    - An 88% historical decision (Confirmed Related / linked) remains preserved,
      never deleted or auto-dismissed, and is excluded from active pending counts.
    - Re-querying after reload confirms persistence and proper queue separation.
    """
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN

    # 1. Persist threshold to 90%
    put_res = client.put("/api/settings", json={"similarityThreshold": 90})
    assert put_res.status_code == 200
    assert put_res.json()["similarity_threshold"] == 90

    # 2. Verify persistence on GET /api/settings
    settings_res = client.get("/api/settings")
    assert settings_res.status_code == 200
    assert settings_res.json()["similarity_threshold"] == 90

    # 3. Create an 88% unreviewed open candidate between two distinct complaints
    db = SessionLocal()
    try:
        from app.models.complaint import Complaint
        from app.models.overlap import ComplaintOverlap
        c1 = db.query(Complaint).filter(Complaint.id == "PGRC-2026-9901").first()
        if not c1:
            db.add(Complaint(
                id="PGRC-2026-9901",
                institution_id="i1",
                bureau="PGRC",
                category="Fee Regulation",
                priority="High",
                officer="Rajesh Kumar",
                status="Pending",
                date="2026-10-20",
                due="2026-10-30",
                title="Test Candidate Complaint 1",
                description="Test Candidate Complaint 1",
            ))
        c2 = db.query(Complaint).filter(Complaint.id == "RB-2026-9902").first()
        if not c2:
            db.add(Complaint(
                id="RB-2026-9902",
                institution_id="i1",
                bureau="RB",
                category="Fee Regulation",
                priority="High",
                officer="Anita Verma",
                status="Pending",
                date="2026-10-20",
                due="2026-10-30",
                title="Test Candidate Complaint 2",
                description="Test Candidate Complaint 2",
            ))
        db.query(ComplaintOverlap).filter(
            (ComplaintOverlap.complaint_a_id == "PGRC-2026-9901") |
            (ComplaintOverlap.complaint_b_id == "PGRC-2026-9901")
        ).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()

    create_payload = {
        "complaint_a_id": "PGRC-2026-9901",
        "complaint_b_id": "RB-2026-9902",
        "similarity": 88,
        "reasons": ["Test 88% unreviewed candidate"],
    }
    create_res = client.post("/api/overlaps", json=create_payload)
    assert create_res.status_code in (200, 201)
    cand_88_id = create_res.json()["id"]

    # 4. Fetch active open candidate queue
    open_res = client.get("/api/overlaps?status=open")
    assert open_res.status_code == 200
    open_overlaps = open_res.json()
    open_ids = [o["id"] for o in open_overlaps]

    # Candidate o3 (91% similarity) MUST be in the active review queue
    assert "o3" in open_ids, "91% pending candidate o3 must be eligible at 90% threshold"
    o3 = next(o for o in open_overlaps if o["id"] == "o3")
    assert o3["similarity"] == 91

    # Candidate cand_88_id (88% similarity) MUST NOT appear in the active review queue
    assert cand_88_id not in open_ids, "88% unreviewed candidate must be filtered out at 90% threshold"

    # Historical decision o2 (88% similarity, linked) MUST NOT appear in the open review queue
    assert "o2" not in open_ids, "88% linked decision o2 must not inflate active pending queue"

    # 5. Fetch all overlaps (default list: active candidates + historical decisions)
    all_res = client.get("/api/overlaps")
    assert all_res.status_code == 200
    all_overlaps = all_res.json()
    all_ids = [o["id"] for o in all_overlaps]

    # Historical decision o2 (88% similarity, status: linked) MUST remain intact
    assert "o2" in all_ids, "Historical 88% linked decision o2 must be preserved"
    o2 = next(o for o in all_overlaps if o["id"] == "o2")
    assert o2["similarity"] == 88
    assert o2["status"] == "linked"

    # 88% unreviewed candidate is NOT in the default list because it's unreviewed below threshold
    assert cand_88_id not in all_ids, "88% unreviewed candidate must not appear in default list at 90% threshold"

    # 6. Below-threshold unreviewed candidates are accessible via include_below_threshold=true
    audit_res = client.get("/api/overlaps?status=open&include_below_threshold=true")
    assert audit_res.status_code == 200
    audit_ids = [o["id"] for o in audit_res.json()]
    assert cand_88_id in audit_ids, "88% unreviewed candidate is retrievable when below-threshold candidates are requested"

    # 7. Convert 88% candidate into a historical decision (Dismissed)
    dec_res = client.patch(
        f"/api/overlaps/{cand_88_id}/decision",
        json={"state": "dismissed", "justification": "Historical dismissal of 88% overlap"},
    )
    assert dec_res.status_code == 200

    # 8. Re-query all overlaps: now that cand_88_id is historical, it is preserved and visible!
    recheck_res = client.get("/api/overlaps")
    assert recheck_res.status_code == 200
    recheck_ids = [o["id"] for o in recheck_res.json()]
    assert cand_88_id in recheck_ids, "Historical decision on 88% candidate must be preserved regardless of threshold"

    # And it still does NOT appear in active open queue
    open_recheck = client.get("/api/overlaps?status=open").json()
    assert cand_88_id not in [o["id"] for o in open_recheck], "Historical decision must not inflate pending count"

    app.dependency_overrides.clear()




def test_sla_setting_affects_complaint_creation_due_date(client):
    """New complaints calculate due date based on the persisted SLA settings."""
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN

    # Set custom SLA windows: Critical=2 days, High=5 days, Medium=10 days
    client.put("/api/settings", json={
        "slaCritical": 2,
        "slaHigh": 5,
        "slaMedium": 10,
    })

    # File a Critical complaint as Complainant
    app.dependency_overrides[get_current_user] = lambda: COMPLAINANT_USER
    payload_crit = {
        "institutionId": "i1",
        "bureau": "RB",
        "category": "Regulatory Violation",
        "priority": "Critical",
        "title": "Hazardous wiring in hostel lab",
        "description": "Urgent hazard requiring rapid inspection.",
        "complainantType": "Student",
    }
    resp_crit = client.post("/api/complaints", json=payload_crit)
    assert resp_crit.status_code == 201
    crit_data = resp_crit.json()
    filing_date = datetime.strptime(crit_data["date"], "%Y-%m-%d")
    due_date = datetime.strptime(crit_data["due"], "%Y-%m-%d")
    assert (due_date - filing_date).days == 2, f"Critical due date should be 2 days from filing, got {(due_date - filing_date).days}"

    # File a High priority complaint
    payload_high = {
        "institutionId": "i1",
        "bureau": "PGRC",
        "category": "Fee Refund Issues",
        "priority": "High",
        "title": "Mandatory capitation deposit dispute",
        "description": "Excess charges levied on admission.",
        "complainantType": "Student",
    }
    resp_high = client.post("/api/complaints", json=payload_high)
    assert resp_high.status_code == 201
    high_data = resp_high.json()
    filing_high = datetime.strptime(high_data["date"], "%Y-%m-%d")
    due_high = datetime.strptime(high_data["due"], "%Y-%m-%d")
    assert (due_high - filing_high).days == 5, f"High due date should be 5 days from filing, got {(due_high - filing_high).days}"

    app.dependency_overrides.clear()


def test_reset_settings_to_defaults(client):
    """System Admin can reset settings back to demonstration defaults."""
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN

    # First alter settings
    client.put("/api/settings", json={"similarityThreshold": 88, "slaCritical": 4, "slaHigh": 8, "slaMedium": 16})
    check_altered = client.get("/api/settings").json()
    assert check_altered["similarity_threshold"] == 88

    # Now reset
    reset_resp = client.post("/api/settings/reset")
    assert reset_resp.status_code == 200
    reset_data = reset_resp.json()
    assert reset_data["similarity_threshold"] == 75
    assert reset_data["sla_critical"] == 3
    assert reset_data["sla_high"] == 7
    assert reset_data["sla_medium"] == 14

    # Non-Admin reset attempt is rejected
    app.dependency_overrides[get_current_user] = lambda: OFFICER_USER
    officer_reset = client.post("/api/settings/reset")
    assert officer_reset.status_code == 403

    app.dependency_overrides.clear()
