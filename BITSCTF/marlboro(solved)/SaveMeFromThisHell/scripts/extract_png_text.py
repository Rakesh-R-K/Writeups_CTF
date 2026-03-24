from pathlib import Path
p=Path('/mnt/c/Users/Rakesh R K/Downloads/bitsctf/marlboro/SaveMeFromThisHell/output/zip/00007332/smoke.png')
b=p.read_bytes()
# PNG signature
if not b.startswith(b'\x89PNG\r\n\x1a\n'):
    print('Not PNG')
    raise SystemExit(1)
pos=8
while pos < len(b):
    if pos+8>len(b): break
    length=int.from_bytes(b[pos:pos+4],'big')
    typ=b[pos+4:pos+8].decode(errors='replace')
    data=b[pos+8:pos+8+length]
    if typ in ('tEXt','zTXt','iTXt'):
        print('CHUNK',typ)
        if typ=='tEXt':
            try:
                k,v=data.split(b'\x00',1)
                print(k.decode(), v.decode(errors='replace'))
            except Exception as e:
                print('tEXt parse error',e,data[:100])
        elif typ=='iTXt':
            # naive split
            parts=data.split(b'\x00')
            print(parts[:5])
        else:
            print('zTXt (compressed) length',len(data))
    pos = pos+8+length+4
