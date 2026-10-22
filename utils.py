# utils.py
from aes_manual import AES_128

def pad(data: bytes) -> bytes:
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)

def unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]

def aes_encrypt(key: str, plaintext: str) -> str:
    aes = AES_128(key.encode('ascii'))
    pt_padded = pad(plaintext.encode('ascii'))
    ct = b''
    for i in range(0, len(pt_padded), 16):
        ct += aes.encrypt_block(pt_padded[i:i+16])
    return ct.hex() # Mengembalikan dalam bentuk Hexadecimal

def aes_decrypt(key: str, ciphertext_hex: str) -> str:
    aes = AES_128(key.encode('ascii'))
    ct_bytes = bytes.fromhex(ciphertext_hex)
    pt = b''
    for i in range(0, len(ct_bytes), 16):
        pt += aes.decrypt_block(ct_bytes[i:i+16])
    return unpad(pt).decode('ascii')