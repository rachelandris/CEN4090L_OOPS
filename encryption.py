# encryption.py
from Crypto.Cipher import AES
import base64
import bcrypt

class AESCipher:
    def __init__(self, key, iv):
        self.key = key
        self.iv = iv

    def encrypt(self, raw):
        raw = raw.encode('utf-8') if isinstance(raw, str) else raw
        cipher = AES.new(self.key, AES.MODE_CFB, self.iv)
        ciphertext = cipher.encrypt(raw)
        return base64.b64encode(ciphertext).decode('utf-8')

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CFB, self.iv)
        decrypted = cipher.decrypt(enc)
        return decrypted.decode('utf-8')

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())
