from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from tools import TimeFormat
import requests
import sys
class Audit(QWidget):
    def __init__(self):
        super().__init__()
        self.headers = {}
        self.data = {}
        self.setUI()
    def setUI(self):
        self.setGeometry(320,200,790,500)
        self.layout = QVBoxLayout()
        menu_layout = QHBoxLayout()
        menu_widget = QWidget()
        menu_widget.setLayout(menu_layout)

        self.setLayout(self.layout)
        label_from = QLabel('从')
        label_to = QLabel('到')
        label_op = QLabel('操作')
        self.time_from = QDateTimeEdit()
        self.time_to = QDateTimeEdit()
        self.delete_btn = QPushButton('筛选')
        self.com = QComboBox()
        self.com.addItems(['登录','注册','上传','下载'])
        menu_layout.addWidget(label_from)
        menu_layout.addWidget(self.time_from)
        menu_layout.addWidget(label_to)
        menu_layout.addWidget(self.time_to)
        menu_layout.addWidget(label_op)
        menu_layout.addWidget(self.com)
        menu_layout.addWidget(self.delete_btn)
        self.layout.addWidget(menu_widget)
        self.table = QTableWidget()
        self.setWindowTitle('审计服务')
        self.table.setColumnCount(7)
        self.table.setColumnWidth(0,130)
        self.table.setHorizontalHeaderLabels(['操作时间','IP','操作主体','操作对象','操作','状态','结果'])
        self.layout.addWidget(self.table)
    def logList(self):
        url = 'http://127.0.0.1:8080/loglist/'
        r = requests.get(url,headers=self.headers)
        data = r.json()['logs']
        self.table.setRowCount(len(data))

        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                if j==0:
                    data[i][j] = TimeFormat(data[i][j])
                self.table.setItem(i,j,QTableWidgetItem(str(data[i][j])))
    def setHeaders(self,headers):
        self.headers = headers
    def setData(self,data):
        self.data['csrfmiddlewaretoken'] = data

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Audit()
    window.setHeaders({'Cookie': 'csrftoken=SdE9RYmao2jJ0pEFw5UMMIFnnzlz1Pzq4hufVUtPlkYms3jNUQvWODQDb6yZKy0H;sessionid=s2l8vos16jk0rs6qqagdzrw27q898kb3;'})
    window.setData('CHhd1FJee2AHSIW6iFHZgDgwDn32g8edOL7j5BQTbkfkkmBeGqi9iyrMrUgsZRFu')
    window.show()
    window.logList()
    sys.exit(app.exec_())