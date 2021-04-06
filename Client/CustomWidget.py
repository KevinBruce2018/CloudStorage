from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
class ClickLabel(QLabel):
    # 自定义信号, 注意信号必须为类属性
    button_clicked_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(ClickLabel, self).__init__(parent)

    def mouseReleaseEvent(self, QMouseEvent):
        self.button_clicked_signal.emit()
        
    # 可在外部与槽函数连接
    def connect_customized_slot(self, func):
        self.button_clicked_signal.connect(func)

class LoginButton(QWidget):
    def __init__(self):
        super().__init__()
        self.login_btn = QPushButton('登      录',self)
        self.forget_pass = ClickLabel(self)
        self.forget_pass.setText('忘记密码')
        self.reg_label = ClickLabel(self)
        self.reg_label.setText('立即注册')
        self.setFixedHeight(60)
        self.draw()
    def draw(self):
        self.login_btn.setFixedHeight(40)
        self.login_btn.setFixedWidth(316)
        self.login_btn.setFont(QFont('Arial',18))
        self.login_btn.setStyleSheet('background-color:#49a8f8;color:rgb(255,255,255);border-radius:8px')
        self.forget_pass.move(0,44)
        self.reg_label.move(260,44)
        self.forget_pass.setStyleSheet(
            'QLabel{color:#70b9fa;}'
            'QLabel:hover{color:#92c9fb;}'
        )
        self.reg_label.setStyleSheet(
            'QLabel{color:#70b9fa;}'
            'QLabel:hover{color:#92c9fb;}'
        )
    def setRegisterFunc(self,func):
        self.reg_label.connect_customized_slot(func)
    def setForgetPassFunc(self,func):
        self.forget_pass.connect_customized_slot(func)
    def setLoginFunc(self,func):
        self.login_btn.clicked.connect(func)

class UserLoginWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.user = QLabel('用户名',self)
        self.passwd = QLabel("密码   ",self)
        self.vcode = QLabel('验证码',self)
        self.userline = QLineEdit(self)
        self.userline.setFixedHeight(35)
        self.userline.setFixedWidth(255)
        self.passline = QLineEdit(self)
        self.passline.setFixedHeight(35)
        self.passline.setFixedWidth(255)
        self.passline.setEchoMode(QLineEdit.Password)
        self.vcode_label = ClickLabel(self)
        self.vcode_line = QLineEdit(self)
        self.vcode_line.setFixedHeight(28)
        self.draw()
        
    def setVcodeFunc(self,func):
        self.vcode_label.connect_customized_slot(func)
    def draw(self):
        w_user = QWidget(self)
        layout_user = QHBoxLayout()
        layout_user.addWidget(self.user)
        layout_user.addWidget(self.userline)
        w_user.setLayout(layout_user)
        
        w_pass = QWidget(self)
        layout_pass = QHBoxLayout()
        layout_pass.addWidget(self.passwd)
        layout_pass.addWidget(self.passline)
        w_pass.setLayout(layout_pass)
        w_pass.move(0,60)

        w_vcode = QWidget(self)
        layout_vcode = QHBoxLayout()
        layout_vcode.addWidget(self.vcode)
        layout_vcode.addWidget(self.vcode_line)
        layout_vcode.addWidget(self.vcode_label)
        w_vcode.setLayout(layout_vcode)
        w_vcode.move(0,115)