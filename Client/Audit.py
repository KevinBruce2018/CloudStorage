from datetime import time
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from tools import TimeFormat, data_classify
import requests
import sys
class Audit(QWidget):
    def __init__(self):
        super().__init__()
        self.headers = {}
        self.data = {}
        self.setUI()
        self.moveWidgets()
        self.addClickedEvent()
    def setUI(self):
        self.setGeometry(320,150,890,550)
        self.setWindowTitle('审计服务')
        self.label_from = QLabel(self)
        self.label_to = QLabel(self)
        self.label_op = QLabel(self)
        self.label_from.setText('从')
        self.label_to.setText('到')
        self.label_op.setText('操作')
        self.labp1 = QLabel(self)
        self.labp1.setText('第')
        self.page_line = QLineEdit(self)
        self.labp2 = QLabel(self)
        self.page_line.setFixedWidth(25)
        self.page_line.setFixedHeight(20)
        self.labp2.setText('/10页')
        self.page_left = QPushButton('上一页',self)
        self.page_right = QPushButton('下一页',self)
        self.time_from = QDateTimeEdit(self)
        self.time_from.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.time_from.setMinimumDate(QDate.currentDate().addDays(-368))
        self.time_to = QDateTimeEdit(QDateTime.currentDateTime(),self)
        self.time_to.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.user_line = QLineEdit(self)
        self.user_line.setFixedWidth(140)
        self.choice_btn = QPushButton('查询',self)
        self.listall_btn = QPushButton('显示全部',self)
        self.lab_user = QLabel(self)
        self.lab_user.setText('用户')
        self.com = QComboBox(self)
        self.com.addItems(['所有操作','登录','注册','上传','下载','获取日志','删除'])
        self.table = QTableWidget(self)
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(8)
        self.table.setFixedSize(870,473)
        self.table.setColumnWidth(0,38)
        self.table.setColumnWidth(1,130)
        self.table.setColumnWidth(2,115)
        self.table.setColumnWidth(3,120)
        self.table.setColumnWidth(4,130)
        self.table.setColumnWidth(5,85)
        self.table.setColumnWidth(6,190)
        self.table.setColumnWidth(7,60)
        self.table.setHorizontalHeaderLabels(['序号','操作时间','IP','操作主体','操作对象','操作','状态','结果'])
    def moveWidgets(self):
        self.table.move(10,43)
        self.label_from.move(10,12)
        self.time_from.move(32,10)
        self.label_to.move(180,12)
        self.time_to.move(200,10)
        self.label_op.move(345,12)
        self.com.move(375,6)
        self.lab_user.move(480,12)
        self.user_line.move(510,10)
        self.listall_btn.move(710,6)
        self.choice_btn.move(810,6)
        self.labp1.move(380,525)
        self.page_line.move(400,525)
        self.labp2.move(430,525)
        self.page_left.move(280,518)
        self.page_right.move(480,518)
    def addClickedEvent(self):
        self.page_left.clicked.connect(self.leftPage)
        self.page_right.clicked.connect(self.rightPage)
        self.listall_btn.clicked.connect(self.logList)
        self.choice_btn.clicked.connect(self.search)
    def logList(self,page=None,data=None):
        if not data:
            url = 'http://127.0.0.1:8080/loglist/'
            r = requests.get(url,headers=self.headers)
            data = r.json()['logs']
        else:
            data = data
        self.raw_data = data
        if len(data)%15!=0:
            pages = int(len(data)/15)+1
        else:
            pages = int(len(data)/15)
        self.labp2.setText('/'+str(pages)+'页')
        datas = data_classify(data,pages)
        if not page:
            self.page_line.setText('1')
            data = datas[0]
            self.cur_page = 1
        elif page<=len(datas):
            self.page_line.setText(str(page))
            data = datas[page-1]
            self.cur_page = page
        self.table.setRowCount(len(data))
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()-1):
                if j==0:
                    data[i][j] = TimeFormat(data[i][j])
                self.table.setItem(i,j+1,QTableWidgetItem(str(data[i][j])))
                self.table.item(i,j+1).setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
            self.table.setItem(i,0,QTableWidgetItem(str(i+1)))
            self.table.item(i,0).setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
    def setHeaders(self,headers):
        self.headers = headers
    def setData(self,data):
        self.data['csrfmiddlewaretoken'] = data
    def keyPressEvent(self, e):
        key = e.key()
        if key==Qt.Key_Return or key==Qt.Key_Enter:
            page = self.page_line.text()
            if page=='':
                return
            else:
                self.logList(int(page))
    def leftPage(self):
        if self.cur_page-1>0:
            self.cur_page-=1
            self.logList(self.cur_page)
    def rightPage(self):
        self.logList(self.cur_page+1)
    def search(self):
        data = []
        op = self.com.currentText()
        username = self.user_line.text()
        time_from = self.time_from.text()
        time_to = self.time_to.text()
        for i in range(len(self.raw_data)):
            times = self.raw_data[i][0]
            if times<=time_to and times>=time_from:
                if username!='' and username==self.raw_data[i][2]:
                    if op=='所有操作' or op==self.raw_data[i][4]:
                        data.append(self.raw_data[i])
                    else:
                        continue
                elif username=='':
                    data.append(self.raw_data[i])
                else:
                    continue
            else:
                continue
        if len(data)%15!=0:
            pages = int(len(data)/15)+1
        else:
            pages = int(len(data)/15)
        data = data_classify(data,pages)
        self.searchList(page=None,data=data)
    def searchList(self,page=None,data=None):
        if len(data)%15!=0:
            pages = int(len(data)/15)+1
        else:
            pages = int(len(data)/15)
        self.labp2.setText('/'+str(pages)+'页')
        datas = data_classify(data,pages)
        if not page:
            self.page_line.setText('1')
            data = datas[0][0]
            self.cur_page = 1
        elif page<=len(datas):
            self.page_line.setText(str(page))
            data = datas[page-1]
            self.cur_page = page
        self.table.setRowCount(len(data))
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()-1):
                self.table.setItem(i,j+1,QTableWidgetItem(str(data[i][j])))
                self.table.item(i,j+1).setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
            self.table.setItem(i,0,QTableWidgetItem(str(i+1)))
            self.table.item(i,0).setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Audit()
    window.setHeaders({'Cookie': 'csrftoken=M091UcZM5ksmi4bZ10liFg3scgBWo74pR9qjDnqsm3h342QNR2gyGbVyHWOjXyvD;sessionid=ecxlq7kk9b0nx57osj8k70ixhhapektz;'})
    window.setData('VADmy5vfLTaLMQ4vwlJmN2OrUnqH8FnO0JUEhgWV2CZsyOJjmnECOXGxp3D4H6O2')
    window.show()
    window.logList()
    sys.exit(app.exec_())