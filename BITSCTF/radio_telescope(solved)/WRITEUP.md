**Radio Telescope — CTF Writeup**

- **Challenge:** Given a raw numeric log from a radio telescope (`rt7-log.txt`), find the hidden flag.

**Summary:**
- The log contains 10,000 floating-point samples recorded from the RT-7 feed. Most samples are regular noise, but there are repeating, tightly clustered runs of values whose integer parts correspond to ASCII codes. By detecting those clusters and mapping their rounded integer values to characters we recover a readable message containing the flag.

**Observations:**
- File: [rt7-log.txt](rt7-log.txt)
- Many values are ordinary random/noisy floats, but there are repeated short runs where consecutive samples vary by less than ~1.0 and cluster tightly around a particular value (e.g., ~67.x, ~84.x, etc.).
- Those clusters looked like intentionally encoded ASCII when rounded to integers.

**Approach:**
1. Parse the log into floats and scan for contiguous runs where consecutive-sample differences are small (chosen threshold: 1.0). These indicate a steady value over many samples.
2. For each sufficiently long cluster, compute the cluster mean (or round each value) and interpret the integer part as an ASCII code.
3. Concatenate the characters from successive clusters to form the hidden message.

**Scripts used (in repo):**
- [analyze_log.py](analyze_log.py) — exploratory script used to inspect fractions, common values, and to locate repeating clusters.
- [extract_flag.py](extract_flag.py) — final extraction script that groups samples into clusters (diff < 1.0) and maps cluster means to ASCII characters, producing `extracted_message.txt`.

**Key command to reproduce:**
```bash
python "c:/Users/Rakesh R K/Downloads/bitsctf/radio_telescope/analyze_log.py"
python "c:/Users/Rakesh R K/Downloads/bitsctf/radio_telescope/extract_flag.py"
```

**Why this works:**
- Random noise produces large sample-to-sample changes; an intentional encoded symbol was left as a short segment of near-constant samples. Rounding that near-constant value yields a single integer per cluster, which maps to a printable ASCII character.

**Result / Flag:**
- During extraction the message was reconstructed and the flag was found as:

CTF{s1l3nc3_1n_th3_n01s3}

**Artifacts:**
- Extraction output: [extracted_message.txt](extracted_message.txt)
- Analysis outputs: [analysis_out.txt](analysis_out.txt)

**Notes & tips:**
- Thresholds (cluster gap < 1.0, minimum cluster length) were pragmatic choices for this data; if the encoder used different smoothing, adjust the threshold accordingly.
- If a cluster mean rounds to a non-printable code, try using the mode or truncation instead of rounding, or check neighboring clusters for off-by-one shifts.

If you want, I can:
- Add a cleaned, commented `WRITEUP.md` section describing the exact parameter choices and show the relevant slices of `rt7-log.txt` that map to each character.
- Commit these files or create a short notebook that visualizes the clusters.
