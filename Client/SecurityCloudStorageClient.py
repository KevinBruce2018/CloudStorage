from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import requests
import os
import hashlib
import base64
from tools import AesTool
from contextlib import closing

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
                content = b''
                with closing(requests.get('http://127.0.0.1:8080/download/?filename='+filename,headers=self.headers,stream=True)) as response:
                    chunk_size = 1024  # 单次请求最大值
                    content_size = int(response.headers['content-length'])  # 内容体总大小
                    data_count = 0
                    with open('下载/'+filename,'wb') as file:
                        for data in response.iter_content(chunk_size=chunk_size):
                            file.write(data)
                            content+=data
                            data_count = data_count + len(data)
                            now_jd = (data_count / content_size) * 100
                            print("\r 文件下载进度：%d%%(%d/%d) - %s" % (now_jd, data_count, content_size, filename), end=" ")

                r = requests.get('http://127.0.0.1:8080/getkey/?file='+filename,headers=self.headers)
                keys = r.json()
                key = keys["key"]
                key2 = keys['key2']
                print(keys)
                with open('下载/'+filename,'wb') as f:  
                    content = AesTool.decrypt(content,base64.b64decode(key),base64.b64decode(key2))
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
