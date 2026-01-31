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