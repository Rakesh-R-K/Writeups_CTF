# Challenge: Raw Data Recovery

## Challenge Description
This file was extracted from a system that crashed mid-transfer. Nothing appears to be missing, but whatever produced it didn't wrap the data the way our tools expect.

**Given:** `chall.raw` (103 bytes)

## Solution

### Initial Analysis
The challenge file `chall.raw` contained 103 bytes of binary data. The hint "didn't wrap the data the way our tools expect" suggested that the data format was missing some expected wrapper or header.

### Identifying the Format
The first bytes of the file were:
```
E3 B2 B5 B5 55 08 8E 0C 0E 71 F5 55 70 F1 74 74 ...
```

This didn't match any common file signatures (PNG, JPEG, ZIP, etc.). However, the hint about "wrapping" suggested compression-related formats.

### The Solution
Compressed data formats like zlib typically have two components:
1. **zlib format**: Includes a 2-byte header, compressed data, and optional checksum
2. **raw DEFLATE**: Just the compressed data stream without headers

The challenge file contained raw DEFLATE compressed data without the zlib wrapper. Standard decompression tools expect the zlib wrapper, which is why they fail.

### Decompression
Using Python's zlib library with the `-zlib.MAX_WBITS` parameter allows decompression of raw DEFLATE streams:

```python
import zlib

with open('chall.raw', 'rb') as f:
    data = f.read()

# Decompress raw DEFLATE (no zlib header)
decompressed = zlib.decompress(data, -zlib.MAX_WBITS)
print(decompressed.decode('utf-8'))
```

### Result
The decompressed output revealed:
```
=== SYSTEM DIAGNOSTIC ===
Status: OK
Logs attached below.

enigmaCTF26{r4w_d3fla7e_aj193n51g}
=== END ===
```

## Flag
`enigmaCTF26{r4w_d3fla7e_aj193n51g}`

## Key Takeaways
- Raw DEFLATE compression is just the compressed data stream without zlib/gzip wrappers
- The `-zlib.MAX_WBITS` parameter in Python's zlib.decompress() handles raw DEFLATE
- The challenge name "r4w_d3fla7e" in the flag is a hint about the solution method
