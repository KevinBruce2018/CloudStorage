from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import requests
import time
import os
import hmac
import hashlib
import base64
from Audit import Audit
from SecurityCloudStorageClient import SecurityCloudStorageClient
from UserRegister import UserRegister
from CustomWidget import *
from AdminClient import AdminClient

class CloudStorageMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.headers = {"Cookie":""}
        self.data = {}
        self.setComponent()
        self.setUI()
        self.loginPre()
        self.mainwindow = SecurityCloudStorageClient()
    def refreshVcode(self):
        r = requests.get('http://127.0.0.1:8080/captcha/',headers=self.headers)
        f = open('.vcode.png','wb')
        f.write(r.content)
        f.close()
        self.vcode_label.setPixmap(QPixmap('.vcode.png'))
        os.remove('.vcode.png')
    def setComponent(self):
        self.pic = QLabel()
        self.user = QLabel('用户名',self)
        self.passwd = QLabel("密码")
        self.blank = QLabel('       ')
        self.vcode = QLabel('验证码')
        self.userline = QLineEdit()
        self.passline = QLineEdit()
        self.passline.setEchoMode(QLineEdit.Password)
        self.vcode_label = ClickLabel()
        self.vcode_line = QLineEdit()
        self.vcode_line.setFixedHeight(28)
        self.vcode_label.connect_customized_slot(self.refreshVcode)

        #使用绝对路径 解决不在当前路径运行时logo不显示的问题
        logo_path = os.path.abspath(__file__).split('/')[:-1]
        logo_path = '/'.join(logo_path)+'/logo.png'
        self.pic.setPixmap(QPixmap(logo_path))
        self.pic.resize(90,90)
    def setUI(self):
        self.setWindowTitle('登录')
        #在Mac下无效
        self.setWindowFlag(Qt.WindowCloseButtonHint)
        self.setFixedSize(360,500)
        #修改背景色为白色
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Background,Qt.white)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        layout=QVBoxLayout()
        user_layout = QHBoxLayout()
        pass_layout = QHBoxLayout()
        vcode_layout = QHBoxLayout()
        btn_layout = QHBoxLayout()
        pic_layout = QHBoxLayout()

        w0 = QWidget()
        w1 = QWidget()
        w2 = QWidget()
        w3 = QWidget()
        w4 = LoginButton()
        w0.setLayout(pic_layout)
        w1.setLayout(user_layout)
        w2.setLayout(pass_layout)
        w3.setLayout(vcode_layout)
        self.setLayout(layout)
        
        pic_layout.addWidget(self.pic)
        user_layout.addWidget(self.user)
        user_layout.addWidget(self.userline)
        pass_layout.addWidget(self.passwd)
        pass_layout.addWidget(self.passline)
        vcode_layout.addWidget(self.vcode)
        vcode_layout.addWidget(self.vcode_line)
        vcode_layout.addWidget(self.vcode_label)
        btn_layout.addWidget(self.blank)
        w4.setRegisterFunc(self.reg)
        w4.setLoginFunc(self.login)
        layout.addWidget(w0)
        layout.addWidget(w1)
        layout.addWidget(w2)
        layout.addWidget(w3)
        layout.addWidget(w4)
    def login(self):
        username = self.userline.text()
        password = self.passline.text()
        vcode = self.vcode_line.text()
        timestamp = str(int(time.time()))
        salt = 'dh;fjlkdffhjsfhks7738e2djekd'
        combine = username+vcode+timestamp
        sign = hmac.new(hashlib.sha256((password+salt).encode()).digest(),combine.encode(),hashlib.md5)
        sign = base64.b64encode(sign.digest()).decode()
        data = {
            'username':username,
            'password':password,
            'vcode':vcode,
            'timestamp':timestamp,
            'sign':sign
        }
        self.data |= data
        
        r = requests.post('http://127.0.0.1:8080/login/',data=self.data,headers=self.headers)
        json_data = r.json()
        if json_data['result']=='success':
            self.close()
            #根据不同的权限显示不同的页面
            r = requests.get('http://127.0.0.1:8080/getauthority/',headers=self.headers)
            if r.status_code!=403 and r.text=='1':
                self.admin = AdminClient()
                self.admin.setHeaders(self.headers)
                self.admin.userList()
                self.admin.setData(self.data['csrfmiddlewaretoken'])
                self.admin.show()
            elif r.status_code!=403 and r.text=='2':
                self.log = Audit()
                self.log.setHeaders(self.headers)
                self.log.setData(self.data['csrfmiddlewaretoken'])
                self.log.logList()
                self.log.show()
            elif r.status_code!=403 and r.text=='3':
                self.mainwindow.show()
                self.mainwindow.setHeaders(self.headers)
                self.mainwindow.setData(self.data['csrfmiddlewaretoken'])
                self.mainwindow.filelist()
        else:
            #中英文转化的问题
            QMessageBox.warning(self,'登录失败',json_data['msg'],QMessageBox.Yes)
            self.refreshVcode()

    def loginPre(self):
        token_url = 'http://127.0.0.1:8080/gettoken/'
        vcode_url = 'http://127.0.0.1:8080/captcha/'
        #获取token
        r = requests.get(token_url)
        self.data = r.json()
        cookies = requests.utils.dict_from_cookiejar(r.cookies)
        r = requests.get(vcode_url)
        cookies |= requests.utils.dict_from_cookiejar(r.cookies)
        #将cookie写入到header中
        for key in cookies:
            self.headers["Cookie"] += key+'='+cookies[key]+';'
        #设置验证码
        f = open('.vcode.png','wb')
        f.write(r.content)
        f.close()
        self.vcode_label.setPixmap(QPixmap('.vcode.png'))
        os.remove('.vcode.png')
    def reg(self):
        self.regwin = UserRegister()
        self.regwin.setHeaders(self.headers)
        self.regwin.setData(self.data['csrfmiddlewaretoken'])
        self.regwin.refreshVcode()
        self.regwin.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CloudStorageMainWindow()
    window.show()
    sys.exit(app.exec_())
    