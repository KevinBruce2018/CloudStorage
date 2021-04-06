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


class UI_MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.headers = {"Cookie":""}
        self.data = {}
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
    def setUI(self):
        self.setWindowTitle('登录')
        #在Mac下无效
        self.setWindowFlag(Qt.WindowCloseButtonHint)
        #卡住固定大小的神器
        self.setFixedSize(340,420)

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
        w4 = QWidget()
        w0.setLayout(pic_layout)
        w1.setLayout(user_layout)
        w2.setLayout(pass_layout)
        w3.setLayout(vcode_layout)
        w4.setLayout(btn_layout)
        self.setLayout(layout)

        self.pic = QLabel()
        #使用绝对路径 解决不在当前路径运行时logo不显示的问题
        logo_path = os.path.abspath(__file__).split('/')[:-1]
        logo_path = '/'.join(logo_path)+'/logo.png'
        self.pic.setPixmap(QPixmap(logo_path))
        self.pic.resize(90,90)
        #self.pic.setScaledContents(True)

        self.user = QLabel('用户名',self)
        self.passwd = QLabel('密码  ',self)
        self.vcode = QLabel('验证码')
        self.reg_btn = QPushButton('注册',self)
        self.login_btn = QPushButton('登录',self)
        self.userline = QLineEdit()
        self.passline = QLineEdit()
        self.passline.setEchoMode(QLineEdit.Password)
        self.vcode_label = ClickLabel()
        self.vcode_line = QLineEdit()
        self.vcode_line.setFixedHeight(28)
        #self.vcode_label.setScaledContents(True)
        self.login_btn.clicked.connect(self.login)
        self.reg_btn.clicked.connect(self.reg)
        self.vcode_label.connect_customized_slot(self.refreshVcode)
        pic_layout.addWidget(self.pic)
        user_layout.addWidget(self.user)
        user_layout.addWidget(self.userline)
        pass_layout.addWidget(self.passwd)
        pass_layout.addWidget(self.passline)
        vcode_layout.addWidget(self.vcode)
        vcode_layout.addWidget(self.vcode_line)
        vcode_layout.addWidget(self.vcode_label)
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.reg_btn)
        layout.addWidget(w0)
        layout.addWidget(w1)
        layout.addWidget(w2)
        layout.addWidget(w3)
        layout.addWidget(w4)
        
    def login(self):
        username = self.userline.text()
        password = self.passline.text()
        vcode = self.vcode_line.text().lower()
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

class AdminClient(QWidget):
    def __init__(self):
        super().__init__()
        self.headers = {}
        self.data = {}
        self.setUI()
        
    def setUI(self):
        self.setGeometry(500,200,440,500)
        self.layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)

        self.setLayout(self.layout)
        self.lock = QPushButton('封号')
        self.unlock = QPushButton('解封账号')
        self.delete_btn = QPushButton('删除')
        self.share_btn = QPushButton('设为管理')

        btn_layout.addWidget(self.lock)
        btn_layout.addWidget(self.unlock)
        btn_layout.addWidget(self.delete_btn)
        self.delete_btn.clicked.connect(self.delete)
        self.unlock.clicked.connect(self.unlockuser)
        btn_layout.addWidget(self.share_btn)
        self.lock.clicked.connect(self.lockuser)
        self.layout.addWidget(btn_widget)
        self.table = QTableWidget()
        
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['用户名','用户状态','用户权限','操作'])
        self.layout.addWidget(self.table)
    def lockuser(self):
        url = 'http://127.0.0.1:8080/lockuser/'
        for i in range(len(self.userbox)):
            if self.userbox[i].checkState()==Qt.Checked:
                username = self.table.item(i,0).text()
                data = {}
                data['user'] = username
                data|=self.data
                r = requests.post(url=url,data=data,headers=self.headers)
                print(r.text)
                self.userList()
    def unlockuser(self):
        url = 'http://127.0.0.1:8080/unlockuser/'
        for i in range(len(self.userbox)):
            if self.userbox[i].checkState()==Qt.Checked:
                username = self.table.item(i,0).text()
                data = {}
                data['user'] = username
                data|=self.data
                r = requests.post(url=url,data=data,headers=self.headers)
                print(r.text)
                self.userList()
    def setHeaders(self,headers):
        self.headers = headers
    def setData(self,data):
        self.data['csrfmiddlewaretoken'] = data
    def userList(self):
        url = 'http://127.0.0.1:8080/userlist/'
        r = requests.get(url,headers=self.headers)
        self.userbox = []
        data = r.json()['users']
        self.table.setRowCount(len(data))
        for i in range(len(data)):
            self.userbox.append(QCheckBox())
            for j in range(self.table.columnCount()-1):
                self.table.setItem(i,j,QTableWidgetItem(str(data[i][j])))
            self.table.setCellWidget(i,self.table.columnCount()-1,self.userbox[i])
    def delete(self):
        for i in range(len(self.userbox)):
            if self.userbox[i].checkState()==Qt.Checked:
                username = self.table.item(i,0).text()
                data = {}
                data['user'] = username
                data|=self.data
                print(self.data)
                r = requests.post('http://127.0.0.1:8080/deluser/',data=data,headers=self.headers)
                text = r.text
                print(text)
                self.userList()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UI_MainWindow()
    """
    window = SecurityCloudStorageClient()
    window.setHeaders({'Cookie': 'csrftoken=TNYQBFIdXKHgqz0yt94V2cE4LpzGLJPa0jItOimNp5mr1yUXdrEV9KGvNHlmpF7B;sessionid=uyng5h4byacxcm34ws3ozetrk9mgoiqq;'})
    window.setData('hqLhgOUUpM8TwMbquK7O8hjtYnfBQLSCoWvUtryuR7N47L5Pe2HOfPlU0F1huHa3')
    
    window.filelist()
    """
    window.show()
    sys.exit(app.exec_())
    