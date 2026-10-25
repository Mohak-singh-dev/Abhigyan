import httpx
import json

def verify_live():
    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=10.0) as client:
        # 1. Health check
        res_health = client.get("/api/health")
        print(f"GET /api/health -> HTTP {res_health.status_code}")
        print(json.dumps(res_health.json(), indent=2))
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "healthy"
        assert res_health.json()["database"] == "connected"

        # 2. Institutions list
        res_inst = client.get("/api/institutions")
        print(f"\nGET /api/institutions -> HTTP {res_inst.status_code}")
        institutions = res_inst.json()
        print(f"Total seeded institutions returned: {len(institutions)}")
        for inst in institutions:
            print(f"  * {inst['id']} | {inst['name']} (PID: {inst['aicteId']}) | {inst['city']}, {inst['state']} | Type: {inst['type']}")
        assert res_inst.status_code == 200
        assert len(institutions) == 7

        # 3. Individual institution detail
        res_detail = client.get("/api/institutions/i2")
        print(f"\nGET /api/institutions/i2 -> HTTP {res_detail.status_code}")
        detail = res_detail.json()
        print(f"  * Name: {detail['name']}, PID: {detail['aicteId']}, City: {detail['city']}")
        assert res_detail.status_code == 200
        assert detail["id"] == "i2"
        assert detail["name"] == "Bharat College of Engineering"

        # 4. Search filter test
        res_search = client.get("/api/institutions?search=Bharat")
        print(f"\nGET /api/institutions?search=Bharat -> HTTP {res_search.status_code}")
        search_results = res_search.json()
        print(f"  * Found {len(search_results)} match: {[i['name'] for i in search_results]}")
        assert res_search.status_code == 200
        assert len(search_results) == 1
        assert search_results[0]["name"] == "Bharat College of Engineering"

        # 5. State filter test
        res_state = client.get("/api/institutions?state=Maharashtra")
        print(f"\nGET /api/institutions?state=Maharashtra -> HTTP {res_state.status_code}")
        state_results = res_state.json()
        print(f"  * Found {len(state_results)} match: {[i['name'] for i in state_results]}")
        assert res_state.status_code == 200
        assert len(state_results) == 1
        assert state_results[0]["name"] == "Sunrise Institute of Technology"

    print("\nALL LIVE REAL-DATABASE CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    verify_live()
