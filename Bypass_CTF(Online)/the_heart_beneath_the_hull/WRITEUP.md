# Bypass CTF Challenge Writeup : The Heart Beneath the Hull 

## Challenge Description
> Not all treasures are buried in sand.

## Challenge Overview
This challenge provides an image of an ESP32 development board (PCB). The image shows a clean PCB layout with:
- ESP32 microcontroller module
- AMS1117 voltage regulator
- BOOT and EN buttons
- Various passive components

At first glance, it appears to be a hardware-themed challenge, but it's categorized as **Steganography**.

## Analysis

### Initial Observations

The image shows a professional ESP32 development board with clear silkscreen markings. For a steganography challenge, we need to look beyond typical digital steganography techniques (LSB, EXIF data, hidden files).

### Key Insight: Visual Steganography

The critical clue is in the challenge description: **"Not all treasures are buried in sand"**

This suggests:
- The treasure isn't hidden in the image file data
- It's not buried deep (no complex extraction needed)
- It's visible, but requires observation

### Finding the Hidden Message

Looking carefully at the PCB silkscreen, there are hexadecimal values printed along the top and bottom edges of the board:

**Top row:**
```
68 65 61 72 74 5f 69 6e 5f 61 5f 63 68 65 73 74
```

**Bottom row:**
```
68 65 61 72 74 5f 69 6e 5f 61 5f 63 68 65 73 74
```

These hex values are printed as part of the PCB silkscreen text, disguised as component labels or pin identifiers!

## Solution

### Converting Hex to ASCII

Let's convert the hexadecimal sequence to ASCII:

| Hex | ASCII |
|-----|-------|
| 68  | h     |
| 65  | e     |
| 61  | a     |
| 72  | r     |
| 74  | t     |
| 5f  | _     |
| 69  | i     |
| 6e  | n     |
| 5f  | _     |
| 61  | a     |
| 5f  | _     |
| 63  | c     |
| 68  | h     |
| 65  | e     |
| 73  | s     |
| 74  | t     |

**Result:** `heart_in_a_chest`

### Python Solution

```python
hex_string = "68 65 61 72 74 5f 69 6e 5f 61 5f 63 68 65 73 74"
hex_bytes = bytes.fromhex(hex_string.replace(" ", ""))
message = hex_bytes.decode('ascii')

print(f"Hidden message: {message}")
print(f"Flag: BYPASS_CTF{{{message}}}")
```

**Output:**
```
Hidden message: heart_in_a_chest
Flag: BYPASS_CTF{heart_in_a_chest}
```

### Quick Manual Conversion

You can also use an online hex-to-ASCII converter or the command line:

```bash
echo "686561727435f696e5f615f636865737434" | xxd -r -p
```

Or in Python:
```bash
python -c "print(bytes.fromhex('68656172745f696e5f615f63686573743').decode())"
```

## Understanding the Theme

The challenge title and solution connect beautifully:

- **"The heart"** → The ESP32 microcontroller (the "heart" of the board)
- **"Beneath the hull"** → Hidden under the hardware context
- **"Not all treasures are buried in sand"** → The message is in plain sight, not digitally hidden
- **"heart_in_a_chest"** → A treasure chest metaphor, fitting the pirate theme

The hex values are cleverly disguised as legitimate PCB silkscreen markings, making them blend into the technical appearance of the board.

## Flag
```
BYPASS_CTF{heart_in_a_chest}
```

## Key Takeaways

1. **Visual Steganography**: Not all steganography involves manipulating file data. Sometimes the message is hidden in plain sight within the visual content itself.

2. **Hardware-Themed Challenges**: When you see technical hardware images, check for:
   - Component labels
   - Silkscreen text
   - Serial numbers
   - Pin labels
   - Any printed text or numbers

3. **Context Matters**: The challenge description provides crucial hints. "Not all treasures are buried in sand" was telling us to look at what's visible on the surface.

4. **Hex Encoding**: A common way to hide ASCII messages is through hexadecimal encoding. Always try converting suspicious hex sequences to ASCII.

5. **Disguise Through Context**: The hex values look legitimate because they're on a PCB. Our brains expect to see technical markings on circuit boards, making it easy to overlook the hidden message.
