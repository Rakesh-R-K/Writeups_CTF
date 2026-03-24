from pathlib import Path
import malbolge
p=Path('/mnt/c/Users/Rakesh R K/Downloads/bitsctf/marlboro/SaveMeFromThisHell/output/zip/00007332/decrypted.bin')
s=p.read_text()
# split header and code
parts=s.split('\n\n',1)
if len(parts)<2:
    code=parts[0]
else:
    code=parts[1]
print('PROGRAM LEN',len(code))
# malbolge.interpret expects iterable of ints
code_bytes=[ord(c) for c in code]
out=malbolge.interpret(code_bytes)
print('---OUTPUT---')
print(out)
