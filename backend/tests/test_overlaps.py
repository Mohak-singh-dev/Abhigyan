"""
Backend unit & integration tests for Phase 2: Cross-Bureau Overlap Confirmation.
Tests coverage:
- Authorized confirmation persists relationship & justification
- Both complaint timelines contain the cross-reference
- Both complaints remain independent dockets (no status/bureau/officer mutation)
- Reloading/switching accounts retrieves persisted relationship
- Linked dockets endpoint returns bidirectional links
- Unauthorized confirmation rejected (Officer -> 403, Complainant -> 403)
- Bureau Admin out-of-jurisdiction rejected (403)
- Missing complaint rejected (404)
- Identical complaint IDs rejected (400)
- Duplicate active confirmation rejected (409)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import get_current_user
from app.models.user import User

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
    role="Admin",
    bureau="RB",
    status="Active",
)

APPROVAL_BUREAU_ADMIN = User(
    id="u5",
    name="Suresh Patel",
    email="suresh.patel@aicte-india.org",
    role="Admin",
    bureau="Approval",
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
    bureau="PGRC",
    status="Active",
)


def test_list_overlaps_authorized(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN
    res = client.get("/api/overlaps")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    item = data[0]
    assert "id" in item
    assert "complaint_a_id" in item
    assert "complaint_b_id" in item
    assert "similarity" in item
    assert "status" in item


def test_get_overlap_by_id_found(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN
    res = client.get("/api/overlaps")
    assert res.status_code == 200
    overlaps = res.json()
    first_id = overlaps[0]["id"]

    res_single = client.get(f"/api/overlaps/{first_id}")
    assert res_single.status_code == 200
    single = res_single.json()
    assert single["id"] == first_id


def test_get_overlap_by_id_not_found(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN
    res = client.get("/api/overlaps/non-existent-overlap-id")
    assert res.status_code == 404


def test_create_overlap_identical_cases_rejected(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN
    payload = {
        "complaint_a_id": "PGRC-2026-9238",
        "complaint_b_id": "PGRC-2026-9238",
        "similarity": 90,
        "reasons": ["Identical complaints test"],
    }
    res = client.post("/api/overlaps", json=payload)
    assert res.status_code == 400
    detail = res.json()["detail"].lower()
    assert "itself" in detail or "distinct" in detail


def test_create_overlap_missing_case_rejected(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN
    payload = {
        "complaint_a_id": "PGRC-2026-9238",
        "complaint_b_id": "NON-EXISTENT-CASE-9999",
        "similarity": 85,
        "reasons": ["Test missing case"],
    }
    res = client.post("/api/overlaps", json=payload)
    assert res.status_code == 404


def test_create_and_confirm_overlap_persists_relationship_and_timelines(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN

    # Fetch two distinct existing complaints
    comp_res = client.get("/api/complaints")
    assert comp_res.status_code == 200
    comp_body = comp_res.json()
    all_comps = comp_body.get("items", comp_body if isinstance(comp_body, list) else [])
    assert len(all_comps) >= 2
    comp_a = all_comps[0]
    comp_b = all_comps[1]

    # Create an overlap candidate between them
    create_payload = {
        "complaint_a_id": comp_a["id"],
        "complaint_b_id": comp_b["id"],
        "similarity": 88,
        "reasons": ["Shared fee circular", "Similar dates"],
    }
    create_res = client.post("/api/overlaps", json=create_payload)
    assert create_res.status_code in (200, 201)
    overlap = create_res.json()
    overlap_id = overlap["id"]

    # First reset to open if it was already linked from previous runs
    client.patch(f"/api/overlaps/{overlap_id}/decision", json={"state": "open", "justification": "Resetting for test"})

    justification_text = "Cross-verified fee circular between both institutions; coordinating notice."
    decision_payload = {
        "state": "linked",
        "justification": justification_text,
    }
    dec_res = client.patch(f"/api/overlaps/{overlap_id}/decision", json=decision_payload)
    assert dec_res.status_code == 200
    updated = dec_res.json()
    assert updated["status"] == "linked"
    assert updated["decision_state"] == "linked"
    assert updated["justification"] == justification_text
    assert updated["reviewed_by"] is not None

    # Check Complaint A timeline contains coordination event referencing Complaint B
    comp_a_res = client.get(f"/api/complaints/{comp_a['id']}")
    assert comp_a_res.status_code == 200
    comp_a_data = comp_a_res.json()
    timeline_a = comp_a_data.get("timeline", [])
    matching_events_a = [
        ev for ev in timeline_a
        if comp_b["id"] in (ev.get("label") or "") or comp_b["id"] in (ev.get("note") or "")
    ]
    assert len(matching_events_a) >= 1
    assert justification_text in (matching_events_a[0].get("note") or "")

    # Check Complaint B timeline contains coordination event referencing Complaint A
    comp_b_res = client.get(f"/api/complaints/{comp_b['id']}")
    assert comp_b_res.status_code == 200
    comp_b_data = comp_b_res.json()
    timeline_b = comp_b_data.get("timeline", [])
    matching_events_b = [
        ev for ev in timeline_b
        if comp_a["id"] in (ev.get("label") or "") or comp_a["id"] in (ev.get("note") or "")
    ]
    assert len(matching_events_b) >= 1
    assert justification_text in (matching_events_b[0].get("note") or "")

    # Confirm complaints remain independent dockets (status, bureau unchanged)
    assert comp_a_data["status"] == comp_a["status"]
    assert comp_a_data["bureau"] == comp_a["bureau"]
    assert comp_b_data["status"] == comp_b["status"]
    assert comp_b_data["bureau"] == comp_b["bureau"]

    # Check linked dockets endpoint
    linked_res_a = client.get(f"/api/overlaps/linked/{comp_a['id']}")
    assert linked_res_a.status_code == 200
    linked_a = linked_res_a.json()
    assert any(ld["case_id"] == comp_b["id"] for ld in linked_a)

    linked_res_b = client.get(f"/api/overlaps/linked/{comp_b['id']}")
    assert linked_res_b.status_code == 200
    linked_b = linked_res_b.json()
    assert any(ld["case_id"] == comp_a["id"] for ld in linked_b)


def test_duplicate_active_confirmation_rejected(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN

    # Find an already confirmed overlap
    res = client.get("/api/overlaps?status=linked")
    assert res.status_code == 200
    linked_overlaps = res.json()
    if not linked_overlaps:
        pytest.skip("No linked overlap found to test duplicate confirmation")

    overlap = linked_overlaps[0]
    payload = {
        "state": "linked",
        "justification": "Attempting redundant active confirmation",
    }
    dup_res = client.patch(f"/api/overlaps/{overlap['id']}/decision", json=payload)
    assert dup_res.status_code == 409
    assert "already active" in dup_res.json()["detail"].lower()


def test_officer_cannot_confirm_overlap(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN
    res = client.get("/api/overlaps")
    assert res.status_code == 200
    overlaps = res.json()
    assert len(overlaps) >= 1
    overlap_id = overlaps[0]["id"]

    # Switch to Officer
    app.dependency_overrides[get_current_user] = lambda: OFFICER_USER
    payload = {
        "state": "linked",
        "justification": "Officer trying to confirm overlap",
    }
    dec_res = client.patch(f"/api/overlaps/{overlap_id}/decision", json=payload)
    assert dec_res.status_code == 403


def test_complainant_cannot_confirm_overlap(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN
    res = client.get("/api/overlaps")
    assert res.status_code == 200
    overlaps = res.json()
    assert len(overlaps) >= 1
    overlap_id = overlaps[0]["id"]

    # Switch to Complainant
    app.dependency_overrides[get_current_user] = lambda: COMPLAINANT_USER
    payload = {
        "state": "linked",
        "justification": "Complainant trying to confirm overlap",
    }
    dec_res = client.patch(f"/api/overlaps/{overlap_id}/decision", json=payload)
    assert dec_res.status_code == 403


def test_bureau_admin_jurisdiction_enforced(client: TestClient):
    # Find an overlap where neither complaint belongs to Approval Bureau
    app.dependency_overrides[get_current_user] = lambda: SYSTEM_ADMIN
    res = client.get("/api/overlaps")
    assert res.status_code == 200
    overlaps = res.json()

    target_overlap = None
    for o in overlaps:
        comp_a_res = client.get(f"/api/complaints/{o['complaint_a_id']}")
        comp_b_res = client.get(f"/api/complaints/{o['complaint_b_id']}")
        if comp_a_res.status_code == 200 and comp_b_res.status_code == 200:
            bureau_a = comp_a_res.json().get("bureau")
            bureau_b = comp_b_res.json().get("bureau")
            if bureau_a != "Approval" and bureau_b != "Approval":
                target_overlap = o
                break

    if not target_overlap:
        pytest.skip("Could not find an overlap outside Approval bureau to test jurisdiction")

    # Switch to Approval Bureau Admin
    app.dependency_overrides[get_current_user] = lambda: APPROVAL_BUREAU_ADMIN
    payload = {
        "state": "dismissed",
        "justification": "Approval admin acting out of jurisdiction",
    }
    res_dec = client.patch(f"/api/overlaps/{target_overlap['id']}/decision", json=payload)
    assert res_dec.status_code == 403
    assert "jurisdiction" in res_dec.json()["detail"].lower()
