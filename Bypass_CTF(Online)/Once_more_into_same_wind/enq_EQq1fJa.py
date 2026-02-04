from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# SECRET FLAG
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
