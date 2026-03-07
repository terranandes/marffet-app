import urllib.request
import time

url = "https://accounts.google.com/.well-known/openid-configuration"
print(f"Testing fetch to {url}...")
start = time.time()
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=5) as response:
        print(f"Status: {response.status}")
        print(f"Time: {time.time() - start:.2f}s")
        data = response.read().decode('utf-8')
        print(f"Data snippet: {data[:100]}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Time: {time.time() - start:.2f}s")
