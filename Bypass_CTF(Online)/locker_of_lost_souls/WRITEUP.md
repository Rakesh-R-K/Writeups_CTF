# Bypass CTF Challenge Writeup : Locker of Lost Souls 

## Challenge Description
> They say that to be locked away in Davy Jones' Locker is to be erased from the world of the living, a fate worse than death. One of our divers recovered this image from the wreck of the *Sea Serpent*. The ship's log spoke of a curse, a vision that could only be understood by those who could 'see beyond the veil'. The image seems to be just a picture of an old locker on the seabed, covered in barnacles, but the log claims it holds the key to escape the Locker itself. Standard instruments find nothing. Maybe the old captain was just mad from the pressure, or maybe... you're just not looking at it the right way.

## Challenge Overview

This is a steganography challenge that provides an image file (`davy_jones_locker.png`) containing a hidden message. The image appears to be random colorful noise or static, but the challenge description contains crucial hints about the solution method.

## Analysis

### Understanding the Clues

The challenge description is rich with hints:
- **"see beyond the veil"** → Look deeper than the surface, see hidden layers
- **"a vision that could only be understood"** → Visual technique required
- **"Standard instruments find nothing"** → Common stego tools (strings, binwalk, exiftool) won't work
- **"you're just not looking at it the right way"** → The KEY hint! You need to look at it differently

These clues all point to a specific type of visual steganography where the viewing method itself reveals the hidden message.

### Initial Investigation

Running standard steganography tools yields nothing:

```bash
# Check metadata
exiftool davy_jones_locker.png
# Nothing unusual

# Check for embedded files
binwalk davy_jones_locker.png
# No hidden files

# Check strings
strings davy_jones_locker.png
# No obvious text

# Try zsteg/stegsolve for LSB
zsteg davy_jones_locker.png
# Nothing found
```

The image appears to be pure colorful noise or static—random-looking pixels with no apparent pattern to the naked eye.

### The Key Insight: Stereogram/Autostereogram

The phrase **"you're just not looking at it the right way"** is the crucial hint. This suggests the image needs to be viewed with a special technique.

The image is actually a **stereogram** (also known as an autostereogram or "Magic Eye" image). These are images that encode 3D depth information or hidden messages through repeating patterns. When viewed correctly, either by:
- **Cross-eyed viewing**: Crossing your eyes to merge two points
- **Parallel viewing**: Looking "through" the image
- **Automated solving**: Using software to extract the depth map

The hidden 3D shape or text becomes visible!

## Solution

### Method 1: Automated Stereogram Solver (Recommended)

Since manually viewing stereograms can be difficult and time-consuming, we can use an online stereogram solver:

**Tool**: [Stereogram Solver by Jérémy Piellard](https://piellardj.github.io/stereogram-solver/)

#### Steps:

1. **Open the stereogram solver website**:
   ```
   https://piellardj.github.io/stereogram-solver/
   ```

2. **Upload the image**:
   - Click the upload button or drag `davy_jones_locker.png` into the browser
   - The tool automatically processes the image

3. **View the result**:
   - The solver extracts the hidden depth map
   - The 3D message becomes visible as raised/lowered text
   - The flag is revealed: **BYPASS_CTF{D35D_M4IN5_CH3ST}**

### Method 2: Manual Viewing (Traditional Method)

For those who want to try the traditional "Magic Eye" technique:

1. **Position the image** at a comfortable viewing distance
2. **Relax your eyes** and try to look "through" the screen
3. **Cross your eyes slightly** or use parallel viewing
4. **Wait for the 3D image to emerge** - you should see text floating above or below the background
5. **Read the revealed message** - it should show the flag

**Tip**: This takes practice! Some people find it easier than others.

### Method 3: Programmatic Approach

You can also write a Python script to decode stereograms using depth map extraction:

```python
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def solve_stereogram(image_path):
    """
    Extract depth map from a stereogram by analyzing pattern repetition
    """
    img = Image.open(image_path)
    img_array = np.array(img)
    
    height, width = img_array.shape[:2]
    
    # Create depth map
    depth_map = np.zeros((height, width))
    
    # For each row, find repeating pattern
    for y in range(height):
        row = img_array[y]
        
        # Search for pattern repetition
        for shift in range(20, width // 2):
            # Compare pixels with shifted version
            similarity = 0
            for x in range(width - shift):
                if np.allclose(row[x], row[x + shift], atol=10):
                    similarity += 1
            
            # If high similarity, this is the pattern shift
            if similarity > width * 0.8:
                for x in range(width - shift):
                    if not np.allclose(row[x], row[x + shift], atol=10):
                        depth_map[y, x] = shift
                break
    
    # Visualize depth map
    plt.imshow(depth_map, cmap='gray')
    plt.title('Stereogram Depth Map (Hidden Message)')
    plt.axis('off')
    plt.show()
    
    return depth_map

# Use it
depth_map = solve_stereogram('davy_jones_locker.png')
```

This extracts the depth map, where the hidden text appears as different shades.

## Flag
```
BYPASS_CTF{D35D_M4IN5_CH3ST}
```

The flag cleverly plays on words : Treasure chest, or Jones' famous "Dead Man's Chest"
- **D35D** 
- **M4IN5** 
- **CH3ST**  

Alternative interpretation: "DEAd MAINS CHEST" could refer to the deep ocean ("mains" as in ocean currents) and a chest/locker.

## How Stereograms Work

### The Science Behind It

Stereograms exploit how human vision perceives depth:

1. **Pattern Repetition**: The image contains a repeating pattern
2. **Depth Encoding**: Shifts in the pattern encode depth information
3. **Binocular Fusion**: When your eyes converge incorrectly, the shifted patterns merge
4. **3D Perception**: Your brain interprets the shift as depth, creating a 3D image

### Mathematical Principle

For a stereogram with pattern width `W` and desired depth `d`:
- Points at depth `d` are rendered with a horizontal shift of `W + d`
- When viewed with eye separation `E`, the perceived depth is:
  ```
  perceived_depth = (E × d) / (W - d)
  ```

### Creating Text in Stereograms

To hide text:
1. Create a depth map where text is "raised" (lighter) or "sunken" (darker)
2. Generate a random pattern
3. For each pixel, shift the pattern based on the depth value
4. The result looks like random noise but encodes 3D structure

## Key Techniques & Learning Points

### 1. **Stereogram Steganography**
- A unique form of visual steganography
- Data is hidden in plain sight through depth encoding
- Requires special viewing technique or solver to decode

### 2. **Challenge Design**
- Excellent use of thematic hints ("see beyond the veil")
- "Not looking at it the right way" directly points to the solution
- Frustrates common stego tools, forcing creative thinking

### 3. **Tool Awareness**
- Standard tools (binwalk, strings, exiftool) are useless here
- Specialized tools exist for specific steganography types
- Sometimes the image format itself is the message

### 4. **Historical Context**
- Stereograms became popular in the 1990s with "Magic Eye" books
- Based on older stereoscopic 3D viewing techniques
- Modern applications include captchas and artistic images

## Tools & Resources

### Online Solvers
- **Stereogram Solver**: https://piellardj.github.io/stereogram-solver/
- **Hidden 3D**: Various apps and websites for viewing stereograms
