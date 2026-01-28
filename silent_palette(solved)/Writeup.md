# Challenge: Silent Palette

## Challenge Description
The challenge provides a PNG image (`chall.png`) that appears to be random colorful noise. The title "Silent Palette" suggests that data might be hidden within the image's color palette or indexing.

**Given:** `chall.png` (PNG image)

## Solution

### Initial Analysis
Upon opening the file, the image looks like high-entropy noise, a common sign of either encrypted data or LSB steganography.

#### Initial Checks
- **File Command**: Confirmed it is a standard PNG image
- **Strings**: Running `strings chall.png` yielded no obvious flag or hidden text
- **ExifTool**: Metadata revealed nothing unusual
- **Palette Check**: Since the title mentioned "Palette," the first check was for a PLTE chunk. However, the image was saved in RGB mode rather than Indexed (P) mode, meaning there was no global palette to exploit

### The Vulnerability: LSB Steganography
The data was hidden using **Least Significant Bit (LSB) Steganography**.

In this technique, the least significant bit of the Red, Green, and Blue color channels for each pixel is modified to store bits of the hidden message. Because the change in color value is only 1 (e.g., from 255 to 254), it is invisible to the human eye, but easily extractable via a script.

### Solution Implementation

Using Python and the Pillow library, we can iterate through the pixels, extract the LSB of each channel, and group them into bytes to reconstruct the ASCII string.

```python
from PIL import Image

def extract_lsb(image_path):
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size

    extracted_bin = ""
    for y in range(height):
        for x in range(width):
            # Extract RGB values
            r, g, b = pixels[x, y][:3]
            # Take the LSB (lowest bit) of each channel
            extracted_bin += str(r & 1)
            extracted_bin += str(g & 1)
            extracted_bin += str(b & 1)

    # Convert binary chunks of 8 into characters
    chars = []
    for i in range(0, len(extracted_bin), 8):
        byte = extracted_bin[i:i+8]
        chars.append(chr(int(byte, 2)))
    
    return "".join(chars)

# Run extraction
data = extract_lsb('chall.png')
print(data[:100]) # Print first 100 chars to find the flag
```

### How It Works

1. **Open the image** and access pixel data
2. **Iterate through each pixel** in row-major order (left to right, top to bottom)
3. **Extract the LSB** from each R, G, B channel using bitwise AND operation (`& 1`)
4. **Concatenate all bits** into a binary string
5. **Group bits into bytes** (8 bits each) and convert to ASCII characters
6. **Search for the flag** pattern in the extracted text

### Result
Running the extraction script reveals the hidden message embedded in the image noise:

```
enigmaCTF26{L$B_H1D1NG_1N_PL@1N_$1GHT!}
```

## Flag
`enigmaCTF26{L$B_H1D1NG_1N_PL@1N_$1GHT!}`

## Key Takeaways
- **Don't let the title mislead you**: "Silent Palette" was designed to make solvers spend time analyzing PNG chunks and palette structures, while the real flag was hidden using the most common steganography technique
- **LSB steganography is still effective**: Despite being a well-known technique, it remains invisible to casual observation
- **Check multiple approaches**: Start with the most common steganography methods (LSB, metadata, strings) before diving into more complex analysis
- **The flag "L$B_H1D1NG_1N_PL@1N_$1GHT"** is a clever reference to the technique used - LSB hiding in plain sight
- **Tool recommendations**: For quick LSB extraction, tools like `zsteg`, `stegsolve`, or custom Python scripts with Pillow are essential

## Tools & Libraries Used
- Python with Pillow (PIL) library
- Image analysis and pixel manipulation
- Bitwise operations for LSB extraction