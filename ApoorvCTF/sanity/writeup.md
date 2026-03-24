Writeup: Zero-Width Character Steganography (ApoorvCTF)
Challenge Overview
We were given a seemingly normal, friendly message announcing "Wave 2" of a challenge. On the surface, it reads like standard text with a few emojis. However, the prompt heavily implied a hidden flag within the message itself.

Step 1: Initial Reconnaissance
When dealing with text that supposedly contains a hidden payload, the first step is to look for invisible anomalies. Dropping the text into a tool like CyberChef, a hex editor, or even a simple Python script reveals a massive amount of invisible Unicode characters hidden between the visible words.

Specifically, we find sequences of the following Zero-Width Characters (ZWCs) and formatting marks:

\u200c (Zero-Width Non-Joiner)

\u200d (Zero-Width Joiner)

\u202a (Left-to-Right Embedding)

\u202c (Pop Directional Formatting)

\ufeff (Zero-Width No-Break Space)

Step 2: Deducing the Encoding
Because there are exactly 5 distinct invisible characters, this strongly suggests a Base-5 encoding scheme. We can map each character to a digit from 0 to 4 based on how they appear to sequence in the text:

\u200c = 0

\u200d = 1

\u202a = 2

\u202c = 3

\ufeff = 4

Step 3: Extracting the Payload
Looking closely at the hidden character strings, they are grouped into distinct blocks, generally separated by the actual visible words.

Most blocks consist of 7 characters, padded at the front with zeroes (\u200c).
For example, the first block before the word "Hallo" is:
\u200c\u200c\u200c\u200c\u202c\ufeff\u202a

Strip the padding: Remove the leading \u200c (0) characters. We are left with \u202c\ufeff\u202a.

Map to Base-5: Using our mapping, this becomes 3 4 2.

Convert Base-5 to Decimal: (3 * 25) + (4 * 5) + (2 * 1) = 97.

Convert Decimal to ASCII: ASCII character 97 is a.

Repeating this process block by block reveals the flag character by character.

Step 4: The Solve Script (Python)
Instead of doing all 34 blocks by hand, we can write a quick Python script to extract and decode the payload automatically:

Python
import re

# The hidden message mapping
base5_map = {
    '\u200c': '0',
    '\u200d': '1',
    '\u202a': '2',
    '\u202c': '3',
    '\ufeff': '4'
}

with open("challenge_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Regex to find consecutive blocks of our target ZWCs
hidden_blocks = re.findall(r'[\u200c\u200d\u202a\u202c\ufeff]+', text)

flag = ""
for block in hidden_blocks:
    # Convert the block to a Base-5 string
    base5_str = "".join([base5_map[char] for char in block])
    
    # Convert Base-5 string to an integer, then to an ASCII character
    ascii_val = int(base5_str, 5)
    flag += chr(ascii_val)

print(f"Flag: {flag}")
The Flag
Running the logic against the full text perfectly reconstructs the hidden string, revealing the double 'o' in the prefix and the leetspeak inside the curly braces.

apoorvctf{d0n7_w0rry_y0u_4r3_s4n3}