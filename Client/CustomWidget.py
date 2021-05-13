from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
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
    def setForgetFunc(self,func):
        self.forget_pass.connect_customized_slot(func)

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

class CheckBoxHeader(QHeaderView):
    """自定义表头类"""

    # 自定义 复选框全选信号
    select_all_clicked = pyqtSignal(bool)
    # 这4个变量控制列头复选框的样式，位置以及大小
    _x_offset = 0
    _y_offset = 0
    _width = 20
    _height = 20

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super(CheckBoxHeader, self).__init__(orientation, parent)
        self.isOn = False
    def setCheckBox(self,header_box):
        self.all_header_combobox = header_box
    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super(CheckBoxHeader, self).paintSection(painter, rect, logicalIndex)
        painter.restore()

        self._y_offset = int((rect.height() - self._width) / 2.)
        #第几列添加复选框
        if logicalIndex == 0:
            option = QStyleOptionButton()
            option.rect = QRect(rect.x() + self._x_offset, rect.y() + self._y_offset, self._width, self._height)
            option.state = QStyle.State_Enabled | QStyle.State_Active
            if self.isOn:
                option.state |= QStyle.State_On
            else:
                option.state |= QStyle.State_Off
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)

    def mousePressEvent(self, event):
        index = self.logicalIndexAt(event.pos())
        if 0 == index:
            x = self.sectionPosition(index)
            #if x + self._x_offset < event.pos().x() < x + self._x_offset + self._width and self._y_offset < event.pos().y() < self._y_offset + self._height:
            if self.isOn:
                self.isOn = False
            else:
                self.isOn = True
                    # 当用户点击了行表头复选框，发射 自定义信号 select_all_clicked()
            self.select_all_clicked.emit(self.isOn)
            #绘制第i列的框
            self.updateSection(0)

    # 自定义信号 select_all_clicked 的槽方法
    def change_state(self, isOn):
        # 如果行表头复选框为勾选状态
        if isOn:
            # 将所有的复选框都设为勾选状态
            for i in self.all_header_combobox:
                i.setCheckState(Qt.Checked)
        else:
            for i in self.all_header_combobox:
                i.setCheckState(Qt.Unchecked)

class CustomFile(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.draw()
    def draw(self):
        self.icon = QLabel(self)
        self.icon.setPixmap(QPixmap('file.png'))
        self.icon.resize(30,30)
        self.icon.setScaledContents(True)
        self.name = QLabel(self)
        self.name.move(35,8)
    def setName(self,name):
        self.name.setText(name) 

class UserManage(QLabel):
    button_clicked_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(UserManage, self).__init__(parent)
    def mouseReleaseEvent(self, QMouseEvent):
        self.button_clicked_signal.emit()
    # 可在外部与槽函数连接
    def connect_customized_slot(self, func):
        self.button_clicked_signal.connect(func)

class CustomFolderDisplay(QWidget):
    #该类可以进行优化点击事件
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.table = ''
        self.draw()
    def draw(self):
        self.icon = QLabel(self)
        self.icon.setPixmap(QPixmap('folder.png'))
        self.icon.resize(22,22)
        self.icon.setScaledContents(True)
        self.name = QLabel(self)
        self.icon.move(5,3)
        self.name.move(35,8)
        
    def setName(self,name):
        self.name.setText(name)
    def getName(self):
        return self.name.text()
    def setHeaders(self,headers):
        self.headers = headers
    def setTable(self,table):
        self.table = table
        self.table.setItem(self.table.rowCount()-1,2,QTableWidgetItem('-'))
        self.table.setItem(self.table.rowCount()-1,3,QTableWidgetItem(time.strftime("%Y-%m-%d %H:%M",time.localtime())))
        self.table.setCellWidget(self.table.rowCount()-1,0,QCheckBox())
    def requestFolder(self,name):
        pass
        #r = requests.get('http://127.0.0.1:8080/createFolder?name='+name,headers=self.headers)
    def mouseDoubleClickEvent(self,e):
        self.table.setRowCount(0)