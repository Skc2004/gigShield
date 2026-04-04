import requests

BASE_URL = "http://127.0.0.1:5000/api"

print("Registering bug tester...")
res = requests.post(f"{BASE_URL}/auth/register", json={
    "phone": "9998887776", "name": "Bug Tester", "role": "agent", "zone": "Koramangala, BLR", "platform": "Food", "password": "123"
})
auth = res.json()
print("Register:", auth)

if 'access_token' in auth:
    tok = auth['access_token']
    print(f"Token acquired. Requesting quotes...")
    res2 = requests.post(f"{BASE_URL}/quotes/generate", headers={"Authorization": f"Bearer {tok}"})
    print("Quotes Code:", res2.status_code)
    print("Quotes Output:", res2.text[:1000])
else:
    print("No token, checking login explicitly...")
    login = requests.post(f"{BASE_URL}/auth/login", json={"phone": "9998887776", "password": "123"})
    print("Login:", login.json())
    if 'access_token' in login.json():
        tok = login.json()['access_token']
        res2 = requests.post(f"{BASE_URL}/quotes/generate", headers={"Authorization": f"Bearer {tok}"})
        print("Quotes Code:", res2.status_code)
        print("Quotes Output:", res2.text[:1000])
