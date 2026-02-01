# Bypass CTF Challenge Writeup: Jigsaw Puzzle

## Challenge Description
A rival pirate ransacked Captain Jack Sparrow's cabin and tore his portrait into 25 pieces. The Captain had scrawled his latest secret orders across the back before it was framed. The task was to reassemble the image and decipher the hidden message.

## Solution

### Step 1: Reconnaissance
The challenge provided 25 PNG image pieces in the `pieces/` directory:
- 25 pieces total (suggesting a 5×5 grid)
- Each piece: 384×216 pixels
- Final reassembled image: 1920×1080 pixels

### Step 2: Image Reassembly
Created a Python script using PIL to reassemble the scattered pieces:

**Key Algorithm:**
- Computed edge compatibility between all piece pairs
- Used greedy backtracking with edge-matching scores
- Compared adjacent edges pixel-by-pixel using squared difference
- Tried different starting positions to find optimal arrangement

**Edge Matching Function:**
```python
def edge_difference(edge1, edge2):
    return np.sum(np.abs(edge1.astype(float) - edge2.astype(float)))
```

The algorithm tested different starting pieces and selected the arrangement with the **lowest total edge mismatch score**.

### Step 3: Finding the Hidden Message
Once the image was correctly reassembled in `reassembled.png`, text was visible on the portrait. The text appeared to be encoded.

### Step 4: Decryption - ROT13
The visible text from the reassembled image was encrypted using **ROT13** cipher.

**ROT13:** A simple letter substitution cipher that replaces each letter with the letter 13 positions after it in the alphabet (A↔N, B↔O, etc.)

After applying ROT13 decryption to the extracted text:

## Flag
```
BYPASS_CTF{EIGHT_PIECES_OF_EIGHT}
```

## Tools Used
- Python 3
- PIL (Pillow) for image manipulation
- NumPy for array operations and edge comparison
- ROT13 decoder

## Key Takeaways
1. **Image Puzzle Solving:** Edge-matching algorithms can effectively solve jigsaw puzzles programmatically
2. **Multi-layer Challenges:** CTFs often combine multiple techniques (image processing + cryptography)
3. **Classic Ciphers:** Don't overlook simple ciphers like ROT13 - they're still used in CTF challenges
4. **Pirates Reference:** "Pieces of Eight" refers to Spanish dollar coins historically used by pirates

