import requests
import sys

BASE_URL = "http://127.0.0.1:5000/api"

def test_registration():
    print("--- Testing Registration ---")
    
    # Test Agent Registration
    phone_agent = "1122334455"
    print(f"1. Registering Agent: {phone_agent}")
    res_agent = requests.post(f"{BASE_URL}/auth/register", json={
        "phone": phone_agent,
        "name": "Test Agent",
        "role": "agent",
        "zone": "Koramangala, BLR",
        "platform": "Food"
    })
    print(f"   Status: {res_agent.status_code}")
    print(f"   Response: {res_agent.json()}")
    
    # Test Manager Registration
    phone_mgr = "5544332211"
    print(f"2. Registering Manager: {phone_mgr}")
    res_mgr = requests.post(f"{BASE_URL}/auth/register", json={
        "phone": phone_mgr,
        "name": "Test Manager",
        "role": "manager"
    })
    print(f"   Status: {res_mgr.status_code}")
    print(f"   Response: {res_mgr.json()}")
    # Test Login & Quote Generation
    print("3. Testing Quote Generation Flow")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": phone_agent,
        "password": "123" # The default is 1234 but let's test just pulling the user's token directly by using correct password
    })
    
    # Wait, the default password is "1234" in app.py's register route.
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": phone_agent,
        "password": "1234"
    })
    
    if login_res.status_code == 200 and 'access_token' in login_res.json():
        token = login_res.json()['access_token']
        print("   Token acquired, requesting quotes...")
        quote_res = requests.post(f"{BASE_URL}/quotes/generate", headers={"Authorization": f"Bearer {token}"})
        print(f"   Quote Status: {quote_res.status_code}")
        print(f"   Quote Response: {quote_res.text[:300]}")
    else:
        print(f"   Login failed: {login_res.status_code} {login_res.text}")
    
    print("--- Testing Complete ---")

if __name__ == "__main__":
    test_registration()
