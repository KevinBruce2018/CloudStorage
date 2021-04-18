from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import requests
import os
import sys

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

class UserRegister(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('注册')
        self.headers = {}
        self.data = {}
        self.setUI()
    def setUI(self):
        self.setGeometry(540,200,360,480)
        """
        window_pale = QPalette() 
        window_pale.setBrush(self.backgroundRole(),QBrush(QPixmap("star.jpeg"))) 
        self.setPalette(window_pale)
        """
        #修改背景色为白色略微偏灰
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Background,QColor(248,248,248))
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        self.pic = QLabel(self)
        self.pic.setPixmap(QPixmap('logo.png'))
        self.user_lab = QLabel('用户名　',self)
        self.pass_lab = QLabel('密码　　',self)
        self.repeat_lab = QLabel('重复密码',self)
        self.email_lab = QLabel('邮箱　　',self)
        self.vcode_textlab = QLabel('验证码　',self)
        self.user_line = QLineEdit(self)
        self.pass_line = QLineEdit(self)
        self.repeat_line = QLineEdit(self)
        self.email_line = QLineEdit(self)
        self.vcode_lab = MyQLabel(self)
        self.vcode_line = QLineEdit(self)
        self.pass_line.setEchoMode(QLineEdit.Password)
        self.repeat_line.setEchoMode(QLineEdit.Password)
        self.submit_btn = QPushButton('提      交',self)
        self.submit_btn.clicked.connect(self.submit)
        self.vcode_lab.connect_customized_slot(self.refreshVcode)
        self.moveWidget()
        self.resizeWidget()
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
        else:
            QMessageBox.warning(self,'注册失败',r.json()['msg'],QMessageBox.Yes)
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
        self.vcode_line.setText('')
    def moveWidget(self):
        self.pic.move(45,20)
        self.user_lab.move(20,175)
        self.user_line.move(75,165)
        self.pass_lab.move(20,225)
        self.pass_line.move(75,215)
        self.repeat_lab.move(20,275)
        self.repeat_line.move(75,265)
        self.email_lab.move(20,325)
        self.email_line.move(75,315)
        self.vcode_lab.move(215,360)
        self.vcode_textlab.move(20,375)
        self.vcode_line.move(75,365)
        self.submit_btn.move(15,410)
    def resizeWidget(self):
        self.vcode_lab.setFixedSize(120,45)
        self.user_line.setFixedSize(255,35)
        self.pass_line.setFixedSize(255,35)
        self.repeat_line.setFixedSize(255,35)
        self.email_line.setFixedSize(255,35)
        self.vcode_line.setFixedHeight(30)
        self.submit_btn.setFixedSize(325,50)
        self.submit_btn.setFont(QFont('Arial',18))
        self.submit_btn.setStyleSheet('background-color:#49a8f8;color:rgb(255,255,255);border-radius:8px')
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UserRegister()
    window.setHeaders({'Cookie': 'csrftoken=9H7FU09VPdUw15XqrjQvHxempFdwEqxkjBqoiHLEeTpAblOi8xfKdWPkz6UhAdzN;sessionid=xldz406z7fdsll6avrykuznoia2zz3yf;'})
    window.setData('8XyfOcorowEbiynJv9IYf78EdLrZMx6ciRRYcT0aNc9fsOeBcn7dLwJCnc8KIk8F')
    window.show()
    window.refreshVcode()
    sys.exit(app.exec_())