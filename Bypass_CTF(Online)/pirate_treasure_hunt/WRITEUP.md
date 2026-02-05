# Bypass CTF Competition Writeup : Pirate Treasure Hunt

## Challenge Description
> Set sail on an adventure through the treacherous seas of mathematics! Navigate through 20 nautical challenges, each more perilous than the last. Solve riddles of arithmetic under time pressure as the Kraken closes in. Only those who master the pirate code of division, multiplication, and conquest can claim the legendary pirate's map.

## Challenge Overview

This is a web-based automation challenge that requires:
- Interacting with a REST API
- Solving 20 mathematical expressions in sequence
- Handling time constraints (5-second limit per question)
- Dealing with anti-bot protection
- Automating the entire process programmatically

The challenge presents itself as a pirate-themed math game where you must answer 20 arithmetic questions correctly to claim the treasure map (flag).

## Analysis

### Understanding the Challenge

From the description, we learn:
- **"20 nautical challenges"** → 20 math problems to solve
- **"time pressure as the Kraken closes in"** → Time limit per question
- **"pirate code of division, multiplication, and conquest"** → Various arithmetic operations
- **"claim the legendary pirate's map"** → The flag is the reward

### API Endpoints Discovery

The challenge provides two main API endpoints:

1. **POST /api/game/start**
   - Initializes a new game session
   - Returns: `sessionId` and first question

2. **POST /api/game/answer**
   - Submits an answer for the current question
   - Requires: `sessionId` and `answer`
   - Returns: Correctness status and next question (or flag if completed)

### Game Mechanics

- **20 Sequential Questions**: Must answer all correctly in order
- **5-Second Time Limit**: Each question must be answered within 5 seconds
- **Anti-Bot Check**: Answers submitted too quickly may be rejected
- **Session-Based**: Must maintain the same session throughout all 20 questions

## Solution

### Strategy

Since manual solving would be:
- Too slow (20 questions × 5 seconds = tight timing)
- Error-prone (one mistake = start over)
- Tedious (repetitive calculations)

**Automation is the only practical approach.**

### Implementation

```python
import requests
import time

BASE_URL = "http://20.196.136.66:3600"

def solve_pirate_challenge():
    session = requests.Session()
    
    # 1. Start the game to get session ID and first question
    print("[*] Hoisting the sails...")
    resp = session.post(f"{BASE_URL}/api/game/start")
    data = resp.json()
    
    if not data.get('success'):
        print("[-] Failed to start the voyage.")
        return

    session_id = data['sessionId']
    question = data['question']
    
    # 2. Loop through the 20 islands (questions)
    for i in range(20):
        expr = question['expression']
        print(f"[+] Island {question['number']}/20: {expr}")
        
        # Clean the expression (e.g., "15 + 10 = ?" -> "15 + 10")
        # Also handle pirate terms like 'plunder' if they appear as multiplication
        clean_expr = expr.split('=')[0].strip()
        clean_expr = clean_expr.replace('x', '*').replace('plunder', '*')
        
        try:
            answer = eval(clean_expr)
        except Exception as e:
            print(f"[-] Error calculating riddle: {e}")
            break
            
        # 3. Wait 1 second to satisfy the anti-speed check
        time.sleep(1.0)
        
        # 4. Claim the gold (submit answer)
        payload = {
            "sessionId": session_id,
            "answer": float(answer)
        }
        
        resp = session.post(f"{BASE_URL}/api/game/answer", json=payload)
        res_data = resp.json()
        
        if not res_data.get('success') or not res_data.get('isCorrect'):
            print(f"[-] The Kraken got us! {res_data}")
            break
            
        if res_data.get('gameCompleted'):
            print("\n[!] TREASURE FOUND!")
            print(f"[!] Map (Flag): {res_data.get('flag')}")
            break
        
        # Prepare for the next riddle
        question = res_data['nextQuestion']

if __name__ == "__main__":
    solve_pirate_challenge()
```

### Execution Output

```
[*] Hoisting the sails...
[+] Island 1/20: 9 - 10
[+] Island 2/20: 8 + 19
[+] Island 3/20: 12 + 10
[+] Island 4/20: 7 + 13
[+] Island 5/20: 6 + 6
[+] Island 6/20: 25 - 43 + 46
[+] Island 7/20: 9 + 46 - 48
[+] Island 8/20: 14 + 22 + 30
[+] Island 9/20: 10 + 38 - 43
[+] Island 10/20: 20 + 27 - 7
[+] Island 11/20: 31 - 16 + 10 * 35
[+] Island 12/20: 100 - 47 + 95 + 31
[+] Island 13/20: 90 * 95 * 36 - 87
[+] Island 14/20: 17 - 55 + 73 - 26
[+] Island 15/20: 67 - 95 - 100 - 87
[+] Island 16/20: 89 / 183 + 185 + 114 + 139
[+] Island 17/20: 69 * 165 + 168 + 170 / 158
[+] Island 18/20: 81 + 127 * 155 / 111 - 43
[+] Island 19/20: 93 / 25 / 146 / 160 + 166
[+] Island 20/20: 165 / 127 - 189 / (146 * 107)

[!] TREASURE FOUND!
[!] Map (Flag): BYPASS_CTF{d1v1d3_n_c0nqu3r_l1k3_4_p1r4t3}
```

## Technical Breakdown

### 1. Session Management

```python
session = requests.Session()
```

Using `requests.Session()` maintains cookies and session state across all API calls, crucial for the challenge's session-based design.

### 2. Expression Parsing

```python
clean_expr = expr.split('=')[0].strip()
```

Expressions come in format `"9 - 10 = ?"`, so we split on `=` and take the first part.

### 3. Mathematical Evaluation

```python
answer = eval(clean_expr)
```

Python's `eval()` function:
- Handles all arithmetic operations (+, -, *, /)
- Respects order of operations (PEMDAS/BODMAS)
- Evaluates parentheses correctly

**Examples:**
- `eval("9 - 10")` → `-1`
- `eval("31 - 16 + 10 * 35")` → `31 - 16 + 350` → `365` ✓
- `eval("165 / 127 - 189 / (146 * 107)")` → Handles nested operations

### 4. Anti-Bot Delay

```python
time.sleep(1.0)
```

Introduces a 1-second delay between receiving the question and submitting the answer. This:
- Mimics human solving time
- Avoids triggering anti-bot mechanisms
- Stays well within the 5-second time limit

### 5. Error Handling

```python
if not res_data.get('success') or not res_data.get('isCorrect'):
    print(f"[-] The Kraken got us! {res_data}")
    break
```

Gracefully handles incorrect answers or API errors.

## Key Challenges & Solutions

### Challenge 1: Operator Precedence

**Problem**: Expression like `31 - 16 + 10 * 35`

**Solution**: Python's `eval()` automatically follows PEMDAS:
```
31 - 16 + 10 * 35
= 31 - 16 + 350    (multiply first)
= 365              (left-to-right for same precedence)
```

### Challenge 2: Division Precision

**Problem**: Division can create floating-point numbers:
```python
89 / 183 + 185 + 114 + 139
= 0.486... + 438
= 438.486...
```

**Solution**: Convert to `float()` when submitting:
```python
"answer": float(answer)
```

### Challenge 3: Nested Parentheses

**Problem**: Complex expressions like `165 / 127 - 189 / (146 * 107)`

**Solution**: `eval()` handles nested operations automatically:
```
= 1.299... - 189 / 15622
= 1.299... - 0.0121...
= 1.287...
```

### Challenge 4: Timing Balance

**Problem**: Too fast = bot detection; too slow = timeout

**Solution**: 1-second delay provides perfect balance:
- Fast enough: Well within 5-second limit
- Slow enough: Appears human-like

## API Response Structure

### Start Game Response

```json
{
  "success": true,
  "sessionId": "unique-session-id",
  "question": {
    "number": 1,
    "expression": "9 - 10 = ?",
    "timeLimit": 5000
  }
}
```

### Answer Response (In Progress)

```json
{
  "success": true,
  "isCorrect": true,
  "questionNumber": 1,
  "nextQuestion": {
    "number": 2,
    "expression": "8 + 19 = ?",
    "timeLimit": 5000
  },
  "score": 1,
  "progress": "1 / 20"
}
```

### Answer Response (Game Completed)

```json
{
  "success": true,
  "isCorrect": true,
  "gameCompleted": true,
  "flag": "BYPASS_CTF{d1v1d3_n_c0nqu3r_l1k3_4_p1r4t3}",
  "score": 20,
  "progress": "20 / 20"
}
```

## Flag
```
BYPASS_CTF{d1v1d3_n_c0nqu3r_l1k3_4_p1r4t3}
```

The flag perfectly captures the essence of the challenge:
- **"divide"** → Division operations in the math problems
- **"conquer"** → Conquering all 20 challenges
- **"like a pirate"** → The pirate theme throughout

It's a play on the classic "divide and conquer" strategy, with leetspeak (`d1v1d3`, `c0nqu3r`, `l1k3`, `4`, `p1r4t3`) giving it that CTF flair.

## Alternative Approaches

### JavaScript (Browser Console)

If there's a web interface:

```javascript
async function autoSolve() {
    let resp = await fetch('/api/game/start', { method: 'POST' });
    let data = await resp.json();
    let sessionId = data.sessionId;
    let question = data.question;
    
    for (let i = 0; i < 20; i++) {
        let expr = question.expression.split('=')[0].trim();
        let answer = eval(expr);
        
        await new Promise(r => setTimeout(r, 1000));
        
        resp = await fetch('/api/game/answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sessionId, answer })
        });
        
        data = await resp.json();
        console.log(`Question ${i+1}: ${expr} = ${answer}`);
        
        if (data.gameCompleted) {
            console.log('Flag:', data.flag);
            break;
        }
        question = data.nextQuestion;
    }
}

autoSolve();
```

### Curl + Bash Script

```bash
#!/bin/bash
BASE_URL="http://20.196.136.66:3600"

# Start game
RESPONSE=$(curl -s -X POST "$BASE_URL/api/game/start")
SESSION_ID=$(echo "$RESPONSE" | jq -r '.sessionId')
EXPR=$(echo "$RESPONSE" | jq -r '.question.expression')

for i in {1..20}; do
    CLEAN_EXPR=$(echo "$EXPR" | sed 's/=.*$//')
    ANSWER=$(echo "$CLEAN_EXPR" | bc -l)
    
    echo "Question $i: $EXPR = $ANSWER"
    sleep 1
    
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/game/answer" \
        -H "Content-Type: application/json" \
        -d "{\"sessionId\":\"$SESSION_ID\",\"answer\":$ANSWER}")
    
    if echo "$RESPONSE" | jq -e '.gameCompleted' > /dev/null; then
        echo "Flag: $(echo "$RESPONSE" | jq -r '.flag')"
        break
    fi
    
    EXPR=$(echo "$RESPONSE" | jq -r '.nextQuestion.expression')
done
```

## Learning Outcomes

### Skills Demonstrated

1. **Web Automation**: Programmatically interacting with web APIs
2. **Session Management**: Maintaining state across multiple requests
3. **Expression Evaluation**: Safely parsing and calculating mathematical expressions
4. **Timing Management**: Balancing speed with detection avoidance
5. **Error Handling**: Graceful failure and recovery mechanisms
6. **JSON Parsing**: Working with structured API responses

### Python Concepts Used

```python
import requests      # HTTP client library
import time          # Timing and delays
import json          # JSON handling (implicit in requests)

# Session management
session = requests.Session()

# HTTP POST with JSON
resp = session.post(url, json=payload)

# Response parsing
data = resp.json()

# String manipulation
clean_expr = expr.split('=')[0].strip()

# Mathematical evaluation
answer = eval(expression)

# Type conversion
float(answer)

# Delays
time.sleep(seconds)
```

## Security Considerations

### The `eval()` Warning

⚠️ **IMPORTANT**: `eval()` is used here safely because we control the input source (the challenge server). 

**NEVER use `eval()` on untrusted user input!**

```python
# SAFE: Controlled input from challenge API
answer = eval("9 - 10")

# DANGEROUS: User-provided input
user_input = input("Enter expression: ")
eval(user_input)  # Can execute arbitrary code!
```

**For production code, use safer alternatives:**

```python
import ast
import operator

def safe_eval(expr):
    """Safely evaluate mathematical expressions"""
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }
    
    node = ast.parse(expr, mode='eval')
    # ... validation and evaluation logic
```

### Anti-Bot Mechanisms

The challenge implements basic bot detection:

1. **Time-based checks**: Too fast = suspicious
2. **Session-based tracking**: Prevents parallel attempts
3. **Sequential progression**: Can't skip questions

**Defense lessons:**
- Rate limiting is essential for game/quiz APIs
- Session management prevents abuse
- Progressive difficulty discourages automation attempts

## Tools & Commands

### Installation

```bash
# Install required library
pip install requests

# Or using pip3
pip3 install requests
```

### Running the Solution

```bash
# Make executable (Linux/Mac)
chmod +x solve.py

# Run the script
python solve.py

# Or with python3
python3 solve.py
```

### Testing Individual Expressions

```python
# Test expression evaluation
python3 -c "print(eval('31 - 16 + 10 * 35'))"
# Output: 365

# Test with division
python3 -c "print(eval('89 / 183 + 185 + 114 + 139'))"
# Output: 438.4863387978142
```

### Key Lessons

1. **Automation is Powerful**: What would take humans minutes/hours takes code seconds
2. **APIs are Everywhere**: Understanding REST APIs is fundamental
3. **Session Management Matters**: Maintaining state is crucial in multi-step processes
4. **Timing is Important**: Balance between speed and detection
5. **Error Handling is Essential**: Robust code handles failures gracefully

