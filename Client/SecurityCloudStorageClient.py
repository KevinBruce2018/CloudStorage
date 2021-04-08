from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import requests
import os
import hashlib
import base64
from tools import AesTool
from contextlib import closing, redirect_stderr
from requests_toolbelt import MultipartEncoder
from requests_toolbelt.multipart import encoder
import _thread
import sys
import time

class SecurityCloudStorageClient(QTabWidget):
    def __init__(self):
        super().__init__()
        self.w = QWidget()
        self.processW = QWidget()
        self.addTab(self.w,'首页')
        self.addTab(self.processW,'传输进度')
        self.setGeometry(500,200,440,500)
        self.setIndexUI()
        self.setProcessUI()
        self.headers = {}
        self.data = {}
        self.filebox = []
    def setIndexUI(self):
        
        self.w.setGeometry(500,200,440,500)
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)

        self.w.setLayout(layout)
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
        layout.addWidget(btn_widget)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['文件名','文件大小','修改时间','操作'])
        layout.addWidget(self.table)
    def setProcessUI(self):
        layout = QVBoxLayout()
        self.upload_table = QTableWidget()
        layout.addWidget(self.upload_table)
        self.processW.setLayout(layout)
        self.upload_table.setColumnCount(4)
        self.upload_table.setHorizontalHeaderLabels(['文件名','文件大小','传输状态','速度'])
    def filelist(self):
        url = 'http://127.0.0.1:8080/getList/'
        r = requests.get(url,headers = self.headers)
        if r.status_code==403 or r.json()=={}:
            self.table.setRowCount(0)
            return None
        data = r.json()['files']
        self.table.setRowCount(len(data))
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()-1):
                self.table.setItem(i,j,QTableWidgetItem(str(data[i][j])))
        for i in range(self.table.rowCount()):
            self.filebox.append(QCheckBox())
            self.table.setCellWidget(i,self.table.columnCount()-1,self.filebox[i])
    def uploadFile(self):
        #完善filetype 不要直接image/png了
        path,fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(), 
        "All Files(*);;Text Files(*.txt)")
        if not path:
            return
        f = open(path,'rb')
        content = f.read()
        f.close()

        key = os.urandom(16)
        iv = os.urandom(16)
        self.data['hash'] = hashlib.md5(content).hexdigest()
        content = AesTool.encryt(content,key,iv)
        key = base64.b64encode(key)
        iv = base64.b64encode(iv)
        self.data['key'] = key
        self.data['key2'] = iv
        #filesize = len(content)
        filename = path.split('/')[-1]
        with open('.'+filename,'wb') as f:
            f.write(content)
        url = 'http://127.0.0.1:8080/upload/'
        fields={
                    'file': (path, open('.'+filename, 'rb'), "img/png")
                }|self.data
        #pbar = tqdm(total=filesize, unit='B', unit_scale=True)
        def my_callback(monitor):
            print(monitor.bytes_read)
            #pbar.update(monitor.bytes_read)
        e = encoder.MultipartEncoder(
                fields
            )
        m = encoder.MultipartEncoderMonitor(e, my_callback)
        r = requests.post(url, data=m,
                        headers=self.headers|{'Content-Type': m.content_type})
        print(r.text)
        os.remove('.'+filename)
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
        row = 0
        for i in range(self.table.rowCount()):
            if self.filebox[i].checkState()==Qt.Checked:
                filename = self.table.item(i,0).text()
                row+=1
                self.upload_table.setRowCount(row)
                self.upload_table.setItem(row-1,0,QTableWidgetItem(filename))
                self.bar = QProgressBar()
                self.upload_table.setCellWidget(row-1,2,self.bar)
                self.work = ProgressThread()
                self.work.setArgs(filename,self.headers,self.data)
                self.work.finish.connect(self.display)
                self.work.start()

        """
                content = b''
                with closing(requests.get('http://127.0.0.1:8080/download/?filename='+filename,headers=self.headers,stream=True)) as response:
                    chunk_size = 1024  # 单次请求最大值
                    content_size = int(response.headers['content-length'])  # 内容体总大小
                    data_count = 0
                    self.upload_table.setItem(row-1,1,QTableWidgetItem(str(content_size)))
                    bar = QProgressBar()
                    self.upload_table.setCellWidget(row-1,2,bar)
                    bar.setMaximum(content_size)
                    with open('下载/'+filename,'wb') as file:
                        for data in response.iter_content(chunk_size=chunk_size):
                            file.write(data)
                            content+=data
                            data_count = data_count + len(data)
                            now_jd = (data_count / content_size) * 100
                            bar.setValue(now_jd)
                            #print("\r 文件下载进度：%d%%(%d/%d) - %s" % (now_jd, data_count, content_size, filename), end=" ")

                r = requests.get('http://127.0.0.1:8080/getkey/?file='+filename,headers=self.headers)
                keys = r.json()
                key = keys["key"]
                key2 = keys['key2']
                with open('下载/'+filename,'wb') as f:  
                    content = AesTool.decrypt(content,base64.b64decode(key),base64.b64decode(key2))
                    f.write(content)
                """
    def display(self,ints,intv,intc):
        self.bar.setValue(ints)
        self.upload_table.setItem(0,3,QTableWidgetItem(str(intv)))
        self.upload_table.setItem(0,1,QTableWidgetItem(str(intc)))
    def delete(self):
        for i in range(self.table.rowCount()):
            if self.filebox[i].checkState()==Qt.Checked:
                filename = self.table.item(i,0).text()
                r = requests.get('http://127.0.0.1:8080/delete/?filename='+filename,headers=self.headers)
                #filelist 出现了bug 只剩一个的时候还会剩下那个文件的名字，离谱
                print(r.text)
        self.filelist()
    def share(self):
        for i in range(self.table.rowCount()):
            if self.filebox[i].checkState()==Qt.Checked:
                filename = self.table.item(i,0).text()
                r = requests.get('http://127.0.0.1:8080/share/?filename='+filename,headers=self.headers)
                #self.filelist()
                #filelist 出现了bug 只剩一个的时候还会剩下那个文件的名字，离谱
                print(r.text)

class ProgressThread(QThread):
    finish = pyqtSignal(int,int,int)
    def __init__(self):
        super().__init__()
    def setArgs(self,filename,headers,data):
        self.filename = filename
        self.headers = headers
        self.data={}
        self.data['csrfmiddlewaretoken'] = data
    def run(self):
        filename = self.filename
        content = b''
        with closing(requests.get('http://127.0.0.1:8080/download/?filename='+filename,headers=self.headers,stream=True)) as response:
            chunk_size = 1024  # 单次请求最大值
            content_size = int(response.headers['content-length'])  # 内容体总大小
            data_count = 0
            start = time.time()
            data_read = 0
            with open('下载/'+filename,'wb') as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    ends = time.time()-start
                    content+=data
                    data_count = data_count + len(data)
                    if ends>=1:
                        self.finish.emit(int(data_count/content_size*100),int((data_count-data_read)/1024),int(content_size/1024))
                        data_read = data_count
                        start = time.time()
        self.finish.emit(int(data_count/content_size*100),0,int(content_size/1024))
        r = requests.get('http://127.0.0.1:8080/getkey/?file='+filename,headers=self.headers)
        keys = r.json()
        key = keys["key"]
        key2 = keys['key2']
        with open('下载/'+filename,'wb') as f:  
            content = AesTool.decrypt(content,base64.b64decode(key),base64.b64decode(key2))
            f.write(content)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SecurityCloudStorageClient()
    window.setHeaders({'Cookie': 'csrftoken=9H7FU09VPdUw15XqrjQvHxempFdwEqxkjBqoiHLEeTpAblOi8xfKdWPkz6UhAdzN;sessionid=xldz406z7fdsll6avrykuznoia2zz3yf;'})
    window.setData('8XyfOcorowEbiynJv9IYf78EdLrZMx6ciRRYcT0aNc9fsOeBcn7dLwJCnc8KIk8F')
    window.show()
    window.filelist()
    sys.exit(app.exec_())