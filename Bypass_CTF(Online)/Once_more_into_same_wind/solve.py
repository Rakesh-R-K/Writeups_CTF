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
