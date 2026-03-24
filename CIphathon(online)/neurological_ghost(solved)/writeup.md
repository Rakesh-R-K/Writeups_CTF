# Neurological Ghost - Web CTF Writeup

## Challenge Info
- Name: Neurological Ghost
- Target: http://78.46.147.244:8890/
- Theme hint: Legacy diagnostic handshake routes may still exist in hidden API hierarchy.

## Objective
Discover the unpurged invariant by traversing hidden or legacy API routes and extract the real flag.

## Methodology

### 1. Initial Recon
Started with basic endpoint and stack fingerprinting:
- Root endpoint returned HTTP 200.
- Server header identified Werkzeug with Python backend.
- Public JavaScript on homepage revealed an API base pointing to /api/v1/public.

Observed public endpoint:
- GET /api/v1/public/stats returned normal statistics JSON.

### 2. Hidden Route Discovery
Expanded enumeration around likely internal/legacy namespaces:
- /api/v1/internal returned HTTP 403 (important signal).

A 403 instead of 404 confirmed a real protected route exists and is not fully removed.

### 3. Internal Subtree Traversal
Performed focused probing under the internal namespace and found:
- /api/v1/internal/debug returned HTTP 403 with a different response profile than the generic internal deny page.

That response difference suggested the route was a distinct handler and likely the intended legacy diagnostic node.

### 4. Final Extraction
Requesting the endpoint directly returned JSON containing status fields and the actual flag.

## Key Requests Used

    curl -i http://78.46.147.244:8890/
    curl -i http://78.46.147.244:8890/api/v1/public/stats
    curl -i http://78.46.147.244:8890/api/v1/internal
    curl -i http://78.46.147.244:8890/api/v1/internal/debug

## Flag
CIPH{STAY_AI_HIDDEN_1337}

## Why This Was the Real Path
The challenge narrative referenced old diagnostic handshakes and hidden API hierarchy. The internal debug route matched that pattern exactly:
- It is outside the public API tree.
- It survived cleanup as a protected internal node.
- It leaks diagnostic core metadata and the flag payload.

## Security Note (Post-CTF)
In real systems, internal diagnostic endpoints should be:
- Fully removed from production builds, or
- Strictly isolated behind network-level controls and strong authentication,
- Never returning sensitive payloads on unauthorized requests.
