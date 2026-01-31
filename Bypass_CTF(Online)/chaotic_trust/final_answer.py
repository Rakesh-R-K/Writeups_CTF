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
flag = bytes(c ^ k for c, k in zip(cipher, keystream))

print('='*60)
print('SOLUTION VERIFIED')
print('='*60)
print(f'Seed: {seed}')
print(f'First 16 bytes of keystream: {keystream[:16].hex()}')
print(f'Leak:                        {leak.hex()}')
print(f'Match: {keystream[:16] == leak}')
print()
print(f'Flag: {flag.decode("ascii")}')
print('='*60)
