from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import requests
import os
import hashlib
import base64
from CustomWidget import *
from tools import AesTool,FileSizeFormat,TimeFormat
from contextlib import closing
from requests_toolbelt import MultipartEncoder
from requests_toolbelt.multipart import encoder
import sys
import time
from urllib.parse import quote,unquote
from tools import *

class ClientIndex(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.resize(1400,1000)
        self.headers = {}
        self.data = {}
        self.filebox = []
        self.bar = []
        self.work= []
        self.draw()
    def draw(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.verticalHeader().setVisible(False)
        self.customHeader = CheckBoxHeader()
        self.customHeader.select_all_clicked.connect(self.customHeader.change_state)
        self.table.setHorizontalHeader(self.customHeader)
        self.table.setHorizontalHeaderLabels(['','文件名','文件大小','修改时间'])
        self.table.setColumnWidth(0,25)
        self.table.setColumnWidth(1,450)
        self.table.setColumnWidth(2,155)
        self.table.setColumnWidth(3,224)
        layout.addWidget(self.table)
    def setHeaders(self,headers):
        self.headers = headers
    def setData(self,data):
        self.data['csrfmiddlewaretoken'] = data
    def setMaxSize(self):
        self.table.setColumnWidth(0,25)
        self.table.setColumnWidth(1,850)
        self.table.setColumnWidth(2,190)
        self.table.setColumnWidth(3,285)
    def setOriginSize(self):
        self.table.setColumnWidth(0,25)
        self.table.setColumnWidth(1,450)
        self.table.setColumnWidth(2,155)
        self.table.setColumnWidth(3,226)
class RecycleHeader(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.data = {}
        self.addWidgets()
        self.draw()
    def addWidgets(self):
        self.restore = QPushButton('还原',self)
        self.delete = QPushButton('删除',self)
        self.clear = QPushButton('清空回收站',self)
    def draw(self):
        self.restore.move(5,0)
        self.delete.move(85,0)
        self.clear.move(165,0)
        self.clear.clicked.connect(self.clearBin)
    def setTables(self,table):
        self.table = table
    def clearBin(self):
        self.table.setRowCount(0)
        r = requests.get('http://127.0.0.1:8080/clearbin/',headers=self.headers)
    def setHeaders(self,headers):
        self.headers = headers
    def setData(self,data):
        self.data['csrfmiddlewaretoken'] = data
class RecycleTable(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.resize(1400,1000)
        self.headers = {}
        self.data = {}
        self.filebox = []
        self.bar = []
        self.work= []
        self.draw()
    def draw(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.verticalHeader().setVisible(False)
        self.customHeader = CheckBoxHeader()
        self.customHeader.select_all_clicked.connect(self.customHeader.change_state)
        self.table.setHorizontalHeader(self.customHeader)
        self.table.setHorizontalHeaderLabels(['','文件名','文件大小','修改时间'])
        self.table.setColumnWidth(0,25)
        self.table.setColumnWidth(1,450)
        self.table.setColumnWidth(2,155)
        self.table.setColumnWidth(3,224)
        layout.addWidget(self.table)
    def setHeaders(self,headers):
        self.headers = headers
    def setData(self,data):
        self.data['csrfmiddlewaretoken'] = data
    def setMaxSize(self):
        self.table.setColumnWidth(0,25)
        self.table.setColumnWidth(1,710)
        self.table.setColumnWidth(2,340)
        self.table.setColumnWidth(3,280)
    def setOriginSize(self):
        self.table.setColumnWidth(0,25)
        self.table.setColumnWidth(1,450)
        self.table.setColumnWidth(2,155)
        self.table.setColumnWidth(3,224)
class DownloadProgressThread(QThread):
    trigger = pyqtSignal(int,str,str,int)
    def __init__(self):
        super().__init__()
    def setArgs(self,filename,headers,data,bar):
        self.filename = filename
        self.headers = headers
        self.data={}
        self.data['csrfmiddlewaretoken'] = data
        self.bar = bar
    def run(self):
        filename = quote(self.filename)
        content = b''
        with closing(requests.get('http://127.0.0.1:8080/download/?filename='+filename,headers=self.headers,stream=True)) as response:
            chunk_size = 4096  # 单次请求最大值
            content_size = int(response.headers['content-length'])  # 内容体总大小
            data_count = 0
            start = time.time()
            data_read = 0
            with open('下载/'+unquote(filename),'wb') as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    ends = time.time()-start
                    content+=data
                    data_count = data_count + len(data)
                    if ends>=1:
                        self.trigger.emit(int(data_count/content_size*100),str(int((data_count-data_read)/1024))+'KB/s',FileSizeFormat(str(int(content_size))),self.bar)
                        data_read = data_count
                        start = time.time()
        self.trigger.emit(int(data_count/content_size*100),'下载完成',FileSizeFormat(str(int(content_size))),self.bar)
        r = requests.get('http://127.0.0.1:8080/getkey/?file='+filename,headers=self.headers)
        keys = r.json()
        key = keys["key"]
        key2 = keys['key2']
        with open('下载/'+unquote(filename),'wb') as f:  
            content = AesTool.decrypt(content,base64.b64decode(key),base64.b64decode(key2))
            f.write(content)
class UploadProgressThread(QThread):
    trigger = pyqtSignal(int,str,str,int)
    def __init__(self):
        super().__init__()
    def setArgs(self,filename,headers,data,bar,content,path):
        self.filename = filename
        self.headers = headers
        self.data={}
        self.data = data
        self.bar = bar
        self.content = content
        self.path = path
    def run(self):
        filesize = len(self.content)
        filename = self.filename
        with open('.'+filename,'wb') as f:
            f.write(self.content)
        url = 'http://127.0.0.1:8080/upload/'
        fields={
                    'file': (self.path, open('.'+filename, 'rb'), "img/png")
                }|self.data
        def my_callback(monitor):
            read_data = monitor.bytes_read
            #发送文件的同时携带了其他信息，所以会比实际的大
            if read_data>filesize:
                self.trigger.emit(100,'上传完成',FileSizeFormat(str(int(filesize))),self.bar)
            else:
                self.trigger.emit(int(read_data/filesize*100),'40M/s',FileSizeFormat(str(int(filesize))),self.bar)
        e = encoder.MultipartEncoder(
                fields
            )
        m = encoder.MultipartEncoderMonitor(e, my_callback)
        r = requests.post(url, data=m,
                        headers=self.headers|{'Content-Type': m.content_type})
        os.remove('.'+filename)

class ClientProgress(QTabWidget):
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.resize(1400,1000)
        self.setProcessUI()
        self.headers = {}
        self.data = {}
        self.filebox = []
        self.bar = []
    def setProcessUI(self):
        layout = QVBoxLayout()
        self.upload_table = QTableWidget()
        layout.addWidget(self.upload_table)
        self.setLayout(layout)
        self.upload_table.setColumnCount(4)
        self.upload_table.setHorizontalHeaderLabels(['文件名','文件大小','传输进度','状态'])
        self.upload_table.setColumnWidth(0,420)
        self.upload_table.setColumnWidth(1,155)
        self.upload_table.setColumnWidth(2,180)
    def setMaxSize(self):
        self.upload_table.setColumnWidth(0,630)
        self.upload_table.setColumnWidth(1,225)
        self.upload_table.setColumnWidth(2,270)
        self.upload_table.setColumnWidth(3,245)
    def setOriginSize(self):
        self.upload_table.setColumnWidth(0,420)
        self.upload_table.setColumnWidth(1,155)
        self.upload_table.setColumnWidth(2,180)
        self.upload_table.setColumnWidth(3,105)
class CustomCloudHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedWidth(1500)
        self.addWidgets()
        self.draw()
    def addWidgets(self):
        self.upload = QPushButton('上传',self)
        self.download = QPushButton('下载',self)
        self.share = QPushButton('分享',self)
        self.delete = QPushButton('删除',self)
        self.folder = QPushButton('新建文件夹',self)
        self.folder.clicked.connect(self.createFolder)
        self.back = QPushButton('后退',self)
        self.search = QLineEdit(self)
        self.search_lab =  QLabel(self)
    def draw(self):
        self.back.move(5,0)
        self.upload.move(85,0)
        self.download.move(165,0)
        self.share.move(245,0)
        self.delete.move(325,0)
        self.folder.move(405,0)
        self.search.move(680,5)
        self.search_lab.move(655,4)
        base_path = os.path.abspath(__file__).split('/')[:-1]
        search_path = '/'.join(base_path)+'/search.png'
        self.search_lab.setPixmap(QPixmap(search_path))
        self.search_lab.resize(25,25)
        self.search_lab.setScaledContents(True)
        self.search.setFixedWidth(180)
    def setTables(self,table):
        self.table = table
    def createFolder(self):
        count = self.table.rowCount()
        self.table.setRowCount(count+1)
        folder = CustomFolder()
        folder.setHeaders({'Cookie': 'csrftoken=co3uyvFWtsS3t2d7bc12cIjbOFVDbJsE05o9UU36kC1UFCEnZrPxavwUfC0FckaF;sessionid=a4ygoijaz5n57td8hr2ws37vflar328n;'})
        folder.setTable(self.table)
        self.table.setCellWidget(count,1,folder)
        folder.foldername.setFocus()
        
    def setMaxSize(self):
        self.search.move(1180,5)
        self.search_lab.move(1155,4)
    def setOriginSize(self):
        self.search.move(680,5)
        self.search_lab.move(655,4)
class CustomFolder(QWidget):
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
        self.name.setHidden(True)
        self.foldername = QLineEdit(self)
        self.foldername.move(35,8)
    def setName(self,name):
        self.name.setText(name)
    def setHeaders(self,headers):
        self.headers = headers
    def setData(self,data):
        self.data['csrfmiddlewaretoken'] = data
    def setTable(self,table):
        self.table = table
    def keyPressEvent(self, event):
        key = event.key()
        if key==Qt.Key_Return or key==Qt.Key_Enter:
            self.table.setItem(self.table.rowCount()-1,2,QTableWidgetItem('-'))
            self.table.setItem(self.table.rowCount()-1,3,QTableWidgetItem(time.strftime("%Y-%m-%d %H:%M",time.localtime())))
            self.table.setCellWidget(self.table.rowCount()-1,0,QCheckBox())
            self.foldername.close()
            name = self.foldername.text()
            self.requestFolder(name)
            self.setName(name)
            self.name.setHidden(False)
    def requestFolder(self,name):
        r = requests.get('http://127.0.0.1:8080/createFolder?name='+name,headers=self.headers)
    def mouseDoubleClickEvent(self,e):
        self.table.setRowCount(0)
class CustomTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.addTab()
        self.draw()
        self.setFixedWidth(70)
        self.setFixedHeight(1000)

    def addTab(self):
        self.index_lab = QLabel('   首页',self)
        self.progress_lab = QLabel('   传输',self)
        self.recycle_lab = QLabel(' 回收站',self)
        self.progress_lab.setStyleSheet('color:#656d7c')
        self.index_lab.setStyleSheet('color:#656d7c')
        self.recycle_lab.setStyleSheet('color:#656d7c')
        self.progress_lab.move(10,140)
        self.index_lab.move(10,60)
        self.recycle_lab.move(10,220)
        self.index = QPushButton('',self)
        self.progress = QPushButton('',self)
        self.recycle = QPushButton('',self)
        self.progress_btn = QPushButton('',self)
        self.index.move(10,10)
        self.progress.move(10,90)
        self.recycle.move(10,170)
        self.index.resize(45,45)
        self.progress.resize(55,55)
        self.recycle.resize(45,45)
        self.progress_btn.move(5,530)
        self.progress_btn.resize(60,35)
        self.vol = QLabel(self)
        self.vol.setText('0.05/5G')
        self.vol.move(11,555)
        self.vol.setStyleSheet('color:#656d7c')
        base_path = os.path.abspath(__file__).split('/')[:-1]
        progress_path = '/'.join(base_path)+'/trans.png'
        index_path = '/'.join(base_path)+'/cloud.png'
        recycle_path = '/'.join(base_path)+'/garbage.png'
        self.progress.setStyleSheet('QPushButton{border-image:url('+progress_path+')}')
        self.index.setStyleSheet('QPushButton{border-image:url('+index_path+')}')
        self.recycle.setStyleSheet('QPushButton{border-image:url('+recycle_path+')}')
        self.progress_btn.setStyleSheet('QPushButton{border-image:url(pro.png)}')
    def draw(self):
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Background,QColor(248,248,248))
        self.setAutoFillBackground(True)
        self.setPalette(pal)
class SecurityCloudStorageClient(QWidget):
    def __init__(self):
        super().__init__()
        self.data ={}
        self.headers = {}
        self.filebox = []
        self.delete_box = []
        self.files = []
        self.delete_files = []
        self.bar = []
        self.work= []
        self.draw()
        self.resize(945,585)
        self.setWindowTitle('安全云存储系统')
        self.addWidgets()
    def setHeaders(self,headers):
        self.headers = headers
    def setData(self,data):
        self.data['csrfmiddlewaretoken'] = data
    def draw(self):
        self.left = CustomTab(self)
        self.top = CustomCloudHeader(self)
        self.recycle_top = RecycleHeader(self)
        self.index = ClientIndex(self)
        self.progress = ClientProgress(self)
        self.recycle = RecycleTable(self)
        self.top.setTables(self.index.table)
        self.recycle_top.setTables(self.recycle.table)
        self.progress.move(70,0)
        self.progress.close()
        self.recycle.move(70,0)
        self.recycle.close()
        self.recycle_top.close()
        self.recycle.move(70,30)
        self.recycle_top.move(70,5)
        self.index.move(70,30)
        self.top.move(70,5)
        self.left.progress.clicked.connect(self.display1)
        self.left.index.clicked.connect(self.display2)
        self.left.recycle.clicked.connect(self.display3)
        self.recycle_top.delete.clicked.connect(self.deletefile)
        self.recycle_top.restore.clicked.connect(self.restore)
    def display1(self):
        self.index.close()
        self.progress.show()
        self.top.close()
        self.recycle.close()
        self.recycle_top.close()
    def display2(self):
        self.progress.close()
        self.index.show()
        self.top.show()
        self.recycle_top.close()
        self.recycle.close()
    def display3(self):
        self.progress.close()
        self.index.close()
        self.top.close()
        self.recycle.show()
        self.recycle_top.show()
        self.delete_list()
        self.recycle_top.setHeaders(self.headers)
        self.recycle_top.setData(self.data)
    def filelist(self):
        self.index.setHeaders(self.headers)
        self.index.setData(self.data['csrfmiddlewaretoken'])
        self.index.filelist()
    def addWidgets(self):
        self.upload = self.top.upload
        self.download_btn = self.top.download
        self.delete_btn = self.top.delete
        self.share_btn = self.top.share
        self.back = self.top.back
        self.upload.clicked.connect(self.uploadFile)
        self.download_btn.clicked.connect(self.download)
        self.delete_btn.clicked.connect(self.delete)
        self.share_btn.clicked.connect(self.share)
        self.back.clicked.connect(self.filelist)
        self.table = self.index.table
        self.customHeader = self.index.customHeader
        self.recycle_header = self.recycle.customHeader
        self.upload_table = self.progress.upload_table
    def filelist(self):
        url = 'http://127.0.0.1:8080/getList/'
        self.filebox.clear()
        self.files.clear()
        r = requests.get(url,headers = self.headers)
        if r.status_code==403:
            self.table.setRowCount(0)
            return None
        data = r.json()['files']
        data = clear_data(data)
        self.table.setRowCount(len(data))
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()-1):
                if j==0:
                    cfile = CustomFile()
                    cfile.setName(data[i][j])
                    self.files.append(cfile)
                    self.table.setCellWidget(i,j+1,cfile)
                elif j==1:
                    data[i][j] = FileSizeFormat(data[i][j])
                    self.table.setItem(i,j+1,QTableWidgetItem(str(data[i][j])))
                elif j==2:
                    data[i][j] = TimeFormat(data[i][j])
                    self.table.setItem(i,j+1,QTableWidgetItem(str(data[i][j])))    
        for i in range(self.table.rowCount()):
            self.filebox.append(QCheckBox())
            self.table.setCellWidget(i,0,self.filebox[i])
        self.customHeader.setCheckBox(self.filebox)
    def delete_list(self):
        url = 'http://127.0.0.1:8080/getList/'
        self.delete_box.clear()
        self.delete_files.clear()
        r = requests.get(url,headers = self.headers)
        if r.status_code==403:
            self.table.setRowCount(0)
            return None
        data = r.json()['files']
        data = delete_data(data)
        self.recycle.table.setRowCount(len(data))
        for i in range(self.recycle.table.rowCount()):
            self.delete_files.append(data[i][0])
            for j in range(self.recycle.table.columnCount()-1):
                if j==0:
                    cfile = CustomFile()
                    cfile.setName(data[i][j])
                    self.files.append(cfile)
                    self.recycle.table.setCellWidget(i,j+1,cfile)
                elif j==1:
                    data[i][j] = FileSizeFormat(data[i][j])
                    self.recycle.table.setItem(i,j+1,QTableWidgetItem(str(data[i][j])))
                elif j==2:
                    data[i][j] = TimeFormat(data[i][j])
                    self.recycle.table.setItem(i,j+1,QTableWidgetItem(str(data[i][j])))    
        for i in range(self.recycle.table.rowCount()):
            self.delete_box.append(QCheckBox())
            self.recycle.table.setCellWidget(i,0,self.delete_box[i])
        self.recycle.customHeader.setCheckBox(self.delete_box)

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
        #显示进度
        row = self.upload_table.rowCount()+1
        self.upload_table.setRowCount(row)
        self.upload_table.setItem(row-1,0,QTableWidgetItem(filename))
        self.bar.append(QProgressBar())
        self.upload_table.setCellWidget(row-1,2,self.bar[-1])
        self.work2 = UploadProgressThread()
        self.work2.setArgs(filename,self.headers,self.data,row-1,content,path)
        self.work2.trigger.connect(self.display)
        self.work2.start()
    def download(self):
        #filename 考虑进行加密
        #直接使用filename有缺陷 最好是带上路径 或者是用ID进行表示
        if not os.path.exists('下载'):
            os.mkdir('下载')
        row = self.upload_table.rowCount()
        for i in range(self.table.rowCount()):
            if self.filebox[i].checkState()==Qt.Checked:
                filename = self.files[i].name.text()
                row+=1
                self.upload_table.setRowCount(row)
                self.upload_table.setItem(row-1,0,QTableWidgetItem(filename))
                self.bar.append(QProgressBar())
                self.upload_table.setCellWidget(row-1,2,self.bar[-1])
                self.work.append(DownloadProgressThread())
                self.work[-1].setArgs(filename,self.headers,self.data,row-1)
                self.work[-1].trigger.connect(self.display)
                self.work[-1].start()

    def display(self,progress,speed,size,num):
        self.bar[num].setValue(progress)
        self.upload_table.setItem(num,1,QTableWidgetItem(str(size)))
        self.upload_table.setItem(num,3,QTableWidgetItem(str(speed)))
        if speed=='上传完成':
            time.sleep(0.1)
            self.filelist()
    def delete(self):
        check_flag = False
        delete_flag = True
        for i in range(self.table.rowCount()):
            if self.filebox[i].checkState()==Qt.Checked:
                check_flag = True
                filename = quote(self.files[i].name.text())
                r = requests.get('http://127.0.0.1:8080/delete/?filename='+filename+'&type=1',headers=self.headers)
                if r.status_code==200 and r.text !='ok':
                    QMessageBox.warning(self,'文件删除失败',r.text,QMessageBox.Yes)
                    delete_flag = False
                elif r.status_code==500:
                    print(r.text)
                    QMessageBox.warning(self,'文件删除失败','服务器异常',QMessageBox.Yes)
                    delete_flag = False
        if check_flag and delete_flag:
            QMessageBox.information(self,'文件删除成功','文件删除成功',QMessageBox.Yes)
        self.customHeader.isOn =False
        self.customHeader.updateSection(0)
        self.filelist()
    def deletefile(self):
        check_flag = False
        delete_flag = True
        for i in range(self.recycle.table.rowCount()):
            if self.delete_box[i].checkState()==Qt.Checked:
                check_flag = True
                filename = quote(self.delete_files[i])
                r = requests.get('http://127.0.0.1:8080/delete/?filename='+filename+'&type=2',headers=self.headers)
                if r.status_code==200 and r.text !='ok':
                    QMessageBox.warning(self,'文件删除失败',r.text,QMessageBox.Yes)
                    delete_flag = False
                elif r.status_code==500:
                    print(r.text)
                    QMessageBox.warning(self,'文件删除失败','服务器异常',QMessageBox.Yes)
                    delete_flag = False
        if check_flag and delete_flag:
            QMessageBox.information(self,'文件删除成功','文件删除成功',QMessageBox.Yes)
        self.recycle.customHeader.isOn = False
        self.recycle.customHeader.updateSection(0)
        self.delete_list()
    def share(self):
        text = ''
        for i in range(self.table.rowCount()):
            if self.filebox[i].checkState()==Qt.Checked:
                filename = self.files[i].name.text()
                r = requests.get('http://127.0.0.1:8080/share/?filename='+filename,headers=self.headers)
                text+='http://127.0.0.1:8080/sharedownload/?filename='+r.text+'\n'
        if text!='':
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(self,'分享成功','分享链接已复制到剪切板!',QMessageBox.Yes)
    def restore(self):
        for i in range(self.recycle.table.rowCount()):
            if self.delete_box[i].checkState()==Qt.Checked:
                filename = quote(self.delete_files[i])
                r = requests.get('http://127.0.0.1:8080/restore/?filename='+filename,headers=self.headers)
        QMessageBox.information(self,'文件恢复成功','文件恢复成功',QMessageBox.Yes)
        self.recycle.customHeader.isOn = False
        self.recycle.customHeader.updateSection(0)
        self.delete_list()
        self.filelist()
    def resizeEvent(self,event):
        if event.size().height()>=790:
            self.index.setMaxSize()
            self.top.setMaxSize()
            self.progress.setMaxSize()
            self.recycle.setMaxSize()
            self.left.progress_btn.move(5,730)
            self.left.vol.move(11,755)
        elif event.size().height()<=590:
            self.index.setOriginSize()
            self.top.setOriginSize()
            self.progress.setOriginSize()
            self.recycle.setOriginSize()
            self.left.progress_btn.move(5,530)
            self.left.vol.move(11,555)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SecurityCloudStorageClient()
    window.setHeaders({'Cookie': 'csrftoken=co3uyvFWtsS3t2d7bc12cIjbOFVDbJsE05o9UU36kC1UFCEnZrPxavwUfC0FckaF;sessionid=a4ygoijaz5n57td8hr2ws37vflar328n;'})
    window.setData('CwC14peXQsaTdUmtiM6j0PKz1IAq66XOqdXGqOC7HCjKpuNJ61UOYCXisFFs7HFP')
    window.show()
    window.filelist()
    sys.exit(app.exec_())