#!/usr/bin/env python3
"""
Fix the Knot - CTF Challenge Solver
Extracts LSB steganography from PNG images

Challenge: Fix the Knot
Flag: CrackOn{Just_nothing}
"""

from PIL import Image
import os
import sys

def extract_lsb_from_png(image_path):
    """
    Extract Least Significant Bit (LSB) data from PNG red channel
    
    Args:
        image_path: Path to PNG file
        
    Returns:
        bytes: Extracted data from LSB layer
    """
    try:
        img = Image.open(image_path)
        filename = os.path.basename(image_path)
        
        print(f"[+] Processing: {filename}")
        print(f"    Dimensions: {img.size[0]} x {img.size[1]} pixels")
        print(f"    Color Mode: {img.mode}")
        
        pixels = img.load()
        width, height = img.size
        
        # Extract LSB from red channel
        lsb_bits = []
        for y in range(height):
            for x in range(width):
                pixel = pixels[x, y]
                
                # Get red channel
                if isinstance(pixel, tuple):
                    red_channel = pixel[0]
                else:
                    red_channel = pixel
                
                # Extract LSB (least significant bit)
                lsb = red_channel & 1
                lsb_bits.append(str(lsb))
        
        # Convert bits to bytes
        message_bytes = []
        for i in range(0, len(lsb_bits) - 7, 8):
            byte_str = ''.join(lsb_bits[i:i+8])
            char_code = int(byte_str, 2)
            message_bytes.append(char_code)
        
        message_data = bytes(message_bytes)
        
        print(f"    LSB Bits: {len(lsb_bits):,}")
        print(f"    Extracted: {len(message_data):,} bytes")
        
        return message_data
    
    except FileNotFoundError:
        print(f"[!] Error: File not found: {image_path}")
        return None
    except Exception as e:
        print(f"[!] Error: {e}")
        return None


def analyze_data(data):
    """
    Analyze extracted data for patterns and flags
    
    Args:
        data: Bytes to analyze
    """
    print(f"\n[*] Data Analysis:")
    
    # Check if all zeros
    if data.count(0) == len(data):
        print(f"    [*] Data contains all NULL bytes (0x00) - no embedded flag")
        return
    
    # Show hex dump
    hex_str = data[:64].hex()
    print(f"    First 64 bytes (hex):")
    for i in range(0, len(hex_str), 32):
        print(f"    {hex_str[i:i+32]}")
    
    # Extract printable text
    printable = ""
    for byte in data[:500]:
        if 32 <= byte <= 126:
            printable += chr(byte)
        elif byte == 10:
            printable += "\n    "
        elif byte == 0:
            printable += "[NUL]"
    
    if any(32 <= ord(c) <= 126 for c in printable):
        print(f"    Extracted text (first 500 bytes):")
        print(f"    {printable[:300]}")


def recreate_null_fixed(workspace):
    """
    Recreate null_fixed.png from null.png by fixing IHDR chunk
    
    Args:
        workspace: Working directory path
    """
    null_path = os.path.join(workspace, 'null.png')
    null_fixed_path = os.path.join(workspace, 'null_fixed.png')
    
    # Check if null_fixed.png already exists
    if os.path.exists(null_fixed_path):
        return True
    
    # Check if null.png exists
    if not os.path.exists(null_path):
        print(f"[!] Error: null.png not found!")
        return False
    
    try:
        # Read null.png
        with open(null_path, 'rb') as f:
            null_data = f.read()
        
        # Fix IHDR chunk (bytes 12-15)
        # Corrupted: 94 84 52 25
        # Fixed:     49 48 44 52 (spells "IHDR" in ASCII)
        fixed_data = bytearray(null_data)
        fixed_data[12:16] = bytes([0x49, 0x48, 0x44, 0x52])
        
        # Write null_fixed.png
        with open(null_fixed_path, 'wb') as f:
            f.write(fixed_data)
        
        print(f"[+] Created: null_fixed.png")
        return True
    
    except Exception as e:
        print(f"[!] Error recreating null_fixed.png: {e}")
        return False


def main():
    """Main solver function"""
    workspace = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 70)
    print("FIX THE KNOT - CTF Challenge Solver")
    print("=" * 70)
    print(f"Location: {workspace}\n")
    
    # Recreate null_fixed.png if needed
    print("[Phase 0] Verifying Challenge Files")
    print("-" * 70)
    recreate_null_fixed(workspace)
    
    # Process try_me.png
    try_me_path = os.path.join(workspace, 'try_me.png')
    
    if not os.path.exists(try_me_path):
        print(f"[!] Error: try_me.png not found!")
        print(f"[*] Required files:")
        print(f"    - try_me.png")
        print(f"    - null.png (for fixing)")
        return
    
    print("\n[Phase 1] LSB Extraction from try_me.png")
    print("-" * 70)
    
    data = extract_lsb_from_png(try_me_path)
    
    if data:
        analyze_data(data)
        
        # Save extracted data
        output_path = os.path.join(workspace, 'extracted_data.bin')
        try:
            with open(output_path, 'wb') as f:
                f.write(data)
            print(f"\n[+] Extracted data saved to: extracted_data.bin ({len(data)} bytes)")
        except Exception as e:
            print(f"[!] Failed to save: {e}")


if __name__ == "__main__":
    main()
