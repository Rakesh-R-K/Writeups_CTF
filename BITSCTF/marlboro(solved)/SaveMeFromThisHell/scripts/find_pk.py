from pathlib import Path
p=Path('output/zip/00007332/smoke.png')
b=p.read_bytes()
pat=b'PK\x03\x04'
offs=[]
start=0
while True:
    j=b.find(pat,start)
    if j==-1: break
    offs.append(j)
    start=j+1
print('\n'.join(str(x) for x in offs))
