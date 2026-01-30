import zlib

# Read the raw DEFLATE compressed data
with open('chall.raw', 'rb') as f:
    data = f.read()

# Decompress raw DEFLATE (no zlib header)
# Using -zlib.MAX_WBITS to handle raw DEFLATE without wrapper
decompressed = zlib.decompress(data, -zlib.MAX_WBITS)

# Print the decompressed content
print(decompressed.decode('utf-8'))
