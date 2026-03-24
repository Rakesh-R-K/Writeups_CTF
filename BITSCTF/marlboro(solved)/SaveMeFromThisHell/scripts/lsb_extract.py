from PIL import Image
from pathlib import Path
p=Path('/mnt/c/Users/Rakesh R K/Downloads/bitsctf/marlboro/SaveMeFromThisHell/output/zip/00007332/smoke.png')
im=Image.open(p)
pix=list(im.getdata())
# try extracting LSB from channels in order R,G,B and combinations
import itertools

def bits_to_bytes(bits):
    out=bytearray()
    for i in range(0,len(bits),8):
        byte=0
        for j in range(8):
            if i+j < len(bits):
                byte=(byte<<1)|bits[i+j]
            else:
                byte=(byte<<1)
        out.append(byte)
    return bytes(out)

candidates=[]
for channels in [(0,),(1,),(2,),(0,1,2)]:
    bits=[]
    for px in pix:
        for ch in channels:
            bits.append(px[ch]&1)
    data=bits_to_bytes(bits)
    candidates.append((channels,data[:2000]))
    # check magic
    for magic in [b'PK\x03\x04', b'%PDF', b'GIF8', b'\x89PNG', b'BITSCTF', b'FLAG']:
        if magic in data:
            print('Found',magic,'in channels',channels)

# write full candidate to files
outdir=Path('/mnt/c/Users/Rakesh R K/Downloads/bitsctf/marlboro/SaveMeFromThisHell/output/zip/00007332/lsb')
outdir.mkdir(parents=True,exist_ok=True)
for channels,data in candidates:
    fname=outdir/f'lsb_{"".join(map(str,channels))}.bin'
    fname.write_bytes(data)
    print('wrote',fname)

print('done')
