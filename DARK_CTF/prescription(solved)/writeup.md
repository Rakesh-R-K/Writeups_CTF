# MedGuard Web Challenge Writeup

## Challenge
Target: http://51.20.10.121:5003

Goal: Retrieve the hidden flag from the prototype medical records system.

## Final Flag
CrackOn{graphql_data_leak}

## Executive Summary
The application exposed an authenticated GraphQL endpoint that allowed an authenticated low-privilege user to request prescription data for arbitrary user IDs.

Two weaknesses were chained:
1. Weak credentials (valid account found: user / user)
2. Authorization failure (IDOR) in GraphQL query getPrescriptions(userId: X)

Additionally, sensitive field exposure existed because the flag field was queryable through GraphQL.

## Step-by-Step Exploitation

### 1) Initial Recon
Observed routes from endpoint probing:
- /login (public)
- /add_prescription (auth required)
- /view_prescriptions (auth required, discovered during deeper route fuzzing)
- /logout (auth required)

Most guessed API routes returned 404.

### 2) Credential Discovery
A local brute-force script tested common demo credentials and found:
- username: user
- password: user

Login response:
{"message":"Login successful","userID":2}

### 3) Hidden GraphQL Discovery
After login, page source from /view_prescriptions showed frontend JavaScript calling:
- POST /graphql

It sent a query similar to:
query {
  getPrescriptions(userId: ${userID}) {
    id
    userId
    prescriptionDetails
  }
}

Important clue in source:
- A comment hinted sensitive handling around flag and query behavior.

### 4) GraphQL Abuse (IDOR)
Using the authenticated session (userID 2), direct GraphQL queries were sent with different userId values.

Critical finding:
- Querying userId: 1 returned admin prescription records, proving broken object-level authorization.

### 5) Sensitive Field Exposure
The GraphQL type included a flag field on PrescriptionType.
By requesting flag in the selection set, records for userId 1 exposed:
- flag: CrackOn{graphql_data_leak}

## Proof of Exploit
Working query used after authenticating as user/user:

```graphql
query {
  getPrescriptions(userId: 1) {
    id
    userId
    prescriptionDetails
    flag
  }
}
```

Representative leaked row:

```json
{
  "id": 43,
  "userId": 1,
  "prescriptionDetails": "Prescription 43 for Admin",
  "flag": "CrackOn{graphql_data_leak}"
}
```

## Vulnerability Analysis
- Authentication weakness: Predictable/default credentials enabled initial access.
- Broken access control (IDOR/BOLA): Server trusted client-supplied userId and did not enforce ownership checks.
- Excessive data exposure: Sensitive field flag was available in a normal GraphQL query.

## Security Impact
Any authenticated user could enumerate other users' records and retrieve sensitive fields, leading to confidentiality breach and secret extraction.

## Recommended Fixes
1. Enforce object-level authorization server-side:
   - Ignore client-supplied userId for user-scoped data.
   - Derive identity from session/JWT and filter records accordingly.
2. Remove sensitive fields from user-facing GraphQL types:
   - Do not expose internal fields like flag in production schemas.
3. Harden authentication:
   - Remove default credentials, enforce strong password policy, add rate-limiting/lockouts.
4. Add GraphQL protections:
   - Disable introspection in production where appropriate.
   - Add schema-level authorization directives and resolver checks.
5. Monitoring and alerting:
   - Detect abnormal cross-user queries and high-volume enumeration.

## Local Artifacts Used
- Final Solve script

## Conclusion
The flag was obtained by chaining weak authentication with GraphQL authorization/data-exposure flaws.
Recovered flag: CrackOn{graphql_data_leak}
