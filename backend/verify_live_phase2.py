import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.main import app

def verify_live():
    print("=" * 70)
    print("LIVE REAL POSTGRESQL VERIFICATION: PHASE 2A COMPLAINTS API")
    print("=" * 70)

    # 1. Verify PostgreSQL Database & Tables
    print("\n[Step 1] Inspecting live PostgreSQL database schema...")
    with engine.connect() as conn:
        db_name = conn.execute(text("SELECT current_database()")).scalar()
        db_version = conn.execute(text("SELECT version()")).scalar()
        print(f"Connected to database: {db_name}")
        print(f"PostgreSQL version: {db_version.split(',')[0]}")

        # Check complaints table exists
        result = conn.execute(text(
            "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'complaints' ORDER BY ordinal_position"
        )).fetchall()
        print(f"\nLive table 'complaints' columns ({len(result)} columns):")
        for col in result:
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")

        # Check foreign keys
        fks = conn.execute(text("""
            SELECT tc.constraint_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name 
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name 
            JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name 
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = 'complaints'
        """)).fetchall()
        print("\nForeign keys on 'complaints':")
        for fk in fks:
            print(f"  - {fk[0]}: {fk[1]} -> {fk[2]}.{fk[3]}")

        # Check seeded rows count
        complaint_count = conn.execute(text("SELECT count(*) FROM complaints")).scalar()
        inst_count = conn.execute(text("SELECT count(*) FROM institutions")).scalar()
        user_count = conn.execute(text("SELECT count(*) FROM users")).scalar()
        print(f"\nLive row counts: {complaint_count} complaints, {inst_count} institutions, {user_count} users")

    # 2. Test live API endpoints with real database (NO dependency overrides)
    print("\n[Step 2] Testing live API endpoints against real PostgreSQL...")
    client = TestClient(app)

    # A. GET /api/complaints (List & Pagination)
    print("\n[Test 2A] Calling GET /api/complaints?page=1&pageSize=5...")
    res = client.get("/api/complaints?page=1&pageSize=5")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    print(f"Status: {res.status_code}")
    print(f"Pagination: total={data['total']}, page={data['page']}, pageSize={data['pageSize']}, totalPages={data['totalPages']}")
    print(f"Returned {len(data['items'])} items. First item: {data['items'][0]['id']} - {data['items'][0]['title'][:40]}...")

    # B. GET /api/complaints with filter (Bureau=PGRC)
    print("\n[Test 2B] Calling GET /api/complaints?bureau=PGRC...")
    res_bureau = client.get("/api/complaints?bureau=PGRC")
    assert res_bureau.status_code == 200
    pgrc_data = res_bureau.json()
    print(f"Status: {res_bureau.status_code}")
    print(f"PGRC Complaints count: {pgrc_data['total']}")
    assert all(item["bureau"] == "PGRC" for item in pgrc_data["items"]), "All items must belong to PGRC"
    print("All filtered items verified to have bureau == 'PGRC'")

    # C. GET /api/complaints with search
    print("\n[Test 2C] Calling GET /api/complaints?search=fire...")
    res_search = client.get("/api/complaints?search=fire")
    assert res_search.status_code == 200
    search_data = res_search.json()
    print(f"Status: {res_search.status_code}, Found: {search_data['total']}")
    assert search_data['total'] >= 1
    print(f"Search match: {search_data['items'][0]['id']} - {search_data['items'][0]['title']}")

    # D. POST /api/complaints (Create new complaint against live DB)
    print("\n[Test 2D] Calling POST /api/complaints (creating real complaint in DB)...")
    live_case_id = "PGRC-2026-9988"
    new_case_payload = {
        "id": live_case_id,
        "institutionId": "i1",
        "bureau": "PGRC",
        "category": "Admission Irregularity",
        "priority": "Critical",
        "title": "Live Database Integration Verification Grievance",
        "description": "Verifying real end-to-end transaction persistence in PostgreSQL 18 abhigyan_db.",
        "complainantType": "Whistleblower",
        "complainantName": "Integration Tester",
        "complainantEmail": "tester@aicte-india.org"
    }
    # Clean up if existing from previous run
    with SessionLocal() as db:
        db.execute(text("DELETE FROM complaints WHERE id = :id"), {"id": live_case_id})
        db.commit()

    res_create = client.post("/api/complaints", json=new_case_payload)
    assert res_create.status_code == 201, f"Expected 201, got {res_create.status_code}: {res_create.text}"
    created_case = res_create.json()
    print(f"Status: {res_create.status_code} Created")
    print(f"Created Case ID: {created_case['id']}")
    print(f"Assigned Officer: {created_case['officer']}")
    print(f"Assigned User ID: {created_case['assignedUserId']}")
    print(f"SLA Due Date: {created_case['due']}")
    print(f"Institution Permanent ID: {created_case['institutionPermanentId']}")
    print(f"Institution Name: {created_case['institutionName']}")

    # E. GET /api/complaints/{id} (Case-insensitive lookup)
    print(f"\n[Test 2E] Calling GET /api/complaints/{live_case_id.lower()} (case-insensitive lookup)...")
    res_lookup = client.get(f"/api/complaints/{live_case_id.lower()}")
    assert res_lookup.status_code == 200
    lookup_case = res_lookup.json()
    assert lookup_case["id"] == live_case_id
    assert lookup_case["institutionId"] == "i1"
    print(f"Lookup verified: {lookup_case['id']} - {lookup_case['title']}")

    # F. GET /api/complaints/{id} (404 Not Found)
    print("\n[Test 2F] Calling GET /api/complaints/NONEXISTENT-9999 (expecting 404)...")
    res_404 = client.get("/api/complaints/NONEXISTENT-9999")
    assert res_404.status_code == 404
    print(f"Status: {res_404.status_code} Not Found, Detail: {res_404.json()['detail']}")

    # Clean up test record to preserve pristine demo database
    with SessionLocal() as db:
        db.execute(text("DELETE FROM complaints WHERE id = :id"), {"id": live_case_id})
        db.commit()
    print(f"\n[Cleanup] Successfully removed temporary verification record '{live_case_id}' from live database.")

    print("\n" + "=" * 70)
    print("ALL REAL POSTGRESQL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    verify_live()
