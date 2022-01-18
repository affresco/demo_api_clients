import base64
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2


class Crypt:

    def __init__(self, salt='Q9T2eYn7HyPTY2U3'):
        self.salt = salt.encode('utf8')
        self.enc_dec_method = 'utf-8'

    def get_private_key(self, secret):
        kdf = PBKDF2(secret, self.salt, 64, 1000)
        key = kdf[:32]
        return key

    def encrypt(self, message, secret):
        private_key = self.get_private_key(secret)
        message = pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(private_key, AES.MODE_CBC, bytearray(iv))
        result = base64.b64encode(iv + cipher.encrypt(bytearray(message, self.enc_dec_method)))
        return result.decode(self.enc_dec_method)


    def decrypt(self, message, secret):
        message = message.encode(self.enc_dec_method)
        private_key = self.get_private_key(secret)
        message = base64.b64decode(message)
        iv = message[:16]
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        decoded = unpad(cipher.decrypt(message[16:]))
        return decoded.decode(self.enc_dec_method)



BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]