import cv2
import datetime
import os
import pandas as pd
import pywinusb.hid as hid
from PyQt5.QtCore import QTimer, Qt, QDateTime
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QSizePolicy,
                             QDesktopWidget, QInputDialog, QMessageBox, QLabel, QHBoxLayout)


class rPPG_GUI(QWidget):
    def __init__(self):
        super().__init__()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_time = 0

        self.init_ui()

    def init_ui(self):
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_button_clicked)

        self.timer_label = QLabel('측정 중: 0 seconds  ', self)
        self.timer_label.setAlignment(Qt.AlignCenter)

        self.start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.start_button.setMinimumSize(200, 50)
        self.start_button.setMaximumSize(100, 50)

        timer_layout = QHBoxLayout()
        timer_layout.addWidget(self.start_button)
        timer_layout.addStretch()
        timer_layout.addWidget(self.timer_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(timer_layout)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

        self.setWindowTitle('rPPG Test')
        self.setGeometry(1000, 450, 500, 100)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def start_button_clicked(self):
        name, ok_name = QInputDialog.getText(self, 'Name', '이름을 입력하세요 (ex. 홍길동 -> HGD) :')
        age, ok_age = QInputDialog.getInt(self, 'Age', '나이를 입력하세요:')
        gender_items = ['남성', '여성']
        gender, ok_gender = QInputDialog.getItem(self, 'Gender', '성별 선택:', gender_items, 0, False)
        disease, ok_disease = QInputDialog.getText(self, 'Disease', '질병 정보 입력:')

        if ok_name and ok_age and ok_gender and ok_disease:
            QMessageBox.information(self, '안내', '1) 센서를 착용해주세요.'
                                                        '\n2) HR 칸에 숫자가 시작되면 OK 버튼을 눌러주세요.'
                                                        '\n3) 측정 중 Low Blood Perfusion 또는 Abnormal Heartbeart 문구가 나타나도 측정이 완료될 때까지 자세를 유지해주세요.'
                                                        '\n4) 센서에서의 측적이 종료되어도 \'측정이 완료되었습니다.\' 창이 뜨기 전까지 자세를 유지해주세요.'
                                                        '\n5) 측정 시간은 약 90초입니다.')
            info_file_path = "Data/SubjectInfo.txt"
            with open(info_file_path, 'a') as file:
                file.write(f"Name: {name}\n")
                file.write(f"Age: {age}\n")
                file.write(f"Gender: {gender}\n")
                file.write(f"Disease: {disease}\n")
                file.write("-" * 20 + "\n")

            self.start_button.setEnabled(False)
            self.start_timer()
            self.main(name)

    def start_timer(self):
        self.start_time = QDateTime.currentDateTime()
        self.timer.start(1000)  # ms 단위

    def update_timer(self):
        current_time = QDateTime.currentDateTime()
        elapsed_time = self.start_time.secsTo(current_time)
        self.elapsed_time = elapsed_time
        self.timer_label.setText(f'측정 중: {elapsed_time} seconds  ')
        QApplication.processEvents()

    def read_handler(self, data):
        # print("Raw data: {0}".format(data))
        sliced_data = data[0:10]
        Packet.append(sliced_data)


    def main(self, experiment_name):
        experiment_time = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        duration = datetime.timedelta(seconds=10)

        folder = "Data/" + experiment_name + '/'

        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

        if not cap.isOpened():
            print("Can't open Camera")
            exit()

        # 비디오 저장을 위한 설정
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(folder + experiment_time + '.avi', fourcc, 30.0, (640, 480))

        if not os.path.exists(folder):
            os.makedirs(folder)

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
                    cv2.imshow("Camera", frame)

                    if cv2.waitKey(1) == 27:
                        break

            except KeyboardInterrupt:
                pass

            device.close()

            df = pd.DataFrame(Packet)
            df.to_csv(folder + experiment_time + '.csv')

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        self.timer.stop()
        QMessageBox.information(self, 'Experiment Completed',
                                '측정이 완료되었습니다.')
        self.start_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication([])
    window = rPPG_GUI()
    window.show()
    app.exec_()
