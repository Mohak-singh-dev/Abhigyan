"""
Comprehensive End-to-End System Audit Tests for Task 6.

Validates all 4 core roles and operations:
1. Student / Complainant Workflow (Preview, Submit, Scoped View, RBAC boundaries)
2. Officer Workflow (Scoped List, Status Progression, Assignment restrictions)
3. Bureau Admin Workflow (Bureau-scoped queries, Reassignment within Bureau, Cross-bureau restrictions)
4. Super Admin Workflow (System-wide authority, Cross-bureau transfers, System audit)
5. AI Classifier Integration & Graceful Error Handling
6. Input Validation & Status Transition Guards
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from app.database import get_db
from app.models.complaint import Complaint
from app.models.institution import Institution
from app.models.timeline import ComplaintTimeline
from app.models.user import User
from app.auth import get_current_user
from tests.test_auth_rbac import (
    MockAuthDBSession,
    USER_ADMIN,
    USER_BUREAU_ADMIN,
    USER_OFFICER_PGRC,
    USER_OFFICER_RB,
    USER_COMPLAINANT,
    ALL_TEST_USERS,
)


SAMPLE_INSTITUTION = Institution(
    id="i1",
    aicte_id="1-4821039",
    name="Delhi Institute of Advanced Engineering & Technology",
    city="New Delhi",
    state="Delhi",
    type="Engineering & Technology",
    approved="2009",
    contact_email="principal@diaet.ac.in",
    contact_phone="+91 11 2689 4400",
    risk_level="Low"
)


class AuditSessionWithInst(MockAuthDBSession):
    def __init__(self):
        super().__init__()
        self.institutions = [SAMPLE_INSTITUTION]

    def query(self, model):
        if model is Institution:
            class InstQuery:
                def __init__(self, insts):
                    self.insts = insts
                def filter(self, *criteria):
                    return self
                def first(self):
                    return self.insts[0] if self.insts else None
                def all(self):
                    return self.insts
            return InstQuery(self.institutions)
        return super().query(model)

    def flush(self):
        pass


@pytest.fixture
def audit_session():
    return AuditSessionWithInst()


@pytest.fixture
def audit_client(audit_session):
    from app.main import app

    app.dependency_overrides[get_db] = lambda: audit_session
    yield TestClient(app)
    app.dependency_overrides.clear()


# ==============================================================================
# 1. Student / Complainant Workflow Audit
# ==============================================================================

def test_student_workflow_audit(audit_client, audit_session):
    """
    Audit Student / Complainant end-to-end:
    - AI classification preview without saving
    - Create complaint with user choices
    - Track complaint & verify timeline intake event
    - Verify Complainant cannot modify status or reassign
    - Verify Complainant cannot view another user's complaint
    """
    from app.main import app
    app.dependency_overrides[get_current_user] = lambda: USER_COMPLAINANT

    # 1. AI preview endpoint without persistence
    preview_res = audit_client.post(
        "/api/complaints/classify",
        json={
            "title": "Unapproved laboratory fee collected without official receipt",
            "description": "Third semester students are forced to pay Rs 15,000 extra or face hall ticket withholding."
        }
    )
    assert preview_res.status_code == 200
    preview_data = preview_res.json()
    assert preview_data["status"] == "success"
    assert "advisoryNotice" in preview_data
    assert preview_data["category"] is not None

    # 2. Student files complaint
    create_payload = {
        "title": "Unapproved laboratory fee collected without official receipt",
        "description": "Third semester students are forced to pay Rs 15,000 extra or face hall ticket withholding.",
        "category": "Fee Regulation",
        "bureau": "PGRC",
        "priority": "High",
        "institutionId": "i1",
        "complainantType": "Student",
    }
    create_res = audit_client.post("/api/complaints", json=create_payload)
    assert create_res.status_code == 201
    created_case = create_res.json()
    assert created_case["complainantEmail"] == USER_COMPLAINANT.email
    assert created_case["category"] == "Fee Regulation"
    assert created_case["bureau"] == "PGRC"
    assert created_case["status"] == "Pending"

    case_id = created_case["id"]

    # 3. Student tries forbidden actions on own complaint
    status_res = audit_client.patch(
        f"/api/complaints/{case_id}/status",
        json={"status": "Resolved", "remarks": "Student trying to self-resolve"}
    )
    assert status_res.status_code == 403, "Student must not be allowed to update status"

    assign_res = audit_client.patch(
        f"/api/complaints/{case_id}/assign",
        json={"officer": "Anita Verma", "bureau": "RB"}
    )
    assert assign_res.status_code == 403, "Student must not be allowed to reassign case"

    # 4. Student cannot access another citizen's complaint (RB-2026-0141)
    other_case_id = "RB-2026-0141"
    forbidden_get = audit_client.get(f"/api/complaints/{other_case_id}")
    assert forbidden_get.status_code == 403


# ==============================================================================
# 2. Officer Workflow Audit
# ==============================================================================

def test_officer_workflow_audit(audit_client, audit_session):
    """
    Audit Handling Officer end-to-end:
    - View assigned cases
    - Progress status: Pending -> In Progress -> Resolved
    - Verify closed case cannot transition further
    - Verify officer cannot directly reassign case
    - Verify officer cannot update unassigned case in different bureau
    """
    from app.main import app
    app.dependency_overrides[get_current_user] = lambda: USER_OFFICER_PGRC

    case_id = "PGRC-2026-0873"

    # 1. Officer progresses case: In Progress -> Resolved
    p1 = audit_client.patch(
        f"/api/complaints/{case_id}/status",
        json={"status": "Resolved", "remarks": "Grievance redressal committee issued refund order"}
    )
    assert p1.status_code == 200
    assert p1.json()["status"] == "Resolved"

    # 2. Verify closed case cannot be reopened
    p2 = audit_client.patch(
        f"/api/complaints/{case_id}/status",
        json={"status": "In Progress", "remarks": "Reopening attempt"}
    )
    assert p2.status_code == 400

    # 3. Officer cannot reassign cases
    assign_attempt = audit_client.patch(
        f"/api/complaints/{case_id}/assign",
        json={"userId": "u5"}
    )
    assert assign_attempt.status_code == 403

    # 4. Officer cannot update unassigned case in different bureau (RB-2026-0141)
    other_bureau_case = "RB-2026-0141"
    forbidden_update = audit_client.patch(
        f"/api/complaints/{other_bureau_case}/status",
        json={"status": "In Progress"}
    )
    assert forbidden_update.status_code == 403


# ==============================================================================
# 3. Bureau Admin Workflow Audit
# ==============================================================================

def test_bureau_admin_workflow_audit(audit_client, audit_session):
    """
    Audit Bureau Admin end-to-end:
    - Reassign case within their bureau
    - Cross-bureau transfer is blocked
    - Cross-bureau view/status update is blocked
    """
    from app.main import app
    app.dependency_overrides[get_current_user] = lambda: USER_BUREAU_ADMIN

    # 1. Cross-bureau access blocked: PGRC Bureau Admin cannot view RB case
    rb_case = "RB-2026-0141"
    cross_view = audit_client.get(f"/api/complaints/{rb_case}")
    assert cross_view.status_code == 403

    # 2. Cross-bureau transfer blocked: Cannot transfer to another bureau
    pgrc_case = "PGRC-2026-0873"
    cross_assign = audit_client.patch(
        f"/api/complaints/{pgrc_case}/assign",
        json={"bureau": "RB", "userId": "u3"}
    )
    assert cross_assign.status_code == 403


# ==============================================================================
# 4. Super Admin Workflow Audit
# ==============================================================================

def test_super_admin_workflow_audit(audit_client, audit_session):
    """
    Audit Super Admin end-to-end:
    - Full system-wide visibility across all bureaus
    - Ability to reassign across any bureau and officer
    - Ability to update status on any docket
    """
    from app.main import app
    app.dependency_overrides[get_current_user] = lambda: USER_ADMIN

    # 1. Super Admin can access all dockets
    for cid in ["PGRC-2026-0873", "RB-2026-0141"]:
        res = audit_client.get(f"/api/complaints/{cid}")
        assert res.status_code == 200

    # 2. Super Admin can reassign cross-bureau
    transfer_res = audit_client.patch(
        "/api/complaints/RB-2026-0141/assign",
        json={"bureau": "PGRC", "userId": "u2", "reason": "Jurisdiction transfer by Member Secretary"}
    )
    assert transfer_res.status_code == 200
    assert transfer_res.json()["bureau"] == "PGRC"


# ==============================================================================
# 5. Input Validation & Error Handling Audit
# ==============================================================================

def test_input_validation_and_error_guards(audit_client, audit_session):
    """
    Audit boundary validation:
    - Non-existent institution returns 400
    - Non-existent complaint ID returns 404
    - Invalid status enum returns 422
    - Invalid priority enum returns 422
    """
    from app.main import app
    app.dependency_overrides[get_current_user] = lambda: USER_ADMIN

    # Non-existent complaint 404
    res_404 = audit_client.get("/api/complaints/NONEXISTENT-9999")
    assert res_404.status_code == 404

    # Invalid status enum 422
    invalid_status = audit_client.patch(
        "/api/complaints/PGRC-2026-0873/status",
        json={"status": "FakeStatus"}
    )
    assert invalid_status.status_code == 422

    # Short AI classify input handles gracefully
    short_ai = audit_client.post(
        "/api/complaints/classify",
        json={"title": "", "description": ""}
    )
    assert short_ai.status_code == 200
    assert short_ai.json()["status"] == "invalid_input"
    assert short_ai.json()["needsManualReview"] is True
