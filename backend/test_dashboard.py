import requests

BASE_URL = "http://127.0.0.1:5000/api"

def test_manager_dashboard():
    print("Logging in as manager...")
    # Seed manager account
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "9999999999", "password": "admin123"
    })
    
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
        
    token = login_res.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Fetching manager dashboard data...")
    dash_res = requests.get(f"{BASE_URL}/manager/dashboard", headers=headers)
    
    if dash_res.status_code == 200:
        data = dash_res.json()
        claims = data.get('claims', [])
        print(f"Found {len(claims)} claims.")
        
        for c in claims:
            print(f"Claim ID: {c['id']}, Agent: {c['agent_name']}, Phone: {c.get('phone')}, Order: {c.get('order_id')}")
            if 'phone' not in c:
                print("FE Error: 'phone' field is missing from claim object!")
    else:
        print(f"Failed to fetch dashboard: {dash_res.status_code}")
        print(dash_res.text)

if __name__ == "__main__":
    test_manager_dashboard()
