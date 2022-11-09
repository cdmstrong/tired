



import argparse
import random
import sys
import time


sys.path.append("..")
from ui import detect
from logic.recognize import Recognize
import torch
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow
from functools import partial
import torch.backends.cudnn as cudnn
import cv2 as cv
import numpy as np
class METHOD():
        CAMERA = 0
        VIDEO = 1
# pyuic5 -o name.py test.ui
class UI_Logic_Window(QtWidgets.QMainWindow):
        def __init__(self, parent = None):
                super(UI_Logic_Window, self).__init__(parent)
                self.timer_video = QtCore.QTimer() # 创建定时器
                #创建一个窗口
                self.w = QMainWindow()
                self.ui = detect.Ui_DREAM_EYE()
                self.ui.setupUi(self)
                self.init_slots()
                self.output_folder = 'output/'
                self.cap = cv.VideoCapture()
                # 日志
                self.logging = ''
                self.recognize = Recognize()    
       # 控件绑定相关操作
        def init_slots(self):
                self.ui.tired_time.setValue(3)
                self.ui.tired_count.setValue(6)
                self.ui.eye.setChecked(True)
                self.ui.video.setChecked(True)
                
                self.ui.select_video.clicked.connect(self.button_video_open)
                self.ui.start_skim.clicked.connect(self.toggleState)
                self.ui.camera.clicked.connect(partial(self.change_method, METHOD.CAMERA))
                self.ui.video.clicked.connect(partial(self.change_method, METHOD.VIDEO))
                
                # self.ui.capScan.clicked.connect(self.button_camera_open)
                # self.ui.loadWeight.clicked.connect(self.open_model)
                # self.ui.initModel.clicked.connect(self.model_init)
                # self.ui.start_skim.clicked.connect(self.toggleState)
                # self.ui.end.clicked.connect(self.endVideo)
                #         # self.ui.pushButton_stop.clicked.connect(self.button_video_stop)
                #         # self.ui.pushButton_finish.clicked.connect(self.finish_detect)
                self.timer_video.timeout.connect(self.show_video_frame) # 定时器超时，将槽绑定至show_video_frame
                
        def change_method(self, type):
                if type == METHOD.CAMERA:
                   self.ui.select_video.setDisabled(True)
                else:
                   self.ui.select_video.setDisabled(False)
                        
        def button_image_open(self):
            print('button_image_open')
            name_list = []
            try:
                img_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件")
            except OSError as reason:
                print('文件出错啦')
                QtWidgets.QMessageBox.warning(self, 'Warning', '文件出错', buttons=QtWidgets.QMessageBox.Ok)
            else:
                if not img_name:
                   QtWidgets.QMessageBox.warning(self,"Warning", '文件出错', buttons=QtWidgets.QMessageBox.Ok)
                   self.log('文件出错')
                else:
                    img = cv.imread(img_name)
                    info_show = self.recognize.skim_video(img)
                    date = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) # 当前时间
                    file_extaction = img_name.split('.')[-1]
                    new_fileName = date + '.' + file_extaction
                    file_path = self.output_folder + 'img_output/' + new_fileName
                    cv.imwrite(file_path, img)
                    self.show_img(info_show, img)
                    
                #     self.log(info_show) #检测信息
                    
                #     self.result = cv.cvtColor(img, cv.COLOR_BGR2BGRA)
                    
                #     self.result =  letterbox(self.result, new_shape=self.opt.img_size)[0] #cv.resize(self.result, (640, 480), interpolation=cv.INTER_AREA)
                #     self.QtImg = QtGui.QImage(self.result.data, self.result.shape[1], self.result.shape[0], QtGui.QImage.Format_RGB32)
                #     print(type(self.ui.show))
                #     self.ui.show.setPixmap(QtGui.QPixmap.fromImage(self.QtImg))
                #     self.ui.show.setScaledContents(True) # 设置图像自适应界面大小
        def show_img(self, info_show, img):
                if info_show:
                    self.log(info_show)
                show = cv.resize(img, (640, 480)) # 直接将原始img上的检测结果进行显示
                self.result = cv.cvtColor(show, cv.COLOR_BGR2RGB)
                showImage = QtGui.QImage(self.result.data, self.result.shape[1], self.result.shape[0],
                                     QtGui.QImage.Format_RGB888)
                self.ui.capture.setPixmap(QtGui.QPixmap.fromImage(showImage))
                self.ui.capture.setScaledContents(True)  # 设置图像自适应界面大小
        def toggleState(self):
                print('toggle')
                state = self.timer_video.signalsBlocked()
                self.timer_video.blockSignals(not state)
                text = '继续' if not state else '暂停'
                self.ui.start_skim.setText(text)
        def endVideo(self):
                print('end')
                self.timer_video.blockSignals(True)
                self.releaseRes()
              
        def button_video_open(self):
                video_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择检测视频', './', filter="*.mp4;;*.avi;;All Files(*)")
                self.ui.video_path.setText(video_path)
                flag = self.cap.open(video_path)
                if not flag:
                        QtWidgets.QMessageBox.warning(self,"Warning", '打开视频失败', buttons=QtWidgets.QMessageBox.Ok)
                else: 
                        self.timer_video.start(1000/self.cap.get(cv.CAP_PROP_FPS)) # 以30ms为间隔，启动或重启定时器
                        # if self.opt.save:
                        #         fps, w, h, path = self.set_video_name_and_path()
                        #         self.vid_writer = cv.VideoWriter(path, cv.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
        def set_video_name_and_path(self):
                # 获取当前系统时间，作为img和video的文件名
                now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
                # if vid_cap:  # video
                fps = self.cap.get(cv.CAP_PROP_FPS)
                w = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
                h = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))
                # 视频检测结果存储位置
                save_path = self.output_folder + 'video/' + now + '.mp4'
                return fps, w, h, save_path

        def button_camera_open(self):
                camera_num = 0
                self.cap = cv.VideoCapture(camera_num)
                if not self.cap.isOpened():
                        QtWidgets.QMessageBox.warning(self, u"Warning", u'摄像头打开失败', buttons=QtWidgets.QMessageBox.Ok)
                else:
                        self.timer_video.start(1000/60)
                        if self.opt.save:
                                fps, w, h, path = self.set_video_name_and_path()
                                self.vid_writer = cv.VideoWriter(path, cv.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                        
        def open_model(self):
                self.openfile_name_model, _ = QFileDialog.getOpenFileName(self, '选择权重文件', directory='./yolov5\yolo\YoloV5_PyQt5-main\weights')
                print(self.openfile_name_model)
                if not self.openfile_name_model:
                #    QtWidgets.QMessageBox.warning(self, u"Warning" u'未选择权重文件，请重试', buttons=QtWidgets.QMessageBox.Ok)
                   self.log("warining 未选择权重文件，请重试")
                else :
                   print(self.openfile_name_model)
                   self.log("权重文件路径为：%s"%self.openfile_name_model)
                pass
        
        def show_video_frame(self):
                name_list = []
                flag, img = self.cap.read()
                if img is None:
                       self.releaseRes() 
                else:
                        close_eye, img = self.recognize.skim_video(img, self.ui.ha.checkState(), self.ui.eye.checkState(), self.ui.tired.checkState())
                        # if self.opt.save:
                        #         self.vid_writer.write(img) # 检测结果写入视频
                        self.show_img(close_eye, img)
        def releaseRes(self):
                        print('读取结束')
                        self.log('检测结束')
                        self.timer_video.stop()
                        self.cap.release() # 释放video_capture资源
                        self.ui.show.clear()
                        if self.opt.save:
                                self.vid_writer.release()               
        def log(self, msg):
                self.logging += '%s\n'%msg
                self.ui.log.setText(self.logging)
                self.ui.log.moveCursor(QtGui.QTextCursor.End)
if __name__=='__main__':
    # 创建QApplication实例
    app=QApplication(sys.argv)#获取命令行参数
    current_ui = UI_Logic_Window()
    current_ui.show()
    sys.exit(app.exec_())
    