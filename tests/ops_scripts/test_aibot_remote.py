import urllib.request
import urllib.error
import json

URL = "https://marffet-app.zeabur.app/api/chat"
payload = {
    "message": "What is TSMC?",
    "context": "Test portfolio with TSMC stock",
    "apiKey": "",
    "isPremium": False
}
data = json.dumps(payload).encode('utf-8')

req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"}, method="POST")

print(f"Testing {URL}...")
try:
    with urllib.request.urlopen(req, timeout=60) as response:
        print(f"Status Code: {response.status}")
        print(f"Response: {response.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Response: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Request failed: {e}")
