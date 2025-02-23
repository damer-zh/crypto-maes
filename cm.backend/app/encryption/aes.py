from Crypto.Cipher import AES
import base64

def pad(data):
    if isinstance(data, str):
        data = data.encode()
    padding_length = 16 - len(data) % 16
    return data + bytes([padding_length] * padding_length)

def unpad(data):
    padding_length = data[-1]
    return data[:-padding_length]

def encrypt_aes(text, key):
    key = key[:16].ljust(16)
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(text))
    return base64.b64encode(encrypted).decode()

def decrypt_aes(text, key):
    key = key[:16].ljust(16)
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    decrypted = unpad(cipher.decrypt(base64.b64decode(text)))
    return decrypted.decode()

def encrypt_file_aes(data, key):
    key = key[:16].ljust(16)
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    padded_data = pad(data)
    encrypted = cipher.encrypt(padded_data)
    return encrypted

def decrypt_file_aes(data, key):
    key = key[:16].ljust(16)
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    decrypted = unpad(cipher.decrypt(data))
    return decrypted
