# The Odyssey — Writeup

## Summary
- Challenge type: Crypto CTF (AES → Drive ZIP → ROT13-obfuscated flag).
- Final flag: `BPCTF{H3l3n_15_R3tr13v3d!!!}`

## Files inspected
- AES script: [AES.py](AES.py)
- RSA stub (unused): [rsa.py](rsa.py)
- Downloaded archive: `The Odyssey.zip` containing `The Odyssey/Flag.txt`

## Step-by-step

1. AES decryption

   - The provided script `AES.py` performs AES-CBC decryption with:
     - Key: `b"odysseus_journey"`
     - IV (padded): `b"Princess"` (left-justified to 16 bytes)
   - Running the script produced a Google Drive URL referencing `The Odyssey.zip`.

   Reproduce:

```bash
python AES.py
```

2. Retrieve and inspect the ZIP

   - Download the Drive file referenced by the AES plaintext and save it as `The Odyssey.zip` in the working directory.
   - The archive is password-protected and contains `The Odyssey/Flag.txt`.

3. Password recovery / extraction

   - Hints in the challenge (AES key, IV and narrative) suggested passwords such as `odysseus`, `Princess`, `helen`, etc.
   - Tried candidate passwords programmatically; the correct password was `odysseus`.

   Example extraction (Python):

```python
import zipfile
zz = zipfile.ZipFile('The Odyssey.zip')
zz.extract('The Odyssey/Flag.txt', pwd=b'odysseus')

with open('The Odyssey/Flag.txt','r') as f:
    print(f.read())
```

4. Decode flag

   - `Flag.txt` contained: `OCPGS{U3y3a_15_E3ge13i3q!!!}`
   - This is ROT13-encoded. Applying ROT13 yields the final flag:

```python
import codecs
print(codecs.decode('OCPGS{U3y3a_15_E3ge13i3q!!!}', 'rot_13'))
# -> BPCTF{H3l3n_15_R3tr13v3d!!!}
```

## Notes
- The RSA parameters in `rsa.py` (`n`, `e`, `c`) were not needed for this challenge; they appear to be a decoy.
- The flow is intentionally linear: AES → link → passworded ZIP → ROT13 flag.

## RSA decryption

- The file `rsa.py` contained an RSA public key (`n`, `e`) and a ciphertext `c`.
- The modulus `n` factors into two very close primes, so Fermat's factorization method quickly recovers `p` and `q`:

```text
p = 11307781433945180701283750671246004718934733341415144444959104053534874483693948046243146551824287332443991084420801729954616329588547554761273206134123669
q = 11307781433945180701283750671246004718934733341415144444959104053534874483693948046243146551824287332443991084420801729954616329588547554761273206134132911
```

- Using these factors we compute the private exponent `d` and decrypt `c`:

```python
# phi = (p-1)*(q-1)
# d = inverse(e, phi)
# m = pow(c, d, n)
# bytes = m.to_bytes((m.bit_length()+7)//8, 'big')
# -> b'Princess'
```

- Decrypted plaintext: `Princess` — this matches the IV used in `AES.py` (and is another in-challenge hint). It served as a useful cross-check and secondary hint when extracting the ZIP.

## Repro checklist

- Run `python AES.py` to get the Drive link.
- Download the Drive file and save it as `The Odyssey.zip`.
- Extract `The Odyssey/Flag.txt` with password `odysseus`.
- ROT13-decode the contents to reveal the flag.

---
Recovered flag: `BPCTF{H3l3n_15_R3tr13v3d!!!}`
