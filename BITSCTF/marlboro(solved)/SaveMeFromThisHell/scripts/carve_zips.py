from pathlib import Path
p=Path('/mnt/c/Users/Rakesh R K/Downloads/bitsctf/marlboro/SaveMeFromThisHell/output/zip/00007332/smoke.png')
b=p.read_bytes()
pat=b'PK'
offs=[]
start=0
while True:
    j=b.find(pat,start)
    if j==-1: break
    offs.append(j)
    start=j+2
outdir=Path('/mnt/c/Users/Rakesh R K/Downloads/bitsctf/marlboro/SaveMeFromThisHell/output/zip/00007332/carved')
outdir.mkdir(parents=True,exist_ok=True)
for i,o in enumerate(offs):
    end = offs[i+1] if i+1<len(offs) else len(b)
    data=b[o:end]
    f=outdir/f'carved_{i:02d}_{o}.zip'
    f.write_bytes(data)
    print('WROTE',f)
