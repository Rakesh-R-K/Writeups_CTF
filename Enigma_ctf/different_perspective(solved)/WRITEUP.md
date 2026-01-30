# Challenge: Different Perspective

## Challenge Description
This challenge involved analyzing an image that appeared to contain hidden information requiring a different approach to reveal.

**Given:** `chall.png` (image file)

## Solution

### Initial Analysis
The challenge image `chall.png` appeared to be a noisy/static RGB image. At first glance, no clear pattern or text was visible. This suggested that the flag was hidden within the pixel data itself, requiring some form of channel manipulation or mathematical transformation.

### Discovery Process

#### Step 1: XOR Analysis
Initial investigation involved performing XOR operations on the RGB channels. This revealed an intermediate image (`flag_xor.png`) that contained a crucial hint - the formula:

```
||R-G|-B|
```

This formula indicated that we needed to:
1. Take the absolute difference between Red and Green channels: `|R-G|`
2. Take the absolute difference between that result and the Blue channel: `||R-G|-B|`

#### Step 2: Applying the Formula
The formula represents a nested absolute difference operation:
- **Inner operation**: `|R - G|` - finds the absolute difference between Red and Green channels
- **Outer operation**: `|result - B|` - finds the absolute difference between the inner result and Blue channel

This type of transformation can reveal hidden patterns where information is encoded in the subtle differences between color channels.

### Implementation

```python
from PIL import Image
import numpy as np

def solve_with_formula(img_path):
    # Open the image
    img = Image.open(img_path).convert('RGB')
    
    # Convert to numpy array for easier channel manipulation
    img_array = np.array(img)
    
    # Extract R, G, B channels
    R = img_array[:, :, 0].astype(np.int16)
    G = img_array[:, :, 1].astype(np.int16)
    B = img_array[:, :, 2].astype(np.int16)
    
    # Apply the formula: ||R-G|-B|
    step1 = np.abs(R - G)  # |R-G|
    step2 = np.abs(step1 - B)  # ||R-G|-B|
    
    # Clip values to 0-255 range
    result = np.clip(step2, 0, 255).astype(np.uint8)
    
    # Create grayscale image from result
    result_img = Image.fromarray(result, mode='L')
    result_img.save('flag_formula.png')
    
    print("[+] Applied formula ||R-G|-B|")
    print("[+] Created flag_formula.png")
    print("[+] Check this file for your flag!")

# Apply the formula on the challenge image
solve_with_formula('chall.png')
```

### Result
Applying the formula to `chall.png` produced `flag_formula.png`, which clearly displayed the flag text:

```
enigmaCTF26{sp0tted_th3_d1ff3rence_a89Hf}
```

## Flag
`enigmaCTF26{sp0tted_th3_d1ff3rence_a89Hf}`

## Key Takeaways
- Information can be hidden in the subtle differences between RGB color channels
- Nested absolute difference operations can reveal patterns invisible to the naked eye
- The challenge name "different_perspective" hints at viewing the image data differently (through mathematical transformations)
- The flag text "sp0tted_th3_d1ff3rence" references the method used to solve it
- Using `numpy` for channel-level image manipulation is more efficient than pixel-by-pixel operations
