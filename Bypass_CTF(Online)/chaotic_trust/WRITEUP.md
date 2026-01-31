# Bypass CTF Writeup : Chaotic Trust 

## Challenge Description
> Chaos was used to generate a keystream for encrypting the flag using XOR.
> A partial keystream leak was left behind during debugging.
> 
> Chaos on computers isn't always unpredictable.
> Can you exploit floating-point precision and recover the flag?

## Challenge Overview
This challenge uses a chaotic system (logistic map) to generate a keystream for XOR encryption. We're given:
- The encrypted flag (ciphertext)
- A partial keystream leak (first 16 bytes)
- The encryption algorithm

## Given Files

### chall.py
```python
import struct

def logistic_map(x, r=3.99):
    return r * x * (1 - x)

def generate_keystream(seed, length):
    x = seed
    stream = b""
    while len(stream) < length:
        x = logistic_map(x)
        stream += struct.pack("f", x)[-2:]
    return stream[:length]
```

### output_cphsRGh.txt
```
cipher = 9f672a7efb6ec57d0379727c360bc968c07e8b6a256acc0a850f4c608b6a9e0b5472f11f0d
leak   = dd3e7a3fa83d9a3e573f093f7e3ff93c
```

## Analysis

### Understanding the Encryption

1. **Logistic Map**: The challenge uses the logistic map, a classic example of a chaotic system:
   - Formula: `x_{n+1} = r * x_n * (1 - x_n)` where `r = 3.99`
   - This is deterministic but exhibits chaotic behavior
   - Small changes in the seed produce vastly different sequences

2. **Keystream Generation**:
   - Iteratively applies the logistic map
   - Takes the last 2 bytes of the 4-byte float representation (`struct.pack("f", x)[-2:]`)
   - Generates a byte stream of the required length

3. **Encryption**: Simple XOR with the keystream

### The Vulnerability

Despite being called "chaotic", the logistic map has a critical weakness:

**It's completely deterministic!**

If we can recover the seed, we can regenerate the entire keystream. The "leak" is the key to solving this challenge.

### Solution Approach

The challenge description hints at "floating-point precision" exploitation. The key insight is:

1. We have the first 16 bytes of the keystream (the leak)
2. The keystream generation is deterministic
3. We can brute-force common seed values

Since this is a CTF challenge, common seeds to try include:
- Simple decimals: 0.1, 0.5, 0.123456, etc.
- Mathematical constants: π/4, e/10, etc.
- Common test values

### Solving the Challenge

Testing common seed values, we find that **seed = 0.123456** produces a keystream that matches the leak perfectly!

```python
import struct

def logistic_map(x, r=3.99):
    return r * x * (1 - x)

def generate_keystream(seed, length):
    x = seed
    stream = b""
    while len(stream) < length:
        x = logistic_map(x)
        stream += struct.pack("f", x)[-2:]
    return stream[:length]

cipher = bytes.fromhex('9f672a7efb6ec57d0379727c360bc968c07e8b6a256acc0a850f4c608b6a9e0b5472f11f0d')
leak = bytes.fromhex('dd3e7a3fa83d9a3e573f093f7e3ff93c')

seed = 0.123456

keystream = generate_keystream(seed, 37)

# Verify the seed is correct
print(f'First 16 bytes of keystream: {keystream[:16].hex()}')
print(f'Leak:                        {leak.hex()}')
print(f'Match: {keystream[:16] == leak}')

# Decrypt the flag
flag = bytes(c ^ k for c, k in zip(cipher, keystream))
print(f'\nFlag: {flag.decode("ascii")}')
```

### Verification

```
First 16 bytes of keystream: dd3e7a3fa83d9a3e573f093f7e3ff93c
Leak:                        dd3e7a3fa83d9a3e573f093f7e3ff93c
Match: True

Flag: BYPASS_CTF{CH40T1C_TRU57_15_4W350M3!}
```

## Key Takeaways

1. **Chaos ≠ Randomness**: Chaotic systems are deterministic, not random. Given the same initial conditions, they produce the same output.

2. **Never Roll Your Own Crypto**: Using mathematical functions like the logistic map for cryptography is dangerous. Proper CSPRNGs (Cryptographically Secure Pseudo-Random Number Generators) should be used.

3. **Information Leaks Are Fatal**: The 16-byte leak was enough to recover the entire keystream because the system was deterministic.

4. **Floating-Point Isn't the Issue Here**: While the challenge description mentions floating-point precision, the real vulnerability is the deterministic nature and the keystream leak. With the leak, we can verify seed candidates directly.

## Flag
```
BYPASS_CTF{CH40T1C_TRU57_15_4W350M3!}
```

## Alternative Approaches

If the seed wasn't a simple value, we could:
1. **Brute-force more systematically**: Try seeds with different precisions
2. **Reverse the logistic map**: Given consecutive outputs, try to work backwards (though this is complex)
3. **Use the floating-point structure**: Analyze the specific byte patterns to constrain possible seeds

However, for this CTF challenge, testing common seed values was the intended and most efficient approach.
