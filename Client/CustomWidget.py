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
        self.draw()
    def draw(self):
        self.login_btn.setFixedHeight(40)
        self.login_btn.setFixedWidth(316)
        self.login_btn.setFont(QFont('Arial',18))
        self.login_btn.setStyleSheet('background-color:#49a8f8;color:rgb(255,255,255)')
        self.forget_pass.move(0,44)
        self.reg_label.move(260,44)
        self.forget_pass.setStyleSheet(
            'QLabel{color:blue;}'
            'QLabel:hover{color:white;}'
        )
        self.reg_label.setStyleSheet(
            'QLabel{color:blue;}'
            'QLabel:hover{color:white;}'
        )
    def setRegisterFunc(self,func):
        self.reg_label.connect_customized_slot(func)
    def setForgetPassFunc(self,func):
        self.forget_pass.connect_customized_slot(func)
    def setLoginFunc(self,func):
        self.login_btn.clicked.connect(func)