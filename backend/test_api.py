import urllib.request
import json
import sys

try:
    print("Testing Login...")
    req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=json.dumps({'username': 'employee1', 'password': 'password123', 'role': 'employee'}).encode('utf-8'), headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    print("Login Response:", data)
    token = data['access_token']
    
    print("\nTesting Checkin...")
    req2 = urllib.request.Request('http://127.0.0.1:5000/api/attendance/checkin', data=json.dumps({'source': 'web'}).encode('utf-8'), headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token})
    res2 = urllib.request.urlopen(req2)
    print("Checkin Response:", res2.read().decode('utf-8'))
    
    print("\nTesting Apply Leave...")
    req3 = urllib.request.Request('http://127.0.0.1:5000/api/leaves/', data=json.dumps({'leave_type_id': 1, 'from_date': '2026-06-10', 'to_date': '2026-06-11', 'reason': 'test'}).encode('utf-8'), headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token})
    res3 = urllib.request.urlopen(req3)
    print("Leave Response:", res3.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
