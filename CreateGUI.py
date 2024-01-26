import cv2
import datetime
import os
import pandas as pd
import pywinusb.hid as hid
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QTextCursor, QImage, QPixmap
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QSizePolicy, QDesktopWidget, QTextEdit, QInputDialog, QMessageBox, QLabel)


class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_button_clicked)

        self.camera_label = QLabel(self)
        self.camera_label.setAlignment(Qt.AlignCenter)

        self.start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.start_button.setMinimumSize(200, 50)
        self.start_button.setMaximumSize(100, 50)

        self.raw_data_text = QTextEdit(self)
        self.raw_data_text.setReadOnly(True)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.start_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.raw_data_text)
        main_layout.addWidget(self.camera_label)
        main_layout.addLayout(button_layout)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

        self.setWindowTitle('rPPG Test')
        self.setGeometry(1000, 450, 1000, 1000)
        self.center()

        self.capture = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.timer_camera = QTimer(self)
        self.timer_camera.timeout.connect(self.show_camera)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def start_button_clicked(self):
        experiment_name, ok_pressed = QInputDialog.getText(self, 'Name', '이름을 입력하세요 (ex. 홍길동 -> HGD) :')
        if ok_pressed and experiment_name:
            self.start_button.setEnabled(False)
            self.timer_camera.start(30)
            self.main(experiment_name)

    def read_handler(self, data):
        # print("Raw data: {0}".format(data))
        sliced_data = data[0:10]
        raw_data = "Raw data: {0}".format(sliced_data)
        self.raw_data_text.append(raw_data)
        Packet.append(sliced_data)

        # Scroll to the bottom to show the latest data
        cursor = self.raw_data_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.raw_data_text.setTextCursor(cursor)

    def show_camera(self):
        success, frame = self.capture.read()
        if success:
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            q_image = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.camera_label.setFixedSize(640, 480)
            self.camera_label.setPixmap(pixmap)
            self.camera_label.setScaledContents(True)

    def main(self, experiment_name):
        experiment_time = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        duration = datetime.timedelta(seconds=30)

        Face_data_folder = "Data/Face/" + experiment_name + '/'
        PPG_data_folder = "Data/PPG/" + experiment_name + '/'

        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

        if not cap.isOpened():
            print("Can't open Camera")
            exit()

        # 비디오 저장을 위한 설정
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(Face_data_folder + experiment_time + '.avi', fourcc, 30.0, (640, 480))

        if not os.path.exists(Face_data_folder):
            os.makedirs(Face_data_folder)
        if not os.path.exists(PPG_data_folder):
            os.makedirs(PPG_data_folder)

        global Packet
        Packet = []
        vendor_num = 0x0f1f
        product_num = 0x0021

        start_time = datetime.datetime.now()
        ubpulse = hid.HidDeviceFilter(vendor_id=vendor_num, product_id=product_num)
        devices = ubpulse.get_devices()

        if devices:
            device = devices[0]
            device.open()
            device.set_raw_data_handler(self.read_handler)

            try:
                while True:
                    current_time = datetime.datetime.now()
                    if current_time - start_time > duration:  # 지정된 시간이 지나면 종료
                        break

                    ret, frame = cap.read()
                    if not ret:
                        print("Can't read frame")
                        break

                    out.write(frame)  # 프레임을 비디오 파일에 기록
                    # cv2.imshow("Camera", frame)

                    if cv2.waitKey(1) == 27:
                        break

            except KeyboardInterrupt:
                pass

            device.close()

            df = pd.DataFrame(Packet)
            df.to_csv(PPG_data_folder + experiment_time + '.csv')

        self.capture.release()
        self.timer_camera.stop()

        # Show a message after the main functionality has finished
        QMessageBox.information(self, 'Experiment Completed',
                                '측정이 완료되었습니다')
        self.start_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication([])
    window = MyApp()
    window.show()
    app.exec_()
  
