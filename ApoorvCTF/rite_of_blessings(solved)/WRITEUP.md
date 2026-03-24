# Rite of Blessings - CTF Writeup

**Challenge Name:** Rite of Blessings  
**Category:** Cryptography / Image Processing / Forensics  
**Flag:** `apoorvctf{1_40_35}`

## Challenge Description

> Glen's Enigmatic Module stands sealed behind a sacred gate, permitting passage only to the blessed ones who can perform the ritual of the gate upon the grid-formed relics that govern the chromatic layers within Glen's image-recognition rite.

## Files Provided

```
files/
├── process_scalars.py
├── retrieve_kernel.py
└── images/
    ├── flower.jpg
    ├── flower_processed.jpg
    └── flower_processed.npy
```

## Solution

### Step 1: Understanding the Scripts

**retrieve_kernel.py**: This script uses least squares regression to recover convolution kernels that were applied to transform an input image into an output image. It processes each RGB channel separately.

**process_scalars.py**: Takes three integer arguments and generates a flag in the format `apoorvctf{d1_d2_d3}`.

### Step 2: Recover the Convolution Kernels

Run the kernel recovery script on the provided images:

```bash
python retrieve_kernel.py flower.jpg flower_processed
```

**Output:**
```
Kernel for the Red layer:
[[ 1 -1  0]
 [-1  5 -1]
 [ 2 -1  0]]

Kernel for the Green layer:
[[ 1  2  1]
 [-1  8 -1]
 [-3 -1  1]]

Kernel for the Blue layer:
[[-1 -4  1]
 [ 1  4  4]
 [-1  3  1]]
```

### Step 3: Decode the Cryptic Clue

The challenge description contains several key hints:
- **"sacred gate"** → A special mathematical operation
- **"ritual of the gate"** → The operation to perform
- **"grid-formed relics"** → 3x3 matrices (the kernels)
- **"chromatic layers"** → RGB color channels

The phrase "ritual of the gate" refers to calculating the **determinant** - one of the most fundamental properties of a matrix.

### Step 4: Calculate Determinants

Calculate the determinant of each 3x3 kernel matrix:

```python
import numpy as np

kr = np.array([[1,-1,0], [-1,5,-1], [2,-1,0]])
kg = np.array([[1,2,1], [-1,8,-1], [-3,-1,1]])
kb = np.array([[-1,-4,1], [1,4,4], [-1,3,1]])

print(f"Red: {int(np.round(np.linalg.det(kr)))}")    # 1
print(f"Green: {int(np.round(np.linalg.det(kg)))}")  # 40
print(f"Blue: {int(np.round(np.linalg.det(kb)))}")   # 35
```

**Results:**
- Red channel determinant: **1**
- Green channel determinant: **40**
- Blue channel determinant: **35**

### Step 5: Generate the Flag

Pass the three determinant values to the scalar processing script:

```bash
python process_scalars.py 1 40 35
```

**Flag:** `apoorvctf{1_40_35}`

## Key Concepts

1. **Convolution Kernels**: Used in image processing to apply various filters and transformations
2. **Kernel Recovery**: Using linear algebra (least squares) to reverse-engineer the transformation
3. **Matrix Determinant**: A scalar value that represents fundamental properties of a linear transformation
4. **Multi-channel Processing**: Operating independently on RGB color channels

## Why Determinants?

The determinant was the correct answer because:
- It's referred to as the "gate" in linear algebra (det = determinant = "gate")
- The determinant is a single scalar that encapsulates the essence of a matrix transformation
- It represents whether a transformation is reversible and by what factor space is scaled
- It's the most "enigmatic" and mathematically significant single value you can extract from a matrix

Other properties tested but incorrect:
- Center element: `5_8_4` ❌
- Sum of elements: `4_7_8` ❌
- Trace (diagonal sum): `6_10_4` ❌
- Determinant: `1_40_35` ✅

## Tools Used

- Python 3
- NumPy (for matrix operations)
- PIL/Pillow (for image processing)

---

**Author Notes:** This challenge cleverly combined image processing, linear algebra, and cryptic storytelling. The poetic description masked a technical challenge requiring understanding of convolution operations and matrix properties.
