from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import requests
import os

class MyQLabel(QLabel):
    # 自定义信号, 注意信号必须为类属性
    button_clicked_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(MyQLabel, self).__init__(parent)

    def mouseReleaseEvent(self, QMouseEvent):
        self.button_clicked_signal.emit()
        
    # 可在外部与槽函数连接
    def connect_customized_slot(self, func):
        self.button_clicked_signal.connect(func)
class Mybox(QWidget):
    def __init__(self):
        super().__init__()
        self.setUp()
    def setUp(self):
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

class UserRegister(QWidget):
    def __init__(self):
        super().__init__()
        self.headers = {}
        self.data = {}
        self.setUI()
    def setUI(self):
        self.setGeometry(550,200,350,500)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        widget_list = []
        for i in range(6):
            widget_list.append(Mybox())
        widget_list[0].layout.addWidget(QLabel('用户名　'))
        widget_list[1].layout.addWidget(QLabel('密码　　'))
        widget_list[2].layout.addWidget(QLabel('重复密码'))
        widget_list[3].layout.addWidget(QLabel('邮箱　　'))
        widget_list[4].layout.addWidget(QLabel('验证码　'))
        for i in range(6):
            self.layout.addWidget(widget_list[i])
        self.user_line = QLineEdit()
        self.pass_line = QLineEdit()
        self.repeat_line = QLineEdit()
        self.email_line = QLineEdit()
        self.vcode_lab = MyQLabel()
        self.vcode_line = QLineEdit()
        self.pass_line.setEchoMode(QLineEdit.Password)
        self.repeat_line.setEchoMode(QLineEdit.Password)
        self.submit_btn = QPushButton('提交')
        widget_list[0].layout.addWidget(self.user_line)
        widget_list[1].layout.addWidget(self.pass_line)
        widget_list[2].layout.addWidget(self.repeat_line)
        widget_list[3].layout.addWidget(self.email_line)
        widget_list[4].layout.addWidget(self.vcode_line)
        widget_list[4].layout.addWidget(self.vcode_lab)
        widget_list[5].layout.addWidget(self.submit_btn)
        self.submit_btn.clicked.connect(self.submit)
        self.vcode_lab.connect_customized_slot(self.refreshVcode)
    def submit(self):
        username = self.user_line.text()
        password = self.pass_line.text()
        repeat = self.repeat_line.text()
        email = self.email_line.text()
        vcode = self.vcode_line.text()
        data = {
            "username":username,
            "password":password,
            "repeatpass":repeat,
            "email":email,
            "vcode":vcode
        }
        data |=self.data
        r = requests.post('http://127.0.0.1:8080/reg/',data=data,headers=self.headers)
        if 'success' in r.text:
            QMessageBox.warning(self,'注册成功',r.json()['msg'],QMessageBox.Yes)
            self.close()
        print(r.text)
    def setHeaders(self,headers):
        self.headers = headers
    def setData(self,data):
        self.data['csrfmiddlewaretoken'] = data
    def refreshVcode(self):
        r = requests.get('http://127.0.0.1:8080/captcha/',headers=self.headers)
        f = open('.vcode.png','wb')
        f.write(r.content)
        f.close()
        self.vcode_lab.setPixmap(QPixmap('.vcode.png'))
        os.remove('.vcode.png')
