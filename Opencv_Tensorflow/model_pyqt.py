import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import QtCore

import cv2
import numpy as np
from keras.models import load_model


# 이미지 크기 조정 함수
def resize_image(image, target_size=(224, 224)):
    return cv2.resize(image, target_size)

class WebcamApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Webcam Object Detection')
        self.setGeometry(100, 100, 550, 350)
        
        main_layout = QHBoxLayout()  # 수평 상자 레이아웃 생성

        # 수직 상자 레이아웃 생성
        vertical_layout = QVBoxLayout()
        
        self.video_label = QLabel()
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        vertical_layout.addWidget(self.video_label)

        self.result_label = QLabel()
        self.result_label.setAlignment(QtCore.Qt.AlignCenter)
        vertical_layout.addWidget(self.result_label)

        # 시작 및 멈춤 버튼
        button_layout = QHBoxLayout()
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_webcam)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_webcam)
        button_layout.addWidget(self.stop_button)

        vertical_layout.addLayout(button_layout)

        main_layout.addLayout(vertical_layout)

        self.setLayout(main_layout)

        self.camera = None
        self.timer = QTimer()
        self.model = load_model("model/keras_Model.h5", compile=False)
        self.class_names = open("model/labels.txt", "r").readlines()
        
        # 테이블
        self.tableWidget = QTableWidget(self)
        self.tableWidget.resize(290, 50)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(5)
        
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)
        
        self.tableWidget.setColumnWidth(0, int(self.tableWidget.width() * 0.2))
        self.tableWidget.setColumnWidth(1, int(self.tableWidget.width() * 0.8))
        
        for i in range(5):
            # 프로그레스 바 추가
            widget = QWidget()
            layout = QVBoxLayout(widget)
            pbar = QProgressBar()
            pbar.setFixedHeight(20)
            pbar.setInvertedAppearance(True)  
            pbar.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            pbar.setStyleSheet("""
                QProgressBar {background-color : rgba(0, 0, 0, 0%);border : 1}
                QProgressBar::Chunk {background-color : rgba(0, 0, 255, 20%);border : 1}
            """)
            layout.addWidget(pbar)
            layout.setAlignment(Qt.AlignVCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            self.tableWidget.setCellWidget(i, 1, widget)
            
            name = self.class_names[i]
            class_name = name[2:-1]
            item = QTableWidgetItem(format(class_name))
            item.setTextAlignment(int(Qt.AlignRight|Qt.AlignVCenter))
            self.tableWidget.setItem(i, 0, item)
        
        main_layout.addWidget(self.tableWidget)

    def start_webcam(self):
        self.camera = cv2.VideoCapture(0)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

    def stop_webcam(self):
        if self.camera is not None:
            self.timer.stop()
            self.camera.release()
            self.video_label.clear()
            self.result_label.clear()

    def update_frame(self):
        ret, frame = self.camera.read()

        frame_resized = resize_image(frame)

        image = np.asarray(frame_resized, dtype=np.float32).reshape(1, 224, 224, 3)
        image = (image / 127.5) - 1

        prediction = self.model.predict(image)
        index = np.argmax(prediction)
        class_name = self.class_names[index]
        confidence_score = prediction[0][index]

        label = class_name[2:-1]
        score = np.round(confidence_score * 100)
        text = f"[ {label} : {score}% ]"

        height, width, channel = frame_resized.shape
        bytesPerLine = 3 * width
        qImg = QImage(frame_resized.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        self.video_label.setPixmap(pixmap)
        
        for i in range(5):
            confidence_score = prediction[0][i]
            score = np.round(confidence_score * 100)
            pbar = self.tableWidget.cellWidget(i, 1).layout().itemAt(0).widget()
            pbar.setValue(score)

        
        self.result_label.setText(text)  
        
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WebcamApp()
    ex.show()
    sys.exit(app.exec_())
