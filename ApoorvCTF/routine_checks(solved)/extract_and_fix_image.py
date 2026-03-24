#!/usr/bin/env python3
"""
Extract and fix the corrupted JPEG from packet #13
"""

from scapy.all import rdpcap, Raw

def extract_and_fix_image():
    print("[*] Loading PCAP...")
    packets = rdpcap("challenge.pcap")
    
    print("[*] Extracting packet #13...")
    packet_13 = packets[13]
    
    if packet_13.haslayer(Raw):
        data = packet_13[Raw].load
        print(f"[*] Extracted {len(data)} bytes")
        
        # Fix the corrupted first byte (0x3f -> 0xff for JPEG)
        print("[*] Fixing corrupted first byte...")
        fixed_data = b'\xff' + data[1:]
        
        # Save the fixed image
        with open('fixed.jpg', 'wb') as f:
            f.write(fixed_data)
        
        print("[+] Saved fixed.jpg")
        print("[*] Use 'steghide extract -sf fixed.jpg' to get the flag")
    else:
        print("[!] No data in packet #13")

if __name__ == "__main__":
    extract_and_fix_image()
