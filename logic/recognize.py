import numpy as np
import dlib 
import cv2 
import sys
import time
sys.path.append("..")
from scipy.spatial import distance as dist 
from collections import OrderedDict

class Recognize():
    
    def __init__(self):
        self.init_data()
        self.init_model()
    def init_data(self):
        self.LANDMARKS = OrderedDict([
            ("mouth", (48, 68)),
            ("right_eyebrow", (17, 22)),
            ("left_eyebrow", (22, 27)),
            ("right_eye", (36, 42)),
            ("left_eye", (42, 48)),
            ("nose", (27, 36)),
            ("jaw", (0, 17))
        ])
        self.EYE_THRESH = 0.3
        self.EYE_FRAMES = 3
        self.COUNTER_FRAMES = 0
        self.TOTAL = 0
        self.MOUSE_UP_FRAMES = 5
        self.MOUSE_COUNTER_FRAMES = 0
        self.MOUSE_RATE = 0.8
        (self.lStart, self.lEnd) = self.LANDMARKS['left_eye']
        (self.rStart, self.rEnd) = self.LANDMARKS['right_eye']
        (self.mStart, self.mEnd) = self.LANDMARKS['mouth']

    def cal_height(self, points):
        leftEye = points[self.lStart: self.lEnd]
        rightEye = points[self.rStart: self.rEnd]
        leftEAR = self.eye_aspect_ratio(leftEye)
        rightEAR = self.eye_aspect_ratio(rightEye)
        return (leftEAR + rightEAR)/2
    
    def cal_mouse_height(self, points):
        mouse = points[self.mStart: self.mEnd]
        mouse_rate = self.mouse_aspect_ratio(mouse)
        return mouse_rate
    
    def mouse_aspect_ratio(self, mouse):
        A = dist.euclidean(mouse[2],mouse[9])
        B = dist.euclidean(mouse[4],mouse[7])
        C = dist.euclidean(mouse[0],mouse[6])
        return (A+ B) / (2 * C)
    def eye_aspect_ratio(self, eye):
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        return (A + B) / (2 * C)

    def init_model(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('F:/python/ML/11-learn/tired/model_data/shape_predictor_68_face_landmarks.dat')

    def init_video_capture(self, method):
        if method == 0:
            self.capture = cv2.VideoCapture(0)
        else:
            self.capture = cv2.VideoCapture(method)
    
    def skim_video(self, img, ha, eye, warn):
            img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            # 人脸数rects
            rects = self.detector(img_gray, 0)
            close_eye = False
            for i in range(len(rects)):
                faces = self.predictor(img, rects[i]).parts()
                points = np.matrix([[p.x, p.y] for p in faces])
                rate = self.cal_height(points)  # 闭眼
                rate_mouse = self.cal_mouse_height(points) # 哈欠
                if rate_mouse > self.MOUSE_RATE and ha:
                    self.MOUSE_COUNTER_FRAMES += 1
                    if self.MOUSE_COUNTER_FRAMES >= self.MOUSE_UP_FRAMES:
                        print('打哈欠')
                        cv2.putText(img, "haha", (rects[i].left(), rects[i].top() - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255))   
                        
                if rate < self.EYE_THRESH and eye:
                    self.COUNTER_FRAMES += 1
                    # print('闭眼检测到了，第%s次'%COUNTER_FRAMES)
                    if self.COUNTER_FRAMES >= 5:
                        self.TOTAL += 1
                        self.COUNTER_FRAMES = 0
                        close_eye = True
                else:
                    self.COUNTER_FRAMES = 0
                # for idx, point in enumerate(points):
                #     pos = (point[0, 0], point[0, 1])
                #     cv2.circle(img, pos, 2, (0, 0, 255), 1)
                #     cv2.putText(img, str(idx + 1), pos, cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255))  
                if self.TOTAL >= 10 and warn:
                        cv2.rectangle(img, (rects[i].left(), rects[i].top()), (rects[i].right(), rects[i].bottom()), color= (255, 0, 255))
                        cv2.putText(img, "tired", (rects[i].left(), rects[i].top() - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255))   
                        print('warning， 您已疲劳，请尽快休息')    
            return "%s闭眼"%time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) if close_eye else "", img
# print('结束检测，检测到了%s次疲劳闭眼'%TOTAL)