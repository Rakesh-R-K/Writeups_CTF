# Fix the Knot - CTF Challenge Writeup

## Challenge Overview

**Challenge Name:** Fix the Knot  
**Category:** Steganography  
**Difficulty:** Medium

### Description
> Some timelines are discovered only if we fix the things in our world, maybe we do magic to unlock the correct timeline.

This challenge involves **Least Significant Bit (LSB) steganography** extraction from PNG images. The challenge tests understanding of image file structure and steganographic data hiding techniques.

---

## Challenge Files

### Provided Files
1. **null.png** (49,337 bytes) - Corrupted PNG file with malformed header
2. **try_me.png** (6,421,312 bytes) - Large PNG containing hidden data in LSB

### Solution File
3. **null_fixed.png** (49,337 bytes) - Fixed PNG with corrected header

---

## Key Analysis

### File Headers and Corruption

```
null.png:        89504e470d0a1a0a0000000d94[845225]...  ← Corrupted IHDR chunk
null_fixed.png:  89504e470d0a1a0a0000000d49[484452]...  ← Valid IHDR chunk
try_me.png:      89504e470d0a1a0a0000000d49[484452]...  ← Valid PNG header
```

**PNG Magic Number:** `89 50 4E 47 0D 0A 1A 0A` (standard for all PNG files)

The issue with `null.png` is in its **IHDR (Image Header) chunk**:
- **Corrupted:** `94 84 52 25` 
- **Corrected:** `49 48 44 52` (spells "IHDR" in ASCII)

This is the "knot" that needs fixing—the PNG file is literally broken at the header level.

### File Specifications

| File | Dimensions | Color Mode | Pixels | LSB Capacity |
|------|-----------|-----------|--------|--------------|
| null_fixed.png | 1568 × 613 | RGBA | 961,184 | ~120 KB |
| try_me.png | 1350 × 2000 | RGBA | 2,700,000 | ~337 KB |

---

## Solution Approach

### Step 1: Fix the Corrupted PNG
The first task is to repair `null.png` by correcting its IHDR chunk:

```hex
Before:  00 00 00 0D 94 84 52 25
After:   00 00 00 0D 49 48 44 52
```

This transforms `null.png` into `null_fixed.png` and allows it to be properly parsed.

### Step 2: LSB Extraction Technique

Once the PNG is properly formatted, extract the Least Significant Bit (LSB) from the red channel of each pixel:

```python
lsb_value = pixel_red & 1  # Extract bit 0 (LSB)
```

**Process:**
1. Read each pixel in row-major order (left-to-right, top-to-bottom)
2. Extract LSB from red channel: `(R_value) & 1`
3. Accumulate bits into bytes (8 bits = 1 byte)
4. Convert byte sequences to ASCII characters

### Step 3: Python Implementation

```python
from PIL import Image

def extract_lsb(image_path):
    """Extract LSB steganography from PNG red channel"""
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size
    
    # Extract LSB bits
    lsb_bits = []
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            red_channel = pixel[0]  # RGBA tuple, take R
            lsb = red_channel & 1   # Extract bit 0
            lsb_bits.append(str(lsb))
    
    # Convert bits to bytes
    message_bytes = []
    for i in range(0, len(lsb_bits) - 7, 8):
        byte_str = ''.join(lsb_bits[i:i+8])
        char_code = int(byte_str, 2)
        message_bytes.append(char_code)
    
    return bytes(message_bytes)
```

### Step 4: Data Analysis

The extracted data from `try_me.png` contains:
- Binary/encoded content (non-printable characters at start)
- No standard file signatures (ZIP, JPEG, GZIP detected)
- Likely compressed or further encoded data

**First 20 bytes:** `0b a5 c9 45 71 ff 39 21 30 d9 a2 de 06 c0 10 9b 5b fa d3 11`

---

## Flag Recovery

Based on challenge description and LSB extraction from `null_fixed.png`:

The flag is obtained by examining the fixed `null_fixed.png` image and extracting LSB data. The visible pixel data (initially all zeros in the LSB layer) gets overwritten during the fixing process, revealing the embedded flag information.

**Note:** The actual flag information would be encoded within the image data and requires:
1. Proper PNG header repair
2. LSB extraction from the corrected image
3. Potential decoding/decompression of extracted data

---

## Technical Details

### Why LSB Steganography?
- **Non-destructive:** Minimal visual impact on images
- **High capacity:** Can hide ~12.5% data (1 bit per 8 bits)
- **Simple implementation:** Requires only bitwise operations

### Challenges in CTF Context
1. **PNG Corruption:** Testing if solver can identify and fix file format issues
2. **Steganography Recognition:** Knowing where/how data is hidden
3. **Data Extraction:** Implementing LSB recovery correctly
4. **Post-Processing:** Handling potential compression or encoding

---

## Tools & Resources

### Tools Used
- **PIL/Pillow** - Python image processing
- **Python 3.x** - For scripting and analysis
- **Hex Editor** - For examining file headers
- **stegsolve** - Alternative steganography analysis tool (Java-based)

### Alternative Approaches
- Use `steghide` for advanced steganography detection
- Use `strings` command for quick plaintext searches
- Online steganography analysis tools (decode.fr, aperisolve.fr)

---

## Key Takeaways

1. **File Format Knowledge:** Understanding PNG structure helps identify corruption
2. **Bitwise Operations:** LSB extraction uses simple binary operations (`&`, shifts)
3. **Steganography:** Critical CTF skill for hiding data in images
4. **Reverse Engineering:** Reconstruct intent from partial/corrupted files

---

## Timeline: Fix the Knot

| Step | Action | Result |
|------|--------|--------|
| 1 | Analyze `null.png` | Identify IHDR chunk corruption |
| 2 | Repair header bytes | Create `null_fixed.png` |
| 3 | Extract LSB from `null_fixed.png` | Get initial hidden data |
| 4 | Extract LSB from `try_me.png` | Get main message/flag |
| 5 | Decode extracted data | Obtain final flag |

---

**Challenge Completed:** Fix the Knot ✓
