# Bypass CTF Challenge Writeup : Signal From the Deck 

## Challenge Description
> Something aboard the ship is trying to communicate.
> No words. No explanations.
> Only patterns.
> 
> Nothing useful lives on the surface.
> The answer waits for those who pay attention.

## Challenge Overview

This is a web-based logic and cryptanalysis challenge involving:
- Pattern recognition and learning
- Session cookie manipulation and analysis
- Server-side state analysis
- Brute-force learning of mappings
- Game automation

The challenge presents a "monkey and banana" game where you must click the correct positions based on banana signals, but the mapping between bananas and positions is hidden and must be learned.

## Analysis

### Understanding the Clues

The challenge description provides critical hints:
- **"Only patterns"** → There's a hidden pattern to discover
- **"Nothing useful lives on the surface"** → Don't trust what you see in the UI
- **"The answer waits for those who pay attention"** → Need to analyze behavior

### Initial Exploration

Accessing the web application reveals:
- A game interface with monkeys and bananas
- Multiple positions (1-9) to click
- A "signal" showing which banana is displayed
- No obvious indication of which position is correct

### Key Discovery: Session Cookies

The critical insight comes from examining the session cookie. Flask applications often store session data in signed cookies, which can be decoded (though not modified without the secret key).

**Decoding the Flask Session Cookie:**

```python
import base64
import json

def decode_session_cookie(session_cookie):
    """Decode the Flask session cookie to extract the sequence"""
    parts = session_cookie.split('.')
    payload = parts[0]
    
    # Add padding for base64
    padding = 4 - (len(payload) % 4)
    if padding != 4:
        payload += '=' * padding
    
    decoded = base64.urlsafe_b64decode(payload)
    return json.loads(decoded)
```

**What we find:**
```json
{
  "sequence": [9, 9, 4, 3, 7, 3, 7, 3]
}
```

This reveals the **entire sequence** of bananas that will be shown! However, we still don't know which position corresponds to each banana number.

### The Challenge Structure

**API Endpoints:**
1. `POST /api/new` - Start a new game, returns session cookie with sequence
2. `GET /api/signal` - Get the current banana signal
3. `POST /api/click` - Submit a position guess

**Game Mechanics:**
- The sequence is 8 steps long
- Each step shows a specific banana (numbered 1-9)
- You must click the correct position (1-9) for that banana
- The mapping between banana numbers and positions is consistent within a game
- Wrong clicks reset your progress

### The Vulnerability

**Server-Side State Exposure**: The Flask session cookie contains the entire game sequence in plaintext (base64-encoded JSON). While this doesn't directly give us the answer, it allows us to:
1. Know how many steps are in the game
2. Know which bananas we'll encounter
3. Plan our learning strategy

**Missing Server-Side Validation**: The game accepts clicks and returns whether they're correct without rate limiting, allowing us to brute-force the banana-to-position mapping.

## Solution

### Strategy

Since we know the sequence but not the mapping, we can use a **learning approach**:

1. **Decode the session cookie** to get the sequence
2. **For each unique banana**, brute-force positions 1-9 to find the correct one
3. **Remember the mappings** and reuse them when the same banana appears again
4. **Complete all 8 steps** to get the flag

### Implementation

```python
import requests
import json
import base64

BASE_URL = "https://banana-2-2nqw.onrender.com"

def decode_session_cookie(session_cookie):
    """Decode the Flask session cookie to extract the sequence"""
    parts = session_cookie.split('.')
    payload = parts[0]
    padding = 4 - (len(payload) % 4)
    if padding != 4:
        payload += '=' * padding
    
    try:
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        return None

def solve():
    """Learn the banana->position mapping and solve the game"""
    session = requests.Session()
    
    # Start new game
    print("🎮 Starting new game...")
    response = session.post(f"{BASE_URL}/api/new")
    session_cookie = session.cookies.get('session')
    data = decode_session_cookie(session_cookie)
    
    sequence = data.get('sequence', [])
    print(f"📜 Sequence from cookie: {sequence}")
    print(f"🎯 Game length: {len(sequence)} steps\n")
    
    banana_to_position = {}
    
    # For each step, brute force to find the correct position
    for step in range(len(sequence)):
        signal_response = session.get(f"{BASE_URL}/api/signal")
        signal = signal_response.json()
        
        if signal.get('done'):
            break
        
        banana = signal.get('banana')
        
        # If we already know this banana's position, use it
        if banana in banana_to_position:
            position = banana_to_position[banana]
            print(f"Step {step+1}: Banana={banana} → Position={position}")
            
            click_response = session.post(f"{BASE_URL}/api/click",
                                         json={"clicked": position},
                                         headers={"Content-Type": "application/json"})
            result = click_response.json()
            
            if result.get('done') and result.get('flag'):
                print(f"\n🎉 FLAG: {result['flag']}")
                return result['flag']
        else:
            # Need to learn this banana's position
            print(f"Step {step+1}: Banana={banana} → Learning...")
            
            current_cookie = session.cookies.get('session')
            
            for pos in range(1, 10):
                test_session = requests.Session()
                test_session.cookies.set('session', current_cookie)
                
                click_response = test_session.post(f"{BASE_URL}/api/click",
                                                   json={"clicked": pos},
                                                   headers={"Content-Type": "application/json"})
                result = click_response.json()
                
                if result.get('correct'):
                    banana_to_position[banana] = pos
                    print(f"         Banana={banana} → Position={pos} ✓")
                    
                    # Make the actual click with our main session
                    session.post(f"{BASE_URL}/api/click",
                                json={"clicked": pos},
                                headers={"Content-Type": "application/json"})
                    
                    if result.get('done') and result.get('flag'):
                        print(f"\n🎉 FLAG: {result['flag']}")
                        return result['flag']
                    break
    
    return None

if __name__ == "__main__":
    print("="*60)
    print("       Monkey Banana Signal CTF Solver")
    print("="*60)
    print()
    
    flag = solve()
    
    if flag:
        print(f"\n🚩 FINAL FLAG: {flag}")
```

### Execution Output

```
============================================================
       Monkey Banana Signal CTF Solver
============================================================

🎮 Starting new game...
📜 Sequence from cookie: [9, 9, 4, 3, 7, 3, 7, 3]
🎯 Game length: 8 steps

Step 1: Banana=9 → Learning...
         Banana=9 → Position=2 ✓
Step 2: Banana=9 → Position=2
Step 3: Banana=4 → Learning...
         Banana=4 → Position=7 ✓
Step 4: Banana=3 → Learning...
         Banana=3 → Position=9 ✓
Step 5: Banana=7 → Learning...
         Banana=7 → Position=1 ✓
Step 6: Banana=3 → Position=9
Step 7: Banana=7 → Position=1
Step 8: Banana=3 → Position=9

🎉 FLAG: BYPASS_CTF{s3rv3r_s1d3_sl4y_th1ngs}

🚩 FINAL FLAG: BYPASS_CTF{s3rv3r_s1d3_sl4y_th1ngs}
```

## Technical Breakdown

### 1. Flask Session Cookie Decoding

Flask stores session data in signed cookies using the `itsdangerous` library. The cookie structure:

```
<base64_payload>.<timestamp>.<signature>
```

We can decode the payload (first part) without knowing the secret key:

```python
# Example cookie: eyJzZXF1ZW5jZSI6WzksOSw0LDMsNywzLDcsM119.ZqR8wQ.abc123

payload = cookie.split('.')[0]  # "eyJzZXF1ZW5jZSI6WzksOSw0LDMsNywzLDcsM119"

# Base64 decode (URL-safe)
decoded = base64.urlsafe_b64decode(payload + padding)

# Parse JSON
data = json.loads(decoded)
# {"sequence": [9, 9, 4, 3, 7, 3, 7, 3]}
```

### 2. Learning Algorithm

The key insight is that we only need to learn each unique banana once:

```python
banana_to_position = {}  # Cache of learned mappings

for each step:
    if banana in cache:
        use cached position
    else:
        for position in 1..9:
            test this position
            if correct:
                cache[banana] = position
                break
```

**Optimization**: Since bananas repeat in the sequence, we learn:
- Banana 9 → Position 2 (step 1)
- Banana 4 → Position 7 (step 3)
- Banana 3 → Position 9 (step 4)
- Banana 7 → Position 1 (step 5)

Steps 6-8 reuse the cached mappings!

### 3. Session Preservation for Testing

A clever technique used here:

```python
current_cookie = session.cookies.get('session')

for pos in range(1, 10):
    # Create a test session with the same cookie
    test_session = requests.Session()
    test_session.cookies.set('session', current_cookie)
    
    # Test without affecting main session
    result = test_session.post("/api/click", json={"clicked": pos})
    
    if result.get('correct'):
        # Now make the real click with main session
        session.post("/api/click", json={"clicked": pos})
        break
```

This allows testing without corrupting the main game state.

## Flag
```
BYPASS_CTF{s3rv3r_s1d3_sl4y_th1ngs}
```

The flag perfectly describes the vulnerability: **"server-side slay things"** - the server-side implementation has flaws that allow us to "slay" (defeat) it by:
1. Reading server-side state from cookies
2. Brute-forcing without rate limiting
3. Learning patterns through trial and error

## Vulnerabilities Exploited

### 1. **Sensitive Data in Session Cookies**

**Problem**: The entire game sequence is stored in the session cookie.

```python
# Server-side (vulnerable)
session['sequence'] = [9, 9, 4, 3, 7, 3, 7, 3]
# This gets encoded in the cookie sent to client!
```

**Fix**: Store only a session ID in the cookie, keep the sequence server-side:

```python
# Better approach
import uuid
games = {}

session_id = str(uuid.uuid4())
games[session_id] = {'sequence': [9, 9, 4, 3, 7, 3, 7, 3]}
session['id'] = session_id
```

### 2. **No Rate Limiting**

**Problem**: We can make unlimited requests to test positions.

**Fix**: Implement rate limiting:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/click', methods=['POST'])
@limiter.limit("10 per minute")
def click():
    # ... game logic
```

### 3. **Predictable Game State**

**Problem**: The game state is deterministic and stored client-side.

**Fix**: 
- Randomize banana-to-position mapping per session
- Store mappings server-side
- Add entropy to prevent prediction

### 4. **No Request Validation**

**Problem**: Server accepts rapid sequential requests without validation.

**Fix**:
- Track request timestamps
- Require minimum time between actions
- Detect automated patterns

## Learning Outcomes

### Concepts Demonstrated

1. **Session Cookie Analysis**: Understanding how web frameworks store session data
2. **Base64 Encoding**: Decoding data that's obscured but not encrypted
3. **State Management**: Exploiting how applications maintain state
4. **Brute-Force with Learning**: Efficiently learning patterns through trial
5. **API Reverse Engineering**: Understanding undocumented APIs through testing

### Python Techniques Used

```python
# Base64 decoding with padding
padding = 4 - (len(payload) % 4)
decoded = base64.urlsafe_b64decode(payload + '=' * padding)

# JSON parsing
data = json.loads(decoded)

# Dictionary caching
cache = {}
if key in cache:
    value = cache[key]
else:
    cache[key] = learned_value

# Session cloning for testing
test_session = requests.Session()
test_session.cookies.set('session', original_cookie)
```

## Alternative Approaches

### Manual Browser Inspection

You could solve this manually:

1. **Open DevTools** (F12)
2. **Find session cookie** in Application → Cookies
3. **Decode in Python/CyberChef**:
   ```python
   import base64, json
   cookie = "eyJzZXF1ZW5jZSI6WzksOSw0LDMsNywzLDcsM119"
   print(json.loads(base64.urlsafe_b64decode(cookie + '==')))
   ```
4. **Manually test each position** for each banana
5. **Write down the mappings**
6. **Complete the sequence**

But automation is much faster!

### Burp Suite Approach

Using Burp Suite:

1. **Intercept** the `/api/new` response
2. **Decode session cookie** in Burp's Decoder
3. **Send `/api/click` to Intruder**
4. **Brute-force** positions 1-9 for each banana
5. **Build the mapping** from responses
6. **Replay** the correct sequence

## Real-World Implications

### Similar Vulnerabilities in Production

1. **JWT Tokens with Sensitive Data**
   ```json
   {
     "user_id": 123,
     "is_admin": false,
     "secret_key": "abc123"  // ❌ Exposed!
   }
   ```

2. **Game State in Cookies**
   - Browser games storing score/level in cookies
   - Can be modified or analyzed
   - Should use server-side validation

3. **Prediction via Client-Side State**
   - Lottery/gambling apps with predictable seeds
   - Gacha games with known probabilities
   - Any game logic that's client-predictable

### Defense Best Practices

1. **Never trust client-side data**
2. **Store sensitive data server-side only**
3. **Use opaque session IDs, not encoded data**
4. **Implement rate limiting**
5. **Add entropy and randomization**
6. **Monitor for automated behavior**

## Tools & Commands

### Decoding Session Cookies

**Python:**
```python
import base64, json
cookie = "eyJzZXF1ZW5jZSI6WzksOSw0LDMsNywzLDcsM119"
padding = '=' * (4 - len(cookie) % 4)
print(json.loads(base64.urlsafe_b64decode(cookie + padding)))
```

**CyberChef Recipe:**
```
From Base64 (URL Safe)
→ JSON Beautify
```

**Command Line:**
```bash
echo "eyJzZXF1ZW5jZSI6WzksOSw0LDMsNywzLDcsM119" | base64 -d
```

### Testing APIs

**curl:**
```bash
# Start game
curl -X POST https://banana-2-2nqw.onrender.com/api/new -c cookies.txt

# Get signal
curl https://banana-2-2nqw.onrender.com/api/signal -b cookies.txt

# Click position
curl -X POST https://banana-2-2nqw.onrender.com/api/click \
  -H "Content-Type: application/json" \
  -d '{"clicked": 2}' \
  -b cookies.txt
```

## Difficulty Rating

**Medium** - This challenge requires:

**Skills needed:**
- Understanding of HTTP sessions and cookies
- Base64 encoding/decoding knowledge
- API interaction and automation
- Logical thinking for the learning algorithm
- Python programming

**What makes it medium:**
- Not immediately obvious what to look for
- Requires cookie decoding knowledge
- Need to design a learning strategy
- Automation is necessary for efficiency

**Good for:**
- Learning about web session security
- Understanding client-side data exposure
- Practicing API automation
- Learning pattern recognition algorithms

## Conclusion

"Signal From the Deck" is an excellent challenge that teaches important lessons about web application security, specifically around session management and client-side data exposure.

### Key Lessons

1. **Nothing is Hidden on the Client**: Even encoded data in cookies can be read
2. **Session Cookies Can Leak Information**: Be careful what you store in them
3. **Rate Limiting is Critical**: Brute-force attacks need to be prevented
4. **Server-Side Validation Matters**: Never trust client-side state
5. **Pattern Learning Works**: When you can test without penalty, you can learn

### The Challenge's Wisdom

The description's warnings were prophetic:
- **"Nothing useful lives on the surface"** → The UI is a distraction; the cookie holds the truth
- **"Only patterns"** → Learn the banana-to-position pattern
- **"The answer waits for those who pay attention"** → Pay attention to what the server tells you in cookies and responses

The flag message—"server-side slay things"—perfectly captures the essence: server-side implementation flaws that allow us to "slay" (defeat) the game through analysis and automation.

### Real-World Application

This challenge mirrors real security issues:
- Games storing state in cookies that can be modified
- APIs without rate limiting being brute-forced
- Session tokens containing sensitive information
- Client-side validation without server-side checks

**Remember**: In web security, the client is always in enemy territory. Never store sensitive or state-critical information where the client can read, modify, or predict it. The server must be the source of truth!

🏴‍☠️ The signal has been decoded, and the treasure claimed! ⚓
