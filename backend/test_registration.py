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
    
    print("--- Testing Complete ---")

if __name__ == "__main__":
    test_registration()
