from PIL import Image

img = Image.open('chall.png')
pixels = img.load()
width, height = img.size

# 1. Check the first row for ASCII hidden in Red/Green/Blue channels
first_row_data = ""
for x in range(width):
    r, g, b = pixels[x, 0][:3]
    # Check if the values fall in printable ASCII range
    for val in [r, g, b]:
        if 32 <= val <= 126:
            first_row_data += chr(val)

print(f"First Row Scan: {first_row_data[:50]}...")

# 2. Check Least Significant Bit (LSB)
lsb_data = ""
byte_val = 0
bit_count = 0

for y in range(height):
    for x in range(width):
        r, g, b = pixels[x, y][:3]
        for channel in [r, g, b]:
            byte_val = (byte_val << 1) | (channel & 1)
            bit_count += 1
            if bit_count == 8:
                if 32 <= byte_val <= 126:
                    lsb_data += chr(byte_val)
                byte_val = 0
                bit_count = 0
    if len(lsb_data) > 100: break # Stop if we find a long string

print(f"LSB Scan: {lsb_data[:50]}...")