import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://78.46.147.244:8890"
PREFIXES = ["/", "/api/", "/api/v1/", "/api/v1/public/", "/api/v1/internal/"]


def req(path: str, method: str = "GET"):
    url = BASE + path
    data = None
    headers = {}
    if method == "POST":
        data = b'{"url":"http://example.com"}'
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url=url, method=method, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=5) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None


words = []
for line in Path("common.txt").read_text(encoding="utf-8", errors="ignore").splitlines():
    w = line.strip()
    if not w or w.startswith("#"):
        continue
    words.append(w)
words = words[:1200]

hits = set()
for w in words:
    for pfx in PREFIXES:
        p = (pfx + w).replace("//", "/")
        s = req(p, "GET")
        if s is not None and s != 404:
            hits.add((s, "GET", p))

        s = req(p, "POST")
        if s is not None and s not in (404, 405):
            hits.add((s, "POST", p))

for p in ["/api/v1/internal", "/api/v1/internal/debug", "/api/v1/public/stats"]:
    for m in ("GET", "POST"):
        s = req(p, m)
        if s is None:
            continue
        if s == 404:
            continue
        if m == "POST" and s == 405:
            continue
        hits.add((s, m, p))

items = sorted(hits, key=lambda x: (x[2], x[1], x[0]))
print("HIT_COUNT", len(items))
for status, method, path in items:
    print(f"{status}\t{method}\t{path}")
