# Atomic Shared Decryption - Writeup

## Challenge Info
- Name: Atomic Shared Decryption
- URL: http://78.46.147.244:8893/
- Provided creds:
  - admin@apexcache.io
  - ApexAdmin123!@#

## Objective
Retrieve the flag by abusing the cache/signature behavior implied by the challenge narrative.

## Recon
1. Opened the landing page and inspected source.
2. Found login form posting to /login.
3. Logged in with provided admin credentials.
4. Compared pre-login and post-login HTML.

Key finding from authenticated page JavaScript:
- The dashboard calls: /api/v1/user/metadata
- Frontend intentionally redacts the flag only in UI rendering:
  - if(displayData.flag) displayData.flag = "REDACTED_ENCRYPTED_INVARIANT";

This means the backend response still contains the real flag, and only the browser-side display hides it.

## Exploitation Steps
1. Authenticate:
   - POST /login with admin@apexcache.io and ApexAdmin123!@#
2. Directly request metadata endpoint in the authenticated session:
   - GET /api/v1/user/metadata
3. Parse JSON response body.

Observed response included:
- cached: false
- x_header: X-CACHE-MISS-FETCHED-FROM-ORIGIN
- content.flag: real flag value

## Proof (Captured Response)
From the authenticated metadata response:

{"cached":false,"content":{"access_key":"AKIA-APEX-9921-X","flag":"CIPH{C4CH3_D3C3PT10N_IS_TH3_N3W_BLACK}","role":"Global Optimizer","server_status":"Overheated","username":"admin"},"x_header":"X-CACHE-MISS-FETCHED-FROM-ORIGIN"}

## Flag
CIPH{C4CH3_D3C3PT10N_IS_TH3_N3W_BLACK}

## Notes
- The intended theme references cache poisoning and signature heuristics, but in this instance the practical break is simpler: client-side redaction only.
- Always inspect the raw API response, not just what the frontend renders.
