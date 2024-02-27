# from quart import Quart, request
# import filterLogin

# app = Quart(__name__)

# @app.route('/login')
# async def login():
#     await filterLogin.login()
#     return '结束抓取'
# if __name__ == '__main__':
#     app.run(port=8666)
    
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,QLineEdit,QLabel
from PyQt6.QtCore import QThread, QObject, pyqtSignal, pyqtSlot,Qt
import filterLogin
import asyncio
class Worker(QObject):
    # 定义一个用于更新UI的信号
    update_signal = pyqtSignal(str)
    def __init__(self, input_text,this):
        super().__init__()
        self.input_text = input_text
        self.this = this
        self.loop=''
        self.task=''
        self.status={
            'task':False
        }
    def run(self):
        self.loop = asyncio.new_event_loop()  # 创建事件循环
        self.task = self.loop.create_task(filterLogin.initMain(self.input_text,self.this,self.status))  # 创建一个任务
        self.loop.run_until_complete(self.task) 
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("弹幕抓取")
        self.setGeometry(100, 100, 400, 300)  # 设置窗口位置和大小
        self.label = QLabel("Hello, PyQt!", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置标签内容居中对齐
        self.input_box=QLineEdit(self)
        self.button = QPushButton("开始抓取", self)
        self.button.clicked.connect(self.handle_button_click)
        # 创建布局，并将标签、输入框和按钮添加到布局中
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input_box)
        layout.addWidget(self.button)
         # 创建一个小部件，并将布局设置为小部件的布局
        widget = QWidget()
        widget.setLayout(layout)
        # 设置主窗口的中心部件为小部件
        self.setCentralWidget(widget)
        
        
        
    def handle_button_click(self):
        # 处理按钮点击事件的逻辑
        input_text = self.input_box.text()
        if hasattr(self, 'worker'):
            print(self.worker.task)
            self.button.setText("开始抓取") 
            self.worker.status['task']=False
            # del self.worker
        else:
            self.worker = Worker('','')  # 创建 Worker 实例
            self.thread = QThread()  # 创建 QThread 实例
            self.worker.moveToThread(self.thread)  # 将 Worker 移动到新线程
            # 连接信号
            self.worker.update_signal.connect(self.updateUI)
            self.worker.status['task']=True
            self.label.setText("正在抓取直播间id: " + input_text) 
            self.button.setText("关闭抓取") 
            self.worker.input_text=input_text
            self.worker.this=self
            self.thread.started.connect(self.worker.run)
            self.thread.start()
            self.button.setEnabled(False)  # 防止多次点击
            self.input_box.setEnabled(False)  # 防止多次点击
    def updateUI(self, message):
        """更新UI的槽函数"""
        self.setWindowTitle(message)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setWindowIcon(QIcon('./images/Dragon.ico'))#设置窗体图标
    window = MyWindow()
    window.show()

    sys.exit(app.exec())