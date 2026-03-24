# The Gotham Files — Forensics Writeup

**Summary**

This was a PNG forensics/stego challenge. The artist left a hint in PNG textual metadata pointing to the `PLTE` (palette) and specifically the red channel: "only the red light tells the truth." The flag was embedded inside the PLTE palette red bytes.

**Files kept**

- `challenge.png` — original challenge image
- `plte_reds.bin` — extracted red bytes from the `PLTE` chunk
- `red_channel.png` — visual red-channel extraction (grayscale)

**What is `PLTE`?**

`PLTE` is the PNG palette chunk that contains a table of RGB palette entries (3 bytes per entry). It is used by indexed images (color type 3) and can also be present for other types as a suggested palette. Because it's a compact ordered RGB table, attackers can embed ASCII in one channel (e.g., every red byte) and it will survive typical PNG viewers.

**Evidence & hint**

The PNG contained two textual chunks (`tEXt`): `Artist: The Collector` and `Comment: Not all colors make it to the page. In Gotham, only the red light tells the truth.` That guided us to inspect the palette red channel.

**Steps taken (commands / code)**

1. Inspect PNG chunks and text metadata:

```bash
# list chunks and textual data
python - <<'PY'
from pathlib import Path
import struct
b = Path('challenge.png').read_bytes()
off=8
while off<len(b):
    L=struct.unpack('>I', b[off:off+4])[0]
    t=b[off+4:off+8].decode('latin1')
    print(t, L)
    off += 12+L
PY
```

2. Extract `PLTE` bytes and save red channel as ASCII:

```python
from pathlib import Path,struct
b = Path('challenge.png').read_bytes()
off=8
while off<len(b):
    L=struct.unpack('>I', b[off:off+4])[0]
    t=b[off+4:off+8].decode('latin1')
    data=b[off+8:off+8+L]
    if t=='PLTE':
        reds = bytes(data[i] for i in range(0,len(data),3))
        Path('plte_reds.bin').write_bytes(reds)
        break
    off += 12+L
```

3. Inspect the extracted `plte_reds.bin` using `strings` or Python and reveal the flag.

```bash
strings plte_reds.bin
# or in python
print(open('plte_reds.bin','rb').read().decode('latin1'))
```

**Result / Flag**

apoorvctf{th3_c0m1cs_l13_1n_th3_PLTE}

**Notes / forensic tips**

- Always check PNG textual chunks (`tEXt`, `iTXt`, `zTXt`) for hints.
- `PLTE` is an easy place to hide ASCII because it's structured and often not visually inspected.
- Use tools such as `pngcheck`, `zsteg`, `binwalk`, and `StegSolve` for automated detection and manual inspection of bitplanes and palette.

**Artifacts**

Kept in this folder:

- `challenge.png`
- `plte_reds.bin`
- `red_channel.png`

---

If you want, I can also compress the three artifacts into a zip, or produce a short slide-style README summarizing the steps for a CTF writeup submission.
