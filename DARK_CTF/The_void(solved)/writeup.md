# CrackOn Forensics Writeup - "void"

## Challenge Summary
The challenge provides a single archive containing a raw disk image. The prompt hints at hidden data:
- "space between the sectors"
- "what was left behind at the edge of the universe"
- "the vault is locked"

These clues indicate:
1. A likely encrypted container (the "vault").
2. Key material hidden in non-obvious disk regions (especially near the end of the image).

## Files Provided
- `quest.zip`
- extracted: `quest/quest.img`

## Initial Triage
After extraction, the image was inspected for structure:
- MBR partition table present
- Two Linux partitions:
  - partition 1: 100 MB
  - partition 2: 399 MB

Partition carving showed:
- `p1.img` is all zeroes (decoy/noise)
- `p2.img` is a valid LUKS2 container

## Key Observations
1. LUKS metadata in `p2.img` shows:
   - keyslot type: luks2
   - AF splitter: luks1, stripes=4000, hash=sha256
   - KDF: argon2id
2. Unallocated regions were checked.
3. The final 4096 bytes at the end of `quest.img` were non-zero and highly suspicious.

This directly matched the clue: "left behind at the edge of the universe".

## Solver Approach
Because root-level tooling (`cryptsetup`) was not available in this environment, we solved in pure Python:

### Script 1: `quest/extract/solve_luks.py`
Purpose:
- Parse LUKS2 JSON metadata.
- Reproduce key derivation (Argon2id).
- Decrypt keyslot area with AES-XTS.
- Reconstruct volume key via AF merge.
- Validate reconstructed key against LUKS digest.

Key result:
- Candidate `raw:last_4096_bytes` (from the tail of `quest.img`) validated successfully.
- Recovered key material saved as `quest/extract/recovered_key.bin`.

### Script 2: `quest/extract/decrypt_and_find_flag.py`
Purpose:
- Use recovered key material to derive/decrypt full payload area.
- Determine correct XTS tweak base mode.
- Decrypt payload into `quest/extract/payload.dec`.
- Search plaintext for `CrackOn{...}` pattern.

Key result:
- Payload decrypted successfully.
- Flag pattern found directly in plaintext.

## Final Flag
`CrackOn{Th1ngs_fr0m_de3p_in_t1me_1983}`

## Reproduction Commands
From workspace root:

```bash
# 1) Extract challenge
powershell -Command "Expand-Archive -LiteralPath quest.zip -DestinationPath quest -Force"

# 2) Run key recovery
wsl bash -lc "python3 quest/extract/solve_luks.py"

# 3) Decrypt payload and extract flag
wsl bash -lc "python3 quest/extract/decrypt_and_find_flag.py"
```

## Why This Works (Hint Mapping)
- "Vault is locked" -> LUKS2 encrypted partition.
- "Space between the sectors" -> hidden-forensics mindset, not normal file paths.
- "Edge of the universe" -> tail-end bytes of the full disk image.
- "Void is not empty" -> seemingly empty image still contains critical key material.

## Artifacts Generated During Solve
- `quest/extract/p1.img`
- `quest/extract/p2.img`
- `quest/extract/solve_luks.py`
- `quest/extract/recovered_key.bin`
- `quest/extract/decrypt_and_find_flag.py`
- `quest/extract/payload.dec`
