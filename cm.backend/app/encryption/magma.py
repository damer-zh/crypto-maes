from pygost.gost28147 import GOST28147, ECB
import base64

def pad(text):
    pad_len = 8 - (len(text) % 8)
    return text + (chr(pad_len) * pad_len)

def unpad(text):
    pad_len = ord(text[-1])
    return text[:-pad_len]

def encrypt_magma(text, key):
    key = key[:32].ljust(32, '0').encode('utf-8')
    cipher = GOST28147(key, ECB)
    padded_text = pad(text).encode('utf-8')
    encrypted = cipher.encrypt(padded_text)
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt_magma(text, key):
    key = key[:32].ljust(32, '0').encode('utf-8')
    cipher = GOST28147(key, ECB)
    decrypted = cipher.decrypt(base64.b64decode(text)).decode('utf-8')
    return unpad(decrypted)