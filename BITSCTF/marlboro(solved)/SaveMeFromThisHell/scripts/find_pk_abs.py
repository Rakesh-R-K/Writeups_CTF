from pathlib import Path
p=Path('/mnt/c/Users/Rakesh R K/Downloads/bitsctf/marlboro/SaveMeFromThisHell/output/zip/00007332/smoke.png')
b=p.read_bytes()
pat=b'PK\x03\x04'
start=0
while True:
    j=b.find(pat,start)
    if j==-1: break
    print(j)
    start=j+1
