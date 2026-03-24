# Trading Platform - Web Challenge Writeup

Challenge Name: Trading Platform  
Challenge URL: http://51.20.10.121:8005  
Flag Format: CrackOn{}

## Objective
Identify unusual behavior in the internal trading platform and recover the hidden flag.

## Reconnaissance
1. Opened the landing page and inspected the HTML source.
2. Found an HTML comment leaking test credentials:
   - TODO: Delete the testing account (test:test)
3. The login flow was two-step:
   - Step 1: submit username on /
   - Step 2: submit password on /password/test

## Authentication and Feature Mapping
1. Logged in using test:test.
2. Reached the dashboard and discovered the following routes from navigation and page scripts:
   - /orders
   - /orders_archive
   - /order/<id>/receipt
   - /order/<id>/archive
3. Checked archived orders and found a suspicious row:
   - Ticker: FLAG
   - Order ID: 300198

## Vulnerability
Broken Access Control / Insecure Object Reference on order receipt endpoint.

The endpoint /order/<id>/receipt returned receipt details directly for order IDs accessible to the logged-in testing user. The FLAG order receipt was retrievable and disclosed sensitive data.

## Exploitation
1. Requesting /order/300198/receipt returned a modal HTML fragment.
2. The response body contained:
   - CrackOn{broken_access_control}

## Automated Local Exploit Script
A local script was created to make exploitation reproducible:
- [solve_trading_platform.py](solve_trading_platform.py)

What the script does:
1. Creates a session with cookies.
2. Logs in with test:test using the two-step flow.
3. Fetches /orders_archive and extracts the order ID for ticker FLAG.
4. Fetches /order/<flag_order_id>/receipt.
5. Extracts and prints the flag using regex.

Run command used on Windows PowerShell:
& "C:/Users/Rakesh R K/AppData/Local/Microsoft/WindowsApps/python3.13.exe" "c:/Users/Rakesh R K/Downloads/dark/trading_platform/solve_trading_platform.py"

## Flag
CrackOn{broken_access_control}

## Security Recommendation
1. Enforce strict authorization checks on every object-level endpoint, especially /order/<id>/receipt.
2. Never expose test accounts in production-facing code or comments.
3. Remove predictable direct object IDs or protect them with robust server-side access controls.
4. Add audit logging and automated tests for authorization regressions.
