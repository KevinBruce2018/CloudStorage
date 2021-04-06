from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import requests
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
