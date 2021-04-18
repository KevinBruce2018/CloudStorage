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
        self.setGeometry(300,200,780,480)
        self.setWindowTitle('后台管理系统')
        self.left = CustomTab(self)
        self.top = CustomCloudHeader(self)
        self.lock = self.top.lock
        self.unlock = self.top.unlock
        self.delete_btn = self.top.delete
        self.clear_btn = self.top.clear
        self.fresh = self.top.fresh
        self.search_line = self.top.search
        self.left.progress.clicked.connect(self.exit)
        self.fresh.clicked.connect(self.userList)
        self.delete_btn.clicked.connect(self.delete)
        self.unlock.clicked.connect(self.unlockuser)
        self.clear_btn.clicked.connect(self.clear)
        self.lock.clicked.connect(self.lockuser)
        self.table = QTableWidget(self)
        self.top.setTables(self.table)
        self.table.move(83,42)
        self.table.resize(680,435)
        self.table.setColumnCount(5)
        self.customHeader = CheckBoxHeader()
        self.customHeader.select_all_clicked.connect(self.customHeader.change_state)
        self.table.setHorizontalHeader(self.customHeader)
        self.table.setHorizontalHeaderLabels(['','用户名','用户状态','用户权限','上次修改时间'])
        self.table.setColumnWidth(0,25)
        self.table.setColumnWidth(1,130)
        self.table.setColumnWidth(2,70)
        self.table.setColumnWidth(3,228)
        self.table.setColumnWidth(4,225)
        self.table.verticalHeader().setVisible(False)

    def lockuser(self):
        url = 'http://127.0.0.1:8080/lockuser/'
        for i in range(len(self.userbox)):
            if self.userbox[i].checkState()==Qt.Checked:
                username = self.table.item(i,1).text()
                data = {}
                data['user'] = username
                data|=self.data
                r = requests.post(url=url,data=data,headers=self.headers)
        self.customHeader.isOn =False
        self.customHeader.updateSection(0)
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
        self.customHeader.isOn =False
        self.customHeader.updateSection(0)
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
            for j in range(self.table.columnCount()-2):
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
                username = self.table.item(i,1).text()
                data = {}
                data['user'] = username
                data|=self.data
                r = requests.post('http://127.0.0.1:8080/deluser/',data=data,headers=self.headers)
        self.customHeader.isOn =False
        self.customHeader.updateSection(0)
        self.userList()
    def clear(self):
        r = requests.get('http://127.0.0.1:8080/delunactive/',headers=self.headers)
        self.customHeader.isOn =False
        self.customHeader.updateSection(0)
        QMessageBox.information(self,'清理完成','未激活账号清理完成',QMessageBox.Yes)
        self.userList()
    def exit(self):
        r = requests.get('http://127.0.0.1:8080/logout/',headers=self.headers)
        self.close()
    def keyPressEvent(self, event):
        key = event.key()
        if key==Qt.Key_Return or key==Qt.Key_Enter:
            username = self.search_line.text()
            if username=='':
                self.userList()
                return
            url = 'http://127.0.0.1:8080/userlist/'
            r = requests.get(url,headers=self.headers)
            self.userbox.clear()
            flag = False
            data = r.json()['users']
            for i in range(len(data)):
                for j in range(self.table.columnCount()-2):
                    if j==0 and data[i][j]==username:
                        self.table.setRowCount(1)
                        data[i][2] = AuthorityFormat(data[i][2])
                        data[i][1] = StatusFormat(data[i][1])
                        self.userbox.append(QCheckBox())
                        self.table.setItem(0,j+1,QTableWidgetItem(str(data[i][j])))
                        self.table.setCellWidget(0,0,self.userbox[0])
                        self.customHeader.setCheckBox(self.userbox)
                        flag = True
                        break
                if flag:
                    break
            if not flag:
                self.table.setRowCount(0)
                
class CustomTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.addTab()
        self.draw()
        self.setFixedWidth(70)
        self.setFixedHeight(1000)

    def addTab(self):
        self.index_lab = QLabel('用户管理',self)
        self.index_lab.move(10,60)
        self.progress_lab = QLabel('   退出',self)
        self.progress_lab.setStyleSheet('color:#656d7c')
        self.index_lab.setStyleSheet('color:#656d7c')
        self.progress_lab.move(10,140)
        self.index = QPushButton('',self)
        self.progress = QPushButton('',self)
        self.index.move(17,10)
        self.progress.move(10,90)
        self.index.resize(38,38)
        self.progress.resize(50,50)
        self.progress.setStyleSheet('QPushButton{border-image:url(exit.png)}')
        self.index.setStyleSheet('QPushButton{border-image:url(user.png)}')
    def draw(self):
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Background,QColor(248,248,248))
        self.setAutoFillBackground(True)
        self.setPalette(pal)
class CustomCloudHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.addWidgets()
        self.draw()
    def addWidgets(self):
        self.lock = QPushButton('禁用',self)
        self.unlock = QPushButton('启用',self)
        self.delete = QPushButton('删除',self)
        self.fresh = QPushButton('刷新',self)
        self.clear = QPushButton('清理账号',self)
        self.search = QLineEdit(self)
        self.search_lab =  QLabel(self)
        self.search_lab.setPixmap(QPixmap('search.png'))
    def draw(self):
        self.lock.move(75,5)
        self.unlock.move(155,5)
        self.delete.move(235,5)
        self.fresh.move(315,5)
        self.clear.move(395,5)
        self.search.move(580,10)
        self.search_lab.move(550,10)
        self.search_lab.resize(25,25)
        self.search_lab.setScaledContents(True)
        self.search.setFixedWidth(180)
        
    def setTables(self,table):
        self.table = table


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdminClient()
    window.setHeaders({'Cookie': 'csrftoken=imcE85RGbnPdI59Up4EfFsLJNnYyeNT3n71UBRN2UggxhdqOPa9SaaP7A4M2dqXj;sessionid=lp7oxbadmcl86juyfxbrsscrzd9r7r2i;'})
    window.setData('DPLa6xGnf6KODveNXRBIqXIWeXIGNax3IAAqzjCJYZb8cDvHnX6lVFMk1EwaMNBj')
    window.show()
    window.userList()
    sys.exit(app.exec_())