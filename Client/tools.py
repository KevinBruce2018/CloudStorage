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

def FileSizeFormat(data):
    if int(data)/1024<1:
        return str(data) + 'B'
    elif int(data)/1024<1024:
        return "{:.2f}KB".format(int(data)/1024)
    elif int(data)/(1024**2)<1024:
        return "{:.2f}MB".format(int(data)/1024/1024)
    else:
        return "{:.2f}GB".format(int(data)/(1024**3))
def TimeFormat(data):
    data = data.split('T')
    day = data[0]
    minute = data[1].split('.')[0][:-3]
    return day+' '+minute

def AuthorityFormat(data):
    if int(data)==1:
        return '管理用户'
    elif int(data)==2:
        return '获取日志'
    elif int(data)==3:
        return '上传、下载、删除文件'
    else:
        return '无权限'
def StatusFormat(data):
    if int(data)==1:
        return '正常'
    elif int(data)==3:
        return '未激活'
    else:
        return '封号'
        