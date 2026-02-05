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