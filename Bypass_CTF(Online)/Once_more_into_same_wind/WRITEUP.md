# Bypass CTF Challenge writeup : Once More Into the Same Wind 

## Challenge Description
> The crew of the Black Horizon believed their cipher unbreakable.
> Captain Blackwind swore by the Galois Seal — "no blade can cut it, no storm can bend it."
> 
> Yet in his haste, the navigator trusted the same wind to carry more than one message.

## Challenge Overview

This is a cryptography challenge involving **AES-GCM nonce reuse vulnerability**. The challenge demonstrates a critical flaw in the implementation of AES-GCM (Galois/Counter Mode) encryption when the same nonce (number used once) is reused with the same key for multiple messages.

We're provided with:
- `enq_EQq1fJa.py` - The encryption code (with redacted key, nonce, and flag)
- `output_RIIqaYT.txt` - Two ciphertexts encrypted with the same nonce

## Analysis

### Understanding the Clues

The challenge description is rich with cryptographic hints:
- **"Galois Seal"** → GCM stands for **Galois/Counter Mode**
- **"trusted the same wind"** → The same **nonce** (wind/direction) was reused
- **"carry more than one message"** → Multiple messages encrypted with the same nonce
- **"Once more into the same wind"** → The title itself hints at nonce reuse!

### Examining the Encryption Code

Looking at `enq_EQq1fJa.py`:

```python
from Crypto.Cipher import AES

FLAG = b"BYPASS_CTF{************************}"
key = b'0123456789abcdef'
nonce = b'******_*****!!'

def encrypt(plaintext, aad=b""):
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    cipher.update(aad)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return ciphertext, tag

aad = b"pirate-aad"
known_plaintext = b"A" * len(FLAG)

c1, t1 = encrypt(known_plaintext, aad)
c2, t2 = encrypt(FLAG, aad)

print("Ciphertext1:", c1.hex())
print("Ciphertext2:", c2.hex())
```

### Critical Vulnerability

The code has a **fatal flaw**: It uses the **same nonce** for both encryptions!

```python
nonce = b'******_*****!!'  # Same nonce for both messages
c1, t1 = encrypt(known_plaintext, aad)  # First encryption
c2, t2 = encrypt(FLAG, aad)             # Second encryption (SAME NONCE!)
```

This violates the fundamental rule of AES-GCM:
> **A nonce MUST be unique for every encryption with the same key.**

### Given Information

From `output_RIIqaYT.txt`:

```
Ciphertext1: 7713283f5e9979693d337dc27b7f5575350591c530d1d4c9070607c898be0588e5cf437aef
Ciphertext2: 740b393f4c8b676b283447f14f534b5d071bb2e105e4f0fa19332ee8b7a027a0d4e66749d3
```

We also know from the code:
- **Plaintext1**: `b"A" * len(FLAG)` (all 'A' characters, same length as the flag)
- **Plaintext2**: The FLAG (unknown, what we want to find)
- Both encrypted with the **same nonce** and **same key**

## Understanding AES-GCM

### How AES-GCM Works

AES-GCM is a mode of operation that provides both:
1. **Encryption** (confidentiality)
2. **Authentication** (integrity)

The encryption process:
```
Ciphertext = Plaintext ⊕ KeyStream
```

Where the keystream is generated from:
```
KeyStream = AES_Encrypt(Key, Counter_Block)
Counter_Block = Nonce || Counter
```

### The Nonce Reuse Vulnerability

When the same nonce is reused with the same key:

**First encryption:**
```
C1 = P1 ⊕ KeyStream
```

**Second encryption (SAME nonce = SAME keystream):**
```
C2 = P2 ⊕ KeyStream
```

### The Attack

Since both use the same keystream, we can XOR the ciphertexts:

```
C1 ⊕ C2 = (P1 ⊕ KeyStream) ⊕ (P2 ⊕ KeyStream)
C1 ⊕ C2 = P1 ⊕ P2           (KeyStream cancels out)
```

If we know P1, we can recover P2:
```
P2 = C1 ⊕ C2 ⊕ P1
```

In our case:
- P1 = `b"A" * len(FLAG)` (known)
- C1 and C2 are given
- P2 = FLAG (what we want)

Therefore:
```
FLAG = C1 ⊕ C2 ⊕ (b"A" * len(FLAG))
```

## Solution

### Exploitation Script

```python
#!/usr/bin/env python3

# AES-GCM nonce reuse attack
# When the same nonce is reused with the same key, we can XOR the ciphertexts

c1_hex = "7713283f5e9979693d337dc27b7f5575350591c530d1d4c9070607c898be0588e5cf437aef"
c2_hex = "740b393f4c8b676b283447f14f534b5d071bb2e105e4f0fa19332ee8b7a027a0d4e66749d3"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# known_plaintext = b"A" * len(FLAG)
known_plaintext = b"A" * len(c1)

# Since both messages use the same nonce and key:
# c1 = known_plaintext XOR keystream
# c2 = FLAG XOR keystream
# Therefore: c1 XOR c2 = known_plaintext XOR FLAG
# So: FLAG = c1 XOR c2 XOR known_plaintext

flag = bytes([c1[i] ^ c2[i] ^ known_plaintext[i] for i in range(len(c1))])

print("FLAG:", flag.decode())
```

### Execution

```bash
python3 solve.py
```

**Output:**
```
FLAG: BYPASS_CTF{rum_is_better_than_cipher}
```

### Step-by-Step Explanation

1. **Convert hex to bytes**:
   ```python
   c1 = bytes.fromhex("7713283f5e9979693d...")
   c2 = bytes.fromhex("740b393f4c8b676b28...")
   ```

2. **Create known plaintext** (all 'A's):
   ```python
   known_plaintext = b"A" * len(c1)
   # In ASCII, 'A' = 0x41
   ```

3. **XOR all three together**:
   ```python
   flag = c1 ⊕ c2 ⊕ known_plaintext
   ```

4. **Decode to ASCII**:
   ```python
   flag.decode()  # "BYPASS_CTF{rum_is_better_than_cipher}"
   ```

### Manual Verification

Let's verify with the first few bytes:

```python
C1[0] = 0x77
C2[0] = 0x74
P1[0] = 0x41 ('A')

FLAG[0] = C1[0] ^ C2[0] ^ P1[0]
        = 0x77 ^ 0x74 ^ 0x41
        = 0x42
        = 'B'  ✓ (First character of "BYPASS_CTF")
```

## Flag
```
BYPASS_CTF{rum_is_better_than_cipher}
```

The flag humorously suggests that pirates prefer rum over cryptography—or perhaps it's a commentary on how poor cryptographic implementation (nonce reuse) makes the cipher as worthless as water compared to rum!

## Why This Attack Works

### The Mathematics

AES-GCM in Counter mode generates a keystream:

```
For message position i:
KeyStream[i] = AES(Key, Nonce || Counter_i)
```

**Encryption:**
```
C1[i] = P1[i] ⊕ KeyStream[i]
C2[i] = P2[i] ⊕ KeyStream[i]
```

**XOR the ciphertexts:**
```
C1[i] ⊕ C2[i] = (P1[i] ⊕ KeyStream[i]) ⊕ (P2[i] ⊕ KeyStream[i])
                = P1[i] ⊕ P2[i] ⊕ KeyStream[i] ⊕ KeyStream[i]
                = P1[i] ⊕ P2[i]  (keystream cancels out)
```

**Recover plaintext:**
```
P2[i] = C1[i] ⊕ C2[i] ⊕ P1[i]
```

This is called a **two-time pad** attack in stream cipher terminology.

## Real-World Impact

### Historical Examples

1. **WEP (WiFi Security)**
   - Used RC4 with 24-bit IV
   - IV reuse was common
   - Led to complete compromise

2. **TLS 1.2 with GCM**
   - Some implementations had nonce generation issues
   - CVE-2016-0270 (Microsoft)

3. **HTTPS Traffic**
   - Nonce reuse can leak authentication keys
   - "Forbidden Attack" on AES-GCM (2016)

### Consequences of Nonce Reuse

1. **Complete Loss of Confidentiality**
   - If you know one plaintext, you can decrypt the other
   - Even without knowing plaintexts, patterns can be detected

2. **Authentication Bypass**
   - The GCM authentication tag can be forged
   - Attacker can create valid ciphertexts

3. **Key Recovery**
   - With enough nonce reuses, the encryption key can be recovered

## The Correct Implementation

### How to Use AES-GCM Properly

```python
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt_correctly(plaintext, key, aad=b""):
    # Generate a UNIQUE nonce for EVERY encryption
    nonce = get_random_bytes(12)  # 96 bits recommended
    
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    cipher.update(aad)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    
    # Return nonce with ciphertext (it's public, not secret)
    return nonce, ciphertext, tag

def decrypt_correctly(key, nonce, ciphertext, tag, aad=b""):
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    cipher.update(aad)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext
```

