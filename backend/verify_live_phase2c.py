import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.database import engine, SessionLocal
from app.models.user import User
from app.models.complaint import Complaint
from app.models.timeline import ComplaintTimeline
from app.config import settings

def run_live_verification():
    print("=" * 70)
    print("ABHIGYAN PHASE 2C: LIVE POSTGRESQL & RBAC VERIFICATION")
    print("=" * 70)

    # 1. Database connection and schema verification
    print("[1/8] Verifying PostgreSQL 18 connection and password_hash schema...")
    with engine.connect() as conn:
        res = conn.execute(text("SELECT current_database(), current_user, version();"))
        row = res.fetchone()
        db_name, db_user, version = row[0], row[1], row[2]
        print(f"      Database: {db_name} | User: {db_user}")
        print(f"      PostgreSQL Version: {version.split(',')[0]}")

        col_check = conn.execute(text(
            "SELECT column_name, data_type, is_nullable "
            "FROM information_schema.columns "
            "WHERE table_name = 'users' AND column_name = 'password_hash';"
        )).fetchone()
        if not col_check:
            raise RuntimeError("FAILED: Column password_hash not found in users table!")
        print(f"      Found column: {col_check[0]} ({col_check[1]}, nullable={col_check[2]})")

    client = TestClient(app)

    # 2. Standard Login Verification
    print("\n[2/8] Verifying Standard Credentials Authentication (POST /api/auth/login)...")
    admin_login_res = client.post("/api/auth/login", json={
        "email": "member-sec@aicte-india.org",
        "password": settings.DEFAULT_SEED_PASSWORD
    })
    assert admin_login_res.status_code == 200, f"Admin login failed: {admin_login_res.text}"
    admin_data = admin_login_res.json()
    admin_token = admin_data["accessToken"]
    print(f"      Admin Login: SUCCESS (Role: {admin_data['user']['role']}, Token length: {len(admin_token)})")

    invalid_login_res = client.post("/api/auth/login", json={
        "email": "member-sec@aicte-india.org",
        "password": "IncorrectPassword999!"
    })
    assert invalid_login_res.status_code == 401, f"Expected 401 for bad password, got {invalid_login_res.status_code}"
    print("      Invalid Password Rejection: SUCCESS (401 Unauthorized)")

    # 3. Development Demo Login Verification
    print("\n[3/8] Verifying Development Demo-Login (POST /api/auth/demo-login)...")
    complainant_demo = client.post("/api/auth/demo-login", json={"userId": "u0"})
    assert complainant_demo.status_code == 200, f"Demo login u0 failed: {complainant_demo.text}"
    complainant_data = complainant_demo.json()
    complainant_token = complainant_data["accessToken"]
    print(f"      Complainant Demo Login: SUCCESS (User: {complainant_data['user']['name']}, Role: {complainant_data['user']['role']})")

    bureau_admin_demo = client.post("/api/auth/demo-login", json={"userId": "u1b"})
    assert bureau_admin_demo.status_code == 200
    bureau_admin_data = bureau_admin_demo.json()
    bureau_admin_token = bureau_admin_data["accessToken"]
    print(f"      Bureau Admin Demo Login: SUCCESS (User: {bureau_admin_data['user']['name']}, Bureau: {bureau_admin_data['user']['bureau']})")

    officer_demo = client.post("/api/auth/demo-login", json={"userId": "u2"})
    assert officer_demo.status_code == 200
    officer_data = officer_demo.json()
    officer_token = officer_data["accessToken"]
    print(f"      Officer Demo Login: SUCCESS (User: {officer_data['user']['name']}, Bureau: {officer_data['user']['bureau']})")

    # 4. Identity Profile Verification
    print("\n[4/8] Verifying Authenticated Profile (GET /api/auth/me)...")
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {officer_token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    print(f"      Verified: {me_data['name']} ({me_data['designation']}) | Active Cases: {me_data['activeCasesCount']}")

    # 5. Complainant RBAC Boundary Verification
    print("\n[5/8] Verifying Complainant Authorization Boundaries...")
    complainant_headers = {"Authorization": f"Bearer {complainant_token}"}

    # List scoping
    list_res = client.get("/api/complaints", headers=complainant_headers)
    assert list_res.status_code == 200
    list_items = list_res.json()["items"]
    for item in list_items:
        assert item["complainantEmail"] == "rohit.sharma@student.edu.in" or item["complainantName"] == "Rohit Sharma", (
            f"Cross-complainant leakage: found {item['id']} for {item.get('complainantEmail')}"
        )
    print(f"      Complainant Query Scoping: SUCCESS (Filtered to {len(list_items)} personal grievances)")

    # Cross-complainant access block
    cross_view = client.get("/api/complaints/RB-2026-0141", headers=complainant_headers)
    assert cross_view.status_code == 403, f"Expected 403 for cross-complainant access, got {cross_view.status_code}"
    print(f"      Complainant Cross-Docket Block: SUCCESS (403 Forbidden: {cross_view.json()['detail']})")

    # Status modification block
    status_block = client.patch(f"/api/complaints/{list_items[0]['id']}/status", json={"status": "Resolved"}, headers=complainant_headers)
    assert status_block.status_code == 403
    print(f"      Complainant Status Update Block: SUCCESS (403 Forbidden: {status_block.json()['detail']})")

    # Assignment block
    assign_block = client.patch(f"/api/complaints/{list_items[0]['id']}/assign", json={"officer": "Rajesh Kumar"}, headers=complainant_headers)
    assert assign_block.status_code == 403
    print(f"      Complainant Case Assignment Block: SUCCESS (403 Forbidden: {assign_block.json()['detail']})")

    # 6. Bureau Admin Jurisdiction Verification
    print("\n[6/8] Verifying Bureau Admin Jurisdiction & Cross-Bureau Restrictions...")
    bureau_admin_headers = {"Authorization": f"Bearer {bureau_admin_token}"}

    # Cross-bureau status update block (Dr. Priya Nair is PGRC, trying to update RB complaint)
    cross_status = client.patch("/api/complaints/RB-2026-0141/status", json={"status": "In Progress"}, headers=bureau_admin_headers)
    assert cross_status.status_code == 403
    print(f"      Bureau Admin Cross-Bureau Status Block: SUCCESS (403 Forbidden: {cross_status.json()['detail']})")

    # Cross-bureau assignment block
    cross_assign = client.patch("/api/complaints/RB-2026-0141/assign", json={"officer": "Rajesh Kumar"}, headers=bureau_admin_headers)
    assert cross_assign.status_code == 403
    print(f"      Bureau Admin Cross-Bureau Assign Block: SUCCESS (403 Forbidden: {cross_assign.json()['detail']})")

    # 7. Officer Permissions & Restrictions
    print("\n[7/8] Verifying Handling Officer Permissions & Reassignment Restrictions...")
    officer_headers = {"Authorization": f"Bearer {officer_token}"}

    # Officer cannot assign/reassign cases
    officer_assign = client.patch("/api/complaints/PGRC-2026-0873/assign", json={"officer": "Anita Verma"}, headers=officer_headers)
    assert officer_assign.status_code == 403
    print(f"      Officer Direct Reassignment Block: SUCCESS (403 Forbidden: {officer_assign.json()['detail']})")

    # Officer cannot update case outside their bureau
    officer_cross = client.patch("/api/complaints/RB-2026-0141/status", json={"status": "In Progress"}, headers=officer_headers)
    assert officer_cross.status_code == 403
    print(f"      Officer Cross-Bureau Status Block: SUCCESS (403 Forbidden: {officer_cross.json()['detail']})")

    # 8. Timeline Actor Integrity on Real PostgreSQL Database
    print("\n[8/8] Verifying Timeline Audit Actor Integrity (Anti-Spoofing Check)...")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    test_case_id = "PGRC-2026-9998"
    # Ensure cleanup before creating
    db = SessionLocal()
    try:
        db.query(ComplaintTimeline).filter(ComplaintTimeline.complaint_id == test_case_id).delete()
        db.query(Complaint).filter(Complaint.id == test_case_id).delete()
        db.commit()

        # Create temporary case using Admin
        create_res = client.post("/api/complaints", json={
            "id": test_case_id,
            "institutionId": "i1",
            "bureau": "PGRC",
            "category": "Fee Regulation",
            "priority": "High",
            "officer": "Rajesh Kumar",
            "status": "Pending",
            "title": "Temporary Test Docket for Timeline Integrity Audit",
            "description": "Verifying that timeline audit attribution cannot be spoofed by client payload.",
            "complainantType": "Student",
            "complainantName": "Rohit Sharma",
            "complainantEmail": "rohit.sharma@student.edu.in",
        }, headers=admin_headers)
        assert create_res.status_code == 201, f"Failed creating test docket: {create_res.text}"

        # Status update executed by Officer Rajesh Kumar with spoofed actor in payload
        spoofed_payload = {
            "status": "In Progress",
            "by": "Member Secretary Dr. Mehta",
            "role": "Admin",
            "userId": "u1",
            "remarks": "Preliminary scrutiny completed.",
            "note": "Notice issued."
        }
        status_res = client.patch(f"/api/complaints/{test_case_id}/status", json=spoofed_payload, headers=officer_headers)
        assert status_res.status_code == 200, f"Status update failed: {status_res.text}"

        # Fetch timeline and check recorded actor
        timeline_res = client.get(f"/api/complaints/{test_case_id}/timeline", headers=officer_headers)
        assert timeline_res.status_code == 200
        events = timeline_res.json()
        status_event = [e for e in events if "In Progress" in e["label"]][0]

        print(f"      Spoofed Request Sent: by='Member Secretary Dr. Mehta', role='Admin', userId='u1'")
        print(f"      Actual Event Recorded in DB: by='{status_event['by']}', role='{status_event['role']}', userId='{status_event['userId']}'")

        assert status_event["userId"] == "u2", "FAILED: timeline actor userId was spoofed!"
        assert status_event["by"] == "Rajesh Kumar", "FAILED: timeline actor name was spoofed!"
        assert status_event["role"] == "Officer", "FAILED: timeline actor role was spoofed!"
        print("      Timeline Actor Integrity: VERIFIED (Client payload spoofing prevented!)")

    finally:
        # Cleanup temporary test case
        db.query(ComplaintTimeline).filter(ComplaintTimeline.complaint_id == test_case_id).delete()
        db.query(Complaint).filter(Complaint.id == test_case_id).delete()
        db.commit()
        db.close()
        print("      Temporary audit records cleaned up safely.")

    print("\n" + "=" * 70)
    print("ALL LIVE POSTGRESQL & RBAC VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_live_verification()
