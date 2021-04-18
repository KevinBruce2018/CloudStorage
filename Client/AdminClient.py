from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import requests
from tools import *
import sys
from CustomWidget import CheckBoxHeader

class AdminClient(QWidget):
    def __init__(self):
        super().__init__()
        self.headers = {}
        self.data = {}
        self.userbox = []
        self.setUI()
        
    def setUI(self):
        self.setGeometry(500,200,500,500)
        self.layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)

        self.setLayout(self.layout)
        self.lock = QPushButton('禁用账号')
        self.unlock = QPushButton('启用账号')
        self.delete_btn = QPushButton('删除')
        self.clear_btn = QPushButton('清理账号')

        btn_layout.addWidget(self.lock)
        btn_layout.addWidget(self.unlock)
        btn_layout.addWidget(self.delete_btn)
        self.delete_btn.clicked.connect(self.delete)
        self.unlock.clicked.connect(self.unlockuser)
        self.clear_btn.clicked.connect(self.clear)
        btn_layout.addWidget(self.clear_btn)
        self.lock.clicked.connect(self.lockuser)
        self.layout.addWidget(btn_widget)
        self.table = QTableWidget()
        
        self.table.setColumnCount(4)
        self.customHeader = CheckBoxHeader()
        self.customHeader.select_all_clicked.connect(self.customHeader.change_state)
        self.table.setHorizontalHeader(self.customHeader)
        self.table.setHorizontalHeaderLabels(['','用户名','用户状态','用户权限'])
        self.table.setColumnWidth(1,130)
        self.table.setColumnWidth(2,70)
        self.table.setColumnWidth(3,228)
        self.table.setColumnWidth(0,30)
        self.table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.table)
    def lockuser(self):
        url = 'http://127.0.0.1:8080/lockuser/'
        for i in range(len(self.userbox)):
            if self.userbox[i].checkState()==Qt.Checked:
                username = self.table.item(i,1).text()
                data = {}
                data['user'] = username
                data|=self.data
                r = requests.post(url=url,data=data,headers=self.headers)
        self.userList()
    def unlockuser(self):
        url = 'http://127.0.0.1:8080/unlockuser/'
        for i in range(len(self.userbox)):
            if self.userbox[i].checkState()==Qt.Checked:
                username = self.table.item(i,1).text()
                data = {}
                data['user'] = username
                data|=self.data
                r = requests.post(url=url,data=data,headers=self.headers)
        self.userList()
    def setHeaders(self,headers):
        self.headers = headers
    def setData(self,data):
        self.data['csrfmiddlewaretoken'] = data
    def userList(self):
        url = 'http://127.0.0.1:8080/userlist/'
        r = requests.get(url,headers=self.headers)
        self.userbox.clear()
        data = r.json()['users']
        self.table.setRowCount(len(data))
        for i in range(len(data)):
            self.userbox.append(QCheckBox())
            for j in range(self.table.columnCount()-1):
                if j==2:
                    data[i][j] = AuthorityFormat(data[i][j])
                if j==1:
                    data[i][j] = StatusFormat(data[i][j])
                self.table.setItem(i,j+1,QTableWidgetItem(str(data[i][j])))
            self.table.setCellWidget(i,0,self.userbox[i])
        self.customHeader.setCheckBox(self.userbox)
    def delete(self):
        for i in range(len(self.userbox)):
            if self.userbox[i].checkState()==Qt.Checked:
                username = self.table.item(i,0).text()
                data = {}
                data['user'] = username
                data|=self.data
                r = requests.post('http://127.0.0.1:8080/deluser/',data=data,headers=self.headers)
        self.userList()
    def clear(self):
        r = requests.get('http://127.0.0.1:8080/delunactive/',headers=self.headers)
        self.customHeader.updateSection(3)
        self.customHeader.paintSection()
        self.userList()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdminClient()
    window.setHeaders({'Cookie': 'csrftoken=imcE85RGbnPdI59Up4EfFsLJNnYyeNT3n71UBRN2UggxhdqOPa9SaaP7A4M2dqXj;sessionid=lp7oxbadmcl86juyfxbrsscrzd9r7r2i;'})
    window.setData('DPLa6xGnf6KODveNXRBIqXIWeXIGNax3IAAqzjCJYZb8cDvHnX6lVFMk1EwaMNBj')
    window.show()
    window.userList()
    sys.exit(app.exec_())