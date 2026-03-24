# CrackOn Web CTF Writeup

## Challenge
- Target: https://web2.crack-on.live/
- Goal: Retrieve flag in format `CrackOn{...}`

## Initial Recon
1. Visiting `/` returned only:
   - `User Profile Service`
2. Probing common routes showed:
   - `/profile` -> `500 Internal Server Error`
3. Testing query parameters found valid entry point:
   - `/profile?id=1` -> `User exists`
   - `/profile?id=999` -> `User not found`

This indicated a backend lookup by numeric `id`.

## Vulnerability Discovery
Boolean-based SQL injection was confirmed on `id`:

- `id=999 OR 1=1` -> `User exists`
- `id=999 AND 1=2` -> `User not found`

This established a reliable blind boolean oracle.

## DB Fingerprinting
SQLite was identified by probing DB-specific functions:

- `id=1 AND (SELECT sqlite_version()) LIKE '3%'` -> true
- MySQL/Postgres-style probes (`version()`, `@@version`, `database()`, `current_database()`) -> false

## Exploitation Strategy
Because output was only true/false text, the approach was:

1. Enumerate table names from `sqlite_master`.
2. Enumerate each table's columns via `pragma_table_info('<table>')`.
3. Search text-cast column values for `CrackOn{%`.
4. Extract matching value character-by-character using `unicode(substr(...))` with binary search.

## Automation Script
Local script created: [sqli_flag_extractor.py](sqli_flag_extractor.py)

Key points:
- Sends requests to `https://web2.crack-on.live/profile?id=<payload>`
- Treats `User exists` as boolean true
- Uses binary search for:
  - Numeric values (`count`, `length`)
  - Character codepoints (`unicode(substr(...))`)
- Prioritizes suspicious table names (`flag`, `secret`, `admin`, etc.)

## Execution
Command used:

```powershell
& "C:/Users/Rakesh R K/AppData/Local/Microsoft/WindowsApps/python3.13.exe" .\sqli_flag_extractor.py
```

Notable extractor output:
- Tables discovered: `admin_backup`, `flag`, `products`, `system_archive`, `system_logs`, `users`
- Matching field found: `system_archive.flag`

## Final Flag
`CrackOn{Sic_Mundus_Creatus_Est_SQLi_83}`

## Notes
- This was blind boolean SQLi with minimal response data.
- Full extraction was still practical via binary search, significantly reducing requests compared to linear brute force.
