#!/usr/bin/env python3
"""
Solution for Medallion_of_Cortez CTF Challenge
Extracts hidden QR code from LSB and uses it to unlock steghide data
"""

from PIL import Image
import numpy as np
from pyzbar.pyzbar import decode
import subprocess

print("🏴‍☠️ Solving Medallion of Cortez CTF Challenge...\n")

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
    print("❌ No QR code found!")
    exit(1)

password = decoded[0].data.decode('utf-8')
print(f"[3] Found password: {password}")

# Step 3: Extract hidden data with steghide
print("[4] Extracting hidden data with steghide...")
try:
    result = subprocess.run(
        ["wsl", "steghide", "extract", "-sf", "Medallion_of_Cortez.bmp", "-p", password, "-f"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print(f"[5] Extraction successful!\n")
        # Read and display the flag
        with open("treasure.txt", "r") as f:
            flag = f.read().strip()
            print("="*50)
            print(f"🏆 FLAG: {flag}")
            print("="*50)
    else:
        print(f"❌ Steghide failed: {result.stderr}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nManual command: steghide extract -sf Medallion_of_Cortez.bmp -p", password)
