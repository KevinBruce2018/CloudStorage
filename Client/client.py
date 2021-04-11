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
import webbrowser

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
    def keyPressEvent(self, event):
        key = event.key()
        if key==Qt.Key_Return or key==Qt.Key_Enter:
            self.login()
    def setComponent(self):
        self.login_widget = UserLoginWidget()
        self.pic = QLabel()
        self.userline = self.login_widget.userline
        self.passline = self.login_widget.passline
        self.vcode_label = self.login_widget.vcode_label
        self.vcode_line = self.login_widget.vcode_line
        self.vcode_line.setFixedHeight(28)
        self.vcode_label.connect_customized_slot(self.refreshVcode)

        #使用绝对路径 解决不在当前路径运行时logo不显示的问题
        logo_path = os.path.abspath(__file__).split('/')[:-1]
        logo_path = '/'.join(logo_path)+'/logo.png'
        self.pic.setPixmap(QPixmap(logo_path))
    def setUI(self):
        self.setWindowTitle('可信云存储系统')
        self.setFixedSize(360,465)
        #修改背景色为白色
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Background,Qt.white)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        layout=QVBoxLayout()
        self.setLayout(layout)
        w0 = QWidget()
        pic_layout = QHBoxLayout()
        pic_layout.setContentsMargins(30,0,10,0)
        pic_layout.addWidget(self.pic)
        w0.setLayout(pic_layout)
        w1 = LoginButton()
        w1.setRegisterFunc(self.reg)
        w1.setLoginFunc(self.login)
        w1.setForgetFunc(self.changePwd)
        layout.addWidget(w0)
        layout.addWidget(self.login_widget)
        layout.addWidget(w1)

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
    def changePwd(self):
        webbrowser.open('http://127.0.0.1:8080/changepwd/')
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CloudStorageMainWindow()
    window.show()
    sys.exit(app.exec_())
    