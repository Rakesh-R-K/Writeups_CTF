# Marlboro (Smoke) — Writeup

## Summary

- Challenge: recover hidden flag from `Marlboro.jpg`.
- Final flag: `BITSCTF{d4mn_y0ur_r34lly_w3n7_7h47_d33p}`

## High-level flow

1. Carve files from the provided JPEG.
2. Inspect extracted `smoke.png` for metadata and text chunks.
3. Extract LSB data from `smoke.png` — it contains instructions and a 32-byte XOR key (hex).
4. XOR-decrypt `encrypted.bin` with the recovered key (bytewise key[i % 32]).
5. The decrypted blob is a Malbolge program; interpret it to get the flag.

## Files and artifacts

- `Marlboro.jpg` — original challenge file.
- `output/zip/00007332/smoke.png` — extracted PNG with hidden data.
- `output/zip/00007332/encrypted.bin` — encrypted payload.
- `output/zip/00007332/lsb/lsb_012.bin` — LSB-extracted text containing the XOR key and instructions.
- `output/zip/00007332/decrypted.bin` — result of XOR-decrypting `encrypted.bin`.
- `scripts/` — helpful scripts used to automate extraction and execution.

## Key findings

- `smoke.png` contains a `tEXt` chunk (Author) hint and large text content.
- LSB extraction (channels R+G+B) produced `lsb_012.bin` which contained plain text:

```
# Marlboro Decryption Key.
Format: 32-byte XOR key in hexadecimal.
KEY=c7027f5fdeb20dc7308ad4a6999a8a3e069cb5c8111d56904641cd344593b657
Usage: XOR each byte of encrypted.bin with key[i % 32]
```

## Reproduction steps (commands)

1) Carve files from the JPEG (if you don't already have `output/`):

```bash
foremost -i Marlboro.jpg -o output
```

2) Inspect PNG metadata and text chunks:

```bash
exiftool output/zip/00007332/smoke.png
python3 scripts/extract_png_text.py    # parses tEXt/iTXt/zTXt
```

3) Extract LSBs (example script used: `scripts/lsb_extract.py`):

```bash
python3 scripts/lsb_extract.py
# produces output/zip/00007332/lsb/lsb_012.bin
```

4) Read key from `lsb_012.bin` (or use the one above), then XOR-decrypt:

```python
# decrypt.py (snippet)
key = bytes.fromhex('c7027f5fdeb20dc7308ad4a6999a8a3e069cb5c8111d56904641cd344593b657')
enc = open('output/zip/00007332/encrypted.bin','rb').read()
plain = bytes([enc[i] ^ key[i % len(key)] for i in range(len(enc))])
open('output/zip/00007332/decrypted.bin','wb').write(plain)
```

5) Inspect `decrypted.bin` — it includes Malbolge source. Run it with a Malbolge interpreter.

I used the Python `malbolge` package and the helper `scripts/run_mal.py` to interpret the program:

```bash
pip3 install --user malbolge
python3 scripts/run_mal.py
# prints: BITSCTF{d4mn_y0ur_r34lly_w3n7_7h47_d33p}
```

## Additional notes

- The challenge used multiple steg layers: visible metadata hint → LSB embedded instructions and key → XOR encryption → esoteric-language payload (Malbolge).
- All helper scripts used during analysis are in `scripts/` for reproducibility.
- If you want a fully polished Markdown tutorial (with images or annotated outputs), I can expand this into a public writeup-ready document.

## Scripts created / used (paths)

- `scripts/find_pk_abs.py` — find `PK` offsets inside files.
- `scripts/carve_zips.py` — carve PK-starting segments (attempts; not strictly required once LSB path is used).
- `scripts/extract_png_text.py` — parse PNG chunks and print `tEXt`/`iTXt`/`zTXt` entries.
- `scripts/lsb_extract.py` — extract LSBs from RGB channels and write candidate binaries (used to obtain `lsb_012.bin`).
- `scripts/run_mal.py` — load `decrypted.bin`, isolate Malbolge source and interpret it via `malbolge` Python package.

## Flag

`BITSCTF{d4mn_y0ur_r34lly_w3n7_7h47_d33p}`

-- End of writeup
