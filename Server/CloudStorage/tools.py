import re
import random
from django.core.mail import send_mail
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import io
from PIL import ImageDraw, ImageFont, Image
import hashlib
import hmac
from Crypto.Cipher import AES
import base64
import threading

def checkUsername(username):
    if len(username)<5 or len(username)>21:
        return False
    compile = re.compile(r'[a-zA-Z]\w{4,20}')
    match =  compile.match(username)
    if match and match.group(0)==username:
        return True
    else:
        return False
def checkPassword(password):
    if len(password)<10 or len(password)>16:
        return False
    num = 0
    for i in password:
        if i.islower():
            num+=1
            break
    for i in password:
        if i.isupper():
            num+=1
            break
    for i in password:
        if i.isdigit():
            num+=1
            break
    for i in password:
        if i in '.~!@#$%^&*()/':
            num+=1
            break
    if num > 2:
        return True
    else:
        return False
def checkEmail(email):
    if len(email)<5 or len(email)>60:
        return False
    compile = re.compile(r'[0-9a-zA-Z_.]*@[0-9a-zA-Z_.]*[.]\w*')
    match =  compile.match(email)
    if match and match.group(0)==email:
        return True
    else:
        return False

def sendActivateMail(username,address):
    subject = '欢迎注册云安全存储系统'
    content = '尊敬的用户您好，请及时点击一下链接进行激活：\n'
    data = {'username': username, 'email': address}
    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    token = serializer.dumps(data).decode()
    content += 'http://127.0.0.1:8080/activate/?token=' + token
    content += '\n如果无法点击可以复制到浏览器中进行访问。\n该链接的有效期为一小时。'
    
    send_mail(subject, content, 
        settings.EMAIL_HOST_USER,[address], 
        fail_silently=False
    )


def check_verify_email_token(token):
    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    try:
        data = serializer.loads(token)
    except:
        return None
    else:
        user_id = data.get('username')
        #email = data.get('email')
        return user_id

def get_random_color():
    R = random.randrange(255)
    G = random.randrange(255)
    B = random.randrange(255)
    return (R, G, B)
# 获取验证码视图
def getChar():
    char_list = '0123456789abcdefghijklmnopqrstuvwxyz'
    char_list+='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return  char_list[random.randint(0,len(char_list)-1)]
def getColor():
    return (255,248,220)
    #return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))
def getColor2():
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))
def getVcode():
    width = 30 * 4
    height = 28
    #  生成图片
    image = Image.new('RGB', (width, height), (255, 255, 255))
    # 创建Font对象:
    font = ImageFont.truetype('Arial.ttf', 25)
    # 创建Draw对象:
    draw = ImageDraw.Draw(image)
    # 填充每个像素:
    for x in range(width):
        for y in range(height):
            draw.point((x, y), fill=getColor())
    # 输出文字:
    listChar=[]
    for t in range(4):
        char=getChar()
        listChar.append(char)
        draw.text((30 * t + 10, 0), char, font=font, fill=getColor2())

    buf = io.BytesIO()
    # 保存图片
    image.save(buf, 'png')
    return buf.getvalue(),''.join(listChar)

def checkSign(username,password,vcode,sign,timestamp):
    combine = username+vcode+timestamp
    salt = settings.SALT
    mac = hmac.new(hashlib.sha256((password+salt).encode()).digest(),combine.encode(),hashlib.md5)
    mac = base64.b64encode(mac.digest()).decode()
    if sign==mac:
        return True
    else:
        return False

class AesTool():
    """
    aes加密算法
    padding : PKCS7
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

class SendThread (threading.Thread):
    def __init__(self,user,email):
        threading.Thread.__init__(self)
        self.user = user
        self.email = email
    def run(self):
        sendActivateMail(self.user,self.email)
