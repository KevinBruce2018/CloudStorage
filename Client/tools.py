# -*- coding=utf-8-*-
from Crypto.Cipher import AES
class AesTool():
    """
    aes加密算法
    padding : PKCS7
    key iv len 16
    """
    __BLOCK_SIZE_16 = BLOCK_SIZE_16 = AES.block_size

    @staticmethod
    def encryt(content, key, iv):
        cipher = AES.new(key, AES.MODE_CBC,iv)
        x = AesTool.__BLOCK_SIZE_16 - (len(content) % AesTool.__BLOCK_SIZE_16)
        if x != 0:
            content = content + chr(x).encode()*x
        msg = cipher.encrypt(content)
        return msg

    @staticmethod
    def decrypt(content, key, iv):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        msg = cipher.decrypt(content)
        paddingLen = msg[len(msg)-1]
        return msg[0:-paddingLen]
