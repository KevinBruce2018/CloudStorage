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
from tools import AesTool
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
        self.pic.setPixmap(QPixmap('logo3.png'))
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
        self.vcode_label = MyQLabel()
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
                self.mainwindow.setData(self.data['csrfmiddlewaretoken'])

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
class SecurityCloudStorageClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setUI()
        self.headers = {}
        self.data = {}
        self.filebox = []
    def setUI(self):
        
        self.setGeometry(500,200,440,500)
        self.layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)

        self.setLayout(self.layout)
        self.upload = QPushButton('上传')
        self.down = QPushButton('下载')
        self.delete_btn = QPushButton('删除')
        self.share_btn = QPushButton('分享')

        btn_layout.addWidget(self.upload)
        btn_layout.addWidget(self.down)
        self.down.clicked.connect(self.download)
        btn_layout.addWidget(self.delete_btn)
        self.delete_btn.clicked.connect(self.delete)
        btn_layout.addWidget(self.share_btn)
        self.share_btn.clicked.connect(self.share)
        self.upload.clicked.connect(self.uploadFile)
        self.layout.addWidget(btn_widget)
        self.table = QTableWidget()
        
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['文件名','文件大小','修改时间','操作'])
        self.layout.addWidget(self.table)

    def filelist(self):
        url = 'http://127.0.0.1:8080/getList/'
        #print(self.headers)
        #print(self.data)
        r = requests.get(url,headers = self.headers)
        if r.status_code==403 or r.json()=={}:
            for j in range(self.table.columnCount()):
                self.table.setItem(0,j,QTableWidgetItem(''))
            return None
        data = r.json()['files']
        self.table.setRowCount(len(data))
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()-1):
                self.table.setItem(i,j,QTableWidgetItem(str(data[i][j])))
        for i in range(self.table.rowCount()):
            self.filebox.append(QCheckBox())
            self.table.setCellWidget(i,self.table.columnCount()-1,self.filebox[i])
        #print(self.data)
        #print(self.headers)
    def uploadFile(self):
        #upload
        path,fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(), 
        "All Files(*);;Text Files(*.txt)")
        print(fileType)
        f = open(path,'rb')
        files = {"file": (path, f, "img/png")}
        
        content = f.read()
        f.close()
        #filesize = len(content)
        #data
        key = os.urandom(16)
        iv = os.urandom(16)
        self.data['hash'] = hashlib.md5(content).hexdigest()
        content = AesTool.encryt(content,key,iv)
        key = base64.b64encode(key)
        iv = base64.b64encode(iv)
        self.data['key'] = key
        self.data['key2'] = iv

        files = {"file": (path, content, "img/png")}
        url = 'http://127.0.0.1:8080/upload/'
        r = requests.post(url,headers=self.headers,data=self.data,files=files)
        #print(r.text)
        r = requests.get('http://127.0.0.1:8080/getkey/',headers=self.headers)
        #print(r.text)
        #if success
        self.filelist()
        
    def setHeaders(self,headers):
        self.headers = headers
    def setData(self,data):
        self.data['csrfmiddlewaretoken'] = data
    def download(self):
        #filename 考虑进行加密
        #直接使用filename有缺陷 最好是带上路径 或者是用ID进行表示
        if not os.path.exists('下载'):
            os.mkdir('下载')
        for i in range(self.table.rowCount()):
            if self.filebox[i].checkState()==Qt.Checked:
                filename = self.table.item(i,0).text()
                r = requests.get('http://127.0.0.1:8080/download/?filename='+filename,headers=self.headers)
                content = r.content
                r = requests.get('http://127.0.0.1:8080/getkey/?file='+filename,headers=self.headers)
                keys = r.json()
                key = keys["key"]
                key2 = keys['key2']
                content = AesTool.decrypt(content,base64.b64decode(key),base64.b64decode(key2))

                with open('下载/'+filename,'wb') as f:
                    f.write(content)

    def delete(self):
        for i in range(self.table.rowCount()):
            if self.filebox[i].checkState()==Qt.Checked:
                filename = self.table.item(i,0).text()
                r = requests.get('http://127.0.0.1:8080/delete/?filename='+filename,headers=self.headers)
                self.filelist()
                #filelist 出现了bug 只剩一个的时候还会剩下那个文件的名字，离谱
                print(r.text)
    def share(self):
        for i in range(self.table.rowCount()):
            if self.filebox[i].checkState()==Qt.Checked:
                filename = self.table.item(i,0).text()
                r = requests.get('http://127.0.0.1:8080/share/?filename='+filename,headers=self.headers)
                #self.filelist()
                #filelist 出现了bug 只剩一个的时候还会剩下那个文件的名字，离谱
                print(r.text)

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
        #widget_list[5].layout.addWidget(QLabel(' '))
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
        #attention
        self.vcode_lab.setPixmap(QPixmap('vcode.png'))
        self.submit_btn = QPushButton('提交')
        #widget_list[5].layout.addWidget(QLabel(' '))
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
        self.down = QPushButton('设为管理')
        self.delete_btn = QPushButton('删除')
        self.share_btn = QPushButton('取消管理')

        btn_layout.addWidget(self.lock)
        btn_layout.addWidget(self.down)
        #self.down.clicked.connect(self.download)
        btn_layout.addWidget(self.delete_btn)
        #self.delete_btn.clicked.connect(self.delete)
        btn_layout.addWidget(self.share_btn)
        #self.share_btn.clicked.connect(self.share)
        self.lock.clicked.connect(self.lockuser)
        self.layout.addWidget(btn_widget)
        self.table = QTableWidget()
        
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['用户名','用户角色','修改时间','操作'])
        self.layout.addWidget(self.table)
    def lockuser(self):
        url = 'http://127.0.0.1:8080/userlist/'
    def setHeaders(self,headers):
        self.headers = headers
    def setData(self,data):
        self.data['csrfmiddlewaretoken'] = data
    def userList(self):
        url = 'http://127.0.0.1:8080/userlist/'
        r = requests.get(url,headers=self.headers)
        #data = r.json()
        print(self.headers)
        print(r.text)
class Audit(QWidget):
    def __init__(self):
        super().__init__()
        self.headers = {}
        self.data = {}
        self.setUI()
    def setUI(self):
        self.setGeometry(500,200,750,500)
        self.layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)

        self.setLayout(self.layout)
        self.lock = QPushButton('哈哈')
        self.down = QPushButton('哈哈哈哈')
        self.delete_btn = QPushButton('哈哈')
        self.share_btn = QPushButton('哈哈哈哈')

        btn_layout.addWidget(self.lock)
        btn_layout.addWidget(self.down)
        #self.down.clicked.connect(self.download)
        btn_layout.addWidget(self.delete_btn)
        #self.delete_btn.clicked.connect(self.delete)
        btn_layout.addWidget(self.share_btn)
        #self.share_btn.clicked.connect(self.share)
        #self.lock.clicked.connect(self.lockuser)
        self.layout.addWidget(btn_widget)
        self.table = QTableWidget()
        self.setWindowTitle('审计服务')
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['操作时间','IP','操作主体','操作对象','操作','状态','结果'])
        self.layout.addWidget(self.table)
    def logList(self):
        url = 'http://127.0.0.1:8080/loglist/'
        r = requests.get(url,headers=self.headers)
        data = r.json()['logs']
        self.table.setRowCount(len(data))

        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                self.table.setItem(i,j,QTableWidgetItem(str(data[i][j])))
    def setHeaders(self,headers):
        self.headers = headers
    def setData(self,data):
        self.data['csrfmiddlewaretoken'] = data
if __name__ == '__main__':
    app = QApplication(sys.argv)
    #window = Audit()
    window = UI_MainWindow()
    #window = UserRegister()
    #window = AdminClient()
    """
    window = SecurityCloudStorageClient()
    window.setHeaders({'Cookie': 'csrftoken=TNYQBFIdXKHgqz0yt94V2cE4LpzGLJPa0jItOimNp5mr1yUXdrEV9KGvNHlmpF7B;sessionid=uyng5h4byacxcm34ws3ozetrk9mgoiqq;'})
    window.setData('hqLhgOUUpM8TwMbquK7O8hjtYnfBQLSCoWvUtryuR7N47L5Pe2HOfPlU0F1huHa3')
    
    window.filelist()
    """
    window.show()
    sys.exit(app.exec_())
    