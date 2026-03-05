from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

cipher_hex = "670c93f3661f6bc085df8793b27bd2b1e1482467d9987aa908a38a7ac0ae1855d5f4688229e9d1370ef3276c08c95d44a913943084ffb4cc9c8695fc02648f3c19c825d4bf1523d6dea0c6e0b21dd211317ad45cf1fcd9c16d003f6cd89f73de"

key = b"odysseus_journey"
iv = b"Princess"

cipher = AES.new(key, AES.MODE_CBC, iv.ljust(16, b"\0"))
plaintext = unpad(cipher.decrypt(bytes.fromhex(cipher_hex)), AES.block_size)
print("Recovered Plaintext:", plaintext.decode())
