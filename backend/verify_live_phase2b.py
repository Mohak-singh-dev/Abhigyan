import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.main import app

def verify_live_phase2b():
    print("=" * 70)
    print("LIVE REAL POSTGRESQL VERIFICATION: PHASE 2B WORKFLOWS & TIMELINE")
    print("=" * 70)

    # 1. Inspect live PostgreSQL database schema
    print("\n[Step 1] Inspecting live PostgreSQL database schema...")
    with engine.connect() as conn:
        db_name = conn.execute(text("SELECT current_database()")).scalar()
        print(f"Connected to database: {db_name}")

        # Check complaint_timelines table exists
        cols = conn.execute(text(
            "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'complaint_timelines' ORDER BY ordinal_position"
        )).fetchall()
        print(f"\nLive table 'complaint_timelines' columns ({len(cols)} columns):")
        for col in cols:
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")

        # Check foreign keys on complaint_timelines
        fks = conn.execute(text("""
            SELECT tc.constraint_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name 
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name 
            JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name 
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = 'complaint_timelines'
        """)).fetchall()
        print("\nForeign keys on 'complaint_timelines':")
        for fk in fks:
            print(f"  - {fk[0]}: {fk[1]} -> {fk[2]}.{fk[3]}")

        # Count records
        t_count = conn.execute(text("SELECT count(*) FROM complaint_timelines")).scalar()
        c_count = conn.execute(text("SELECT count(*) FROM complaints")).scalar()
        print(f"\nLive row counts: {t_count} timeline events across {c_count} complaints.")

    # 2. Test live API endpoints with real database (NO dependency overrides)
    print("\n[Step 2] Testing Phase 2B API endpoints against real PostgreSQL...")
    client = TestClient(app)

    # A. GET /api/complaints/{id}/timeline on existing seeded complaint
    print("\n[Test 2A] Calling GET /api/complaints/PGRC-2026-0873/timeline...")
    res_tl = client.get("/api/complaints/PGRC-2026-0873/timeline")
    assert res_tl.status_code == 200, f"Expected 200, got {res_tl.status_code}: {res_tl.text}"
    events = res_tl.json()
    print(f"Status: {res_tl.status_code}")
    print(f"Returned {len(events)} chronological timeline events:")
    for ev in events:
        print(f"  - [Event #{ev['id']} | {ev['date']}] {ev['label']} (by {ev['by']})")
    assert len(events) >= 2
    # Verify chronological ordering
    for i in range(len(events) - 1):
        assert events[i]["id"] < events[i + 1]["id"], "Timeline events must be in strictly ascending chronological order by ID"
    print("Chronological timeline ordering verified.")

    # B. POST /api/complaints: Create test grievance & check automatic initial timeline creation
    test_case_id = "PGRC-2026-8877"
    print(f"\n[Test 2B] Calling POST /api/complaints to create test grievance '{test_case_id}'...")
    # Clean up previous run if needed
    with SessionLocal() as db:
        db.execute(text("DELETE FROM complaints WHERE id = :id"), {"id": test_case_id})
        db.commit()

    payload_create = {
        "id": test_case_id,
        "institutionId": "i1",
        "bureau": "PGRC",
        "category": "Admission Irregularity",
        "priority": "High",
        "title": "Phase 2B Live Verification Grievance",
        "description": "Verifying status history transitions, assignment and timeline in real PostgreSQL.",
        "complainantType": "Student",
        "complainantName": "Aman Verma",
        "complainantEmail": "aman.verma@student.edu.in",
    }
    res_create = client.post("/api/complaints", json=payload_create)
    assert res_create.status_code == 201
    created_c = res_create.json()
    print(f"Created: {created_c['id']} in status '{created_c['status']}' assigned to '{created_c['officer']}'.")
    assert len(created_c["timeline"]) == 2, f"Expected 2 initial timeline events, got {len(created_c['timeline'])}"
    print(f"Initial timeline automatically created: {created_c['timeline'][0]['label']} & {created_c['timeline'][1]['label']}")

    # C. PATCH /api/complaints/{id}/status: Transition Pending -> In Progress
    print(f"\n[Test 2C] Calling PATCH /api/complaints/{test_case_id}/status (Pending -> In Progress)...")
    payload_status_1 = {
        "status": "In Progress",
        "remarks": "Investigation notice issued to the principal.",
        "by": "Rajesh Kumar",
        "role": "Officer",
        "note": "Formal counter-affidavit requested within 7 working days."
    }
    res_s1 = client.patch(f"/api/complaints/{test_case_id}/status", json=payload_status_1)
    assert res_s1.status_code == 200, f"Expected 200, got {res_s1.status_code}: {res_s1.text}"
    c_s1 = res_s1.json()
    assert c_s1["status"] == "In Progress"
    assert c_s1["remarks"] == payload_status_1["remarks"]
    assert len(c_s1["timeline"]) == 3
    print(f"Status updated to: {c_s1['status']}")
    print(f"New timeline event appended: '{c_s1['timeline'][-1]['label']}' (note: {c_s1['timeline'][-1]['note']})")

    # D. PATCH /api/complaints/{id}/status: Transition In Progress -> Resolved
    print(f"\n[Test 2D] Calling PATCH /api/complaints/{test_case_id}/status (In Progress -> Resolved)...")
    payload_status_2 = {
        "status": "Resolved",
        "remarks": "Institution complied fully. Excess fee adjusted and report archived.",
        "by": "Rajesh Kumar",
        "role": "Officer"
    }
    res_s2 = client.patch(f"/api/complaints/{test_case_id}/status", json=payload_status_2)
    assert res_s2.status_code == 200
    c_s2 = res_s2.json()
    assert c_s2["status"] == "Resolved"
    assert len(c_s2["timeline"]) == 4
    print(f"Status updated to: {c_s2['status']}")
    print(f"Resolution event: '{c_s2['timeline'][-1]['label']}'")

    # E. PATCH /api/complaints/{id}/status: Attempt invalid transition from Resolved
    print(f"\n[Test 2E] Testing invalid transition from 'Resolved' status...")
    res_s_invalid = client.patch(f"/api/complaints/{test_case_id}/status", json={"status": "In Progress"})
    assert res_s_invalid.status_code == 400
    print(f"Expected 400 caught: {res_s_invalid.json()['detail']}")

    # F. PATCH /api/complaints/{id}/assign: Reassign complaint to another officer & bureau
    print(f"\n[Test 2F] Calling PATCH /api/complaints/{test_case_id}/assign (reassign to Anita Verma, RB)...")
    payload_assign = {
        "userId": "u3",
        "reason": "Regulatory inquiry requires joint jurisdiction by Regulation Bureau."
    }
    res_assign = client.patch(f"/api/complaints/{test_case_id}/assign", json=payload_assign)
    assert res_assign.status_code == 200, f"Expected 200, got {res_assign.status_code}: {res_assign.text}"
    c_assigned = res_assign.json()
    assert c_assigned["officer"] == "Anita Verma"
    assert c_assigned["assignedUserId"] == "u3"
    assert c_assigned["bureau"] == "RB"
    assert len(c_assigned["timeline"]) == 5
    print(f"Assigned to: {c_assigned['officer']} (bureau: {c_assigned['bureau']}, user_id: {c_assigned['assignedUserId']})")
    print(f"Assignment timeline event: '{c_assigned['timeline'][-1]['label']}'")
    print(f"Justification note: '{c_assigned['timeline'][-1]['note']}'")

    # G. PATCH /api/complaints/{id}/assign: Attempt invalid user
    print("\n[Test 2G] Testing assignment to invalid user ID...")
    res_bad_user = client.patch(f"/api/complaints/{test_case_id}/assign", json={"userId": "nonexistent_u"})
    assert res_bad_user.status_code == 400
    print(f"Expected 400 caught: {res_bad_user.json()['detail']}")

    # H. GET /api/complaints/{id}/timeline: Verify all events in PostgreSQL
    print(f"\n[Test 2H] Querying full chronological timeline for '{test_case_id}'...")
    res_final_tl = client.get(f"/api/complaints/{test_case_id}/timeline")
    assert res_final_tl.status_code == 200
    final_events = res_final_tl.json()
    assert len(final_events) == 5
    print(f"Verified {len(final_events)} events in PostgreSQL database:")
    for idx, ev in enumerate(final_events, 1):
        print(f"  {idx}. [ID {ev['id']}] {ev['label']} | Actor: {ev['by']} ({ev['role']})")

    # Cleanup test record
    with SessionLocal() as db:
        db.execute(text("DELETE FROM complaints WHERE id = :id"), {"id": test_case_id})
        db.commit()
    print(f"\n[Cleanup] Successfully removed temporary test record '{test_case_id}' and all associated timeline events.")

    print("\n" + "=" * 70)
    print("ALL REAL POSTGRESQL VERIFICATION CHECKS FOR PHASE 2B PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    verify_live_phase2b()
