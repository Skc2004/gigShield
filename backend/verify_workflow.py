import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_workflow():
    print("--- Starting Verification Workflow ---")
    
    # 1. Register an Agent
    agent_phone = "9988776655"
    print(f"1. Registering Agent: {agent_phone}")
    reg_res = requests.post(f"{BASE_URL}/auth/register", json={
        "phone": agent_phone,
        "name": "Test Agent",
        "role": "agent",
        "zone": "Koramangala, BLR",
        "platform": "Food"
    })
    agent_data = reg_res.json()
    print(f"   Success: {agent_data.get('success')}")
    
    # 2. Check Agent Data (Orders)
    print("2. Fetching Agent Data...")
    data_res = requests.get(f"{BASE_URL}/worker/data?phone={agent_phone}")
    worker_data = data_res.json()
    orders = worker_data.get('orders', [])
    print(f"   Found {len(orders)} seeded orders")
    
    if not orders:
        print("   FAILED: No orders found for agent")
        return

    order_id = orders[0]['id']
    
    # 3. Initiate Claim
    print(f"3. Initiating Claim for Order {order_id}...")
    claim_res = requests.post(f"{BASE_URL}/claims/initiate", json={
        "phone": agent_phone,
        "order_id": order_id
    })
    claim_init = claim_res.json()
    print(f"   Claim Status: {claim_init.get('status')}, ID: {claim_init.get('claim_id')}")
    claim_id = claim_init.get('claim_id')

    # 4. Manager Dashboard
    print("4. Fetching Manager Dashboard...")
    mgr_res = requests.get(f"{BASE_URL}/manager/dashboard")
    mgr_data = mgr_res.json()
    pending = mgr_data.get('metrics', {}).get('pending_claims', 0)
    print(f"   Pending Claims: {pending}")

    # 5. Approve Claim
    print(f"5. Approving Claim {claim_id}...")
    app_res = requests.post(f"{BASE_URL}/manager/claims/update", json={
        "claim_id": claim_id,
        "status": "approved"
    })
    print(f"   Approval Result: {app_res.json().get('success')}")

    # 6. Analytics
    print("6. Fetching Analytics...")
    ana_res = requests.get(f"{BASE_URL}/analytics?role=manager")
    ana_data = ana_res.json()
    print(f"   Analytics Entries: {len(ana_data.get('daily', []))}")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    try:
        test_workflow()
    except Exception as e:
        print(f"ERROR: {e}")
