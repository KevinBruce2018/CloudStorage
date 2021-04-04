from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import requests
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
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.share_btn)
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