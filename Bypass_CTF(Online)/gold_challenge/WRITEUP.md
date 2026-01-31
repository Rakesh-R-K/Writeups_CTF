#  Bypass CTF Writeup : Gold Challenge 

## Challenge Description
> The challenge is contained within the Medallion_of_Cortez.bmp file.
> 
> This cursed coin holds more than just gold.
> 
> They say the greed of those who plundered it left a stain upon its very soul—a fractured image, visible only to those who can peel back the layers of light.
> 
> To lift the curse, you must first reassemble the key. Once the key is whole, its message will grant you the power to unlock the true treasure within.
> 
> Beware, for the final step is guarded, and only the words revealed by the light will let you pass.

## Challenge Overview
This is a multi-layered steganography challenge involving:
- LSB (Least Significant Bit) steganography
- QR code extraction and decoding
- Password-protected steghide extraction

We're given a single file: `Medallion_of_Cortez.bmp` - an image of an Aztec gold medallion with a skull design.

## Analysis

### Understanding the Clues

The challenge description gives us important hints:
- **"peel back the layers of light"** → LSB extraction from image data
- **"reassemble the key"** → Extract and decode a hidden QR code
- **"its message will grant you the power"** → The QR code contains a password
- **"guarded"** → Steghide password protection
- **"words revealed by the light"** → The password from the QR code unlocks the final treasure

### Step 1: LSB Extraction

LSB steganography hides data in the least significant bit of pixel values. Since the challenge mentions "layers of light," we need to extract these bits to reveal hidden information.

The BMP image uses RGB channels. We focus on the **red channel** and extract the LSB from each pixel:

```python
from PIL import Image
import numpy as np

# Load the image
img = Image.open("Medallion_of_Cortez.bmp")
img_array = np.array(img)

# Extract red channel
red_channel = img_array[:, :, 0]

# Get LSB and amplify to visible range (0 or 255)
red_lsb = (red_channel & 1) * 255

# Create image from LSB
lsb_image = Image.fromarray(red_lsb.astype(np.uint8))
lsb_image.save("qr_code.png")
```

This extracts the least significant bit from each red pixel value using the bitwise AND operation (`& 1`), then multiplies by 255 to make it visible.

### Step 2: Decode the QR Code

The LSB extraction reveals a hidden QR code! We can decode it using the `pyzbar` library:

```python
from pyzbar.pyzbar import decode

decoded = decode(lsb_image)
password = decoded[0].data.decode('utf-8')
print(f"Password: {password}")
```

**Result:** `SunlightRevealsAll`

This password is beautifully thematic - "sunlight" referring to the "layers of light" mentioned in the challenge description!

### Step 3: Steghide Extraction

Now that we have the password, we can use `steghide` to extract the hidden data from the original BMP file:

```bash
steghide extract -sf Medallion_of_Cortez.bmp -p SunlightRevealsAll
```

This extracts a file called `treasure.txt` containing the flag!

## Complete Solution Script

```python
#!/usr/bin/env python3
"""
Solution for Medallion_of_Cortez CTF Challenge
Extracts hidden QR code from LSB and uses it to unlock steghide data
"""

from PIL import Image
import numpy as np
from pyzbar.pyzbar import decode
import subprocess

print("Solving Medallion of Cortez CTF Challenge...\n")

# Step 1: Extract LSB from BMP
print("[1] Extracting LSB from red channel...")
img = Image.open("Medallion_of_Cortez.bmp")
img_array = np.array(img)
red_channel = img_array[:, :, 0]
red_lsb = (red_channel & 1) * 255
lsb_image = Image.fromarray(red_lsb.astype(np.uint8))

# Step 2: Decode QR code
print("[2] Decoding QR code from LSB...")
decoded = decode(lsb_image)
if not decoded:
    print("No QR code found!")
    exit(1)

password = decoded[0].data.decode('utf-8')
print(f"[3] Found password: {password}")

# Step 3: Extract hidden data with steghide
print("[4] Extracting hidden data with steghide...")
result = subprocess.run(
    ["steghide", "extract", "-sf", "Medallion_of_Cortez.bmp", "-p", password, "-f"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print(f"[5] Extraction successful!\n")
    # Read and display the flag
    with open("treasure.txt", "r") as f:
        flag = f.read().strip()
        print("="*50)
        print(f"FLAG: {flag}")
        print("="*50)
else:
    print(f"Steghide failed: {result.stderr}")
```

### Execution Output

```
Solving Medallion of Cortez CTF Challenge...

[1] Extracting LSB from red channel...
[2] Decoding QR code from LSB...
[3] Found password: SunlightRevealsAll
[4] Extracting hidden data with steghide...
[5] Extraction successful!

==================================================
FLAG: BYPASS_CTF{Aztec_Gold_Curse_Lifted}
==================================================
```

## Key Techniques Used

### 1. **LSB Steganography**
- Hides data in the least significant bit of pixel values
- Virtually invisible to the naked eye
- Extracted using bitwise operations: `pixel_value & 1`

### 2. **QR Code Steganography**
- The LSB extraction revealed a complete QR code
- QR codes are robust even when embedded in noisy data
- Decoded using `pyzbar` library

### 3. **Steghide**
- Popular steganography tool for hiding files within images
- Supports password protection
- The password was cleverly hidden in the QR code within the LSB layer

## Tools Required

- **Python 3** with libraries:
  - `PIL` (Pillow) - Image processing
  - `numpy` - Array operations
  - `pyzbar` - QR code decoding
- **Steghide** - File extraction tool

### Installation

```bash
# Python libraries
pip install pillow numpy pyzbar

# Steghide (Linux/WSL)
sudo apt-get install steghide

# On Windows, use WSL or download steghide binary
```

## Flag
```
BYPASS_CTF{Aztec_Gold_Curse_Lifted}
```

## Learning Points

1. **Multi-Layer Steganography**: This challenge demonstrates that steganography can have multiple layers - LSB hiding a QR code, which contains a password for steghide.

2. **Channel Selection**: Not all steganography uses all channels. Here, only the red channel's LSB was used. Always test individual RGB channels separately.

3. **QR Code Robustness**: QR codes have built-in error correction, making them ideal for embedding in potentially noisy environments like LSB data.

4. **Thematic Passwords**: The password "SunlightRevealsAll" ties beautifully to the challenge description's mention of "light" and "layers of light."

5. **Tool Combination**: Modern CTF challenges often require combining multiple tools (image processing, QR decoding, steghide) to solve.


