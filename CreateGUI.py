import cv2
import datetime
import os
import pandas as pd
import pywinusb.hid as hid
from PyQt5.QtCore import QTimer, Qt, QDateTime, QDate
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QSizePolicy,
                             QDesktopWidget, QMessageBox, QLabel, QHBoxLayout, QDateEdit, QLineEdit,
                             QComboBox)

Packet = []

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

        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.clicked.connect(self.cancel_button_clicked)

        self.timer_label = QLabel('측정 중: 0 seconds  ', self)
        self.timer_label.setAlignment(Qt.AlignCenter)

        self.date_edit = QDateEdit(self)
        self.date_edit.setDisplayFormat("dddd, MMMM d, yyyy")
        self.date_edit.setMinimumDate(QDate(2024, 1, 1))

        self.name_edit = QLineEdit(self)
        self.age_edit = QLineEdit(self)
        self.gender_combo = QComboBox(self)
        self.disease_combo = QComboBox(self)
        self.gender_combo.addItems(['남성', '여성'])
        self.disease_combo.addItems(['심장 및 혈관 관련 질환 있음', '없음'])

        self.start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.start_button.setMinimumSize(200, 50)
        self.start_button.setMaximumSize(100, 50)

        self.cancel_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cancel_button.setMinimumSize(200, 50)
        self.cancel_button.setMaximumSize(100, 50)

        self.personal_info_layout = QVBoxLayout()
        self.personal_info_layout.addWidget(QLabel('Personal Information'))
        self.personal_info_layout.addWidget(QLabel('Name (ex. 홍길동 -> HGD):'))
        self.personal_info_layout.addWidget(self.name_edit)
        self.personal_info_layout.addWidget(QLabel('Age:'))
        self.personal_info_layout.addWidget(self.age_edit)
        self.personal_info_layout.addWidget(QLabel('Gender:'))
        self.personal_info_layout.addWidget(self.gender_combo)
        self.personal_info_layout.addWidget(QLabel('Disease:'))
        self.personal_info_layout.addWidget(self.disease_combo)
        self.personal_info_layout.addWidget(QLabel('Date:'))
        self.personal_info_layout.addWidget(self.date_edit)
        self.personal_info_layout.addSpacing(10)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.cancel_button)

        timer_layout = QVBoxLayout()
        timer_layout.addWidget(self.timer_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.personal_info_layout)
        main_layout.addLayout(timer_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.setWindowTitle('rPPG Test')
        self.setGeometry(1000, 450, 1000, 800)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def start_button_clicked(self):
        info_text = ('1) 센서를 착용해주세요.'
                     '\n2) 센서의 HR 칸에 숫자가 시작되면 OK 버튼을 눌러주세요.'
                     '\n3) 측정 중 Low Blood Perfusion 또는 Abnormal Heartbeart 문구가 나타나도 측정이 완료될 때까지 자세를 유지해주세요.'
                     '\n4) 센서에서의 측적이 종료되어도 \'측정이 완료되었습니다.\' 창이 뜨기 전까지 자세를 유지해주세요.'
                     '\n5) 측정 시간은 약 90초입니다.')

        QMessageBox.information(self, '안내', info_text)

        name = self.name_edit.text()
        age = self.age_edit.text()
        gender = self.gender_combo.currentText()
        disease = self.disease_combo.currentText()
        date = self.date_edit.text()

        info_file_path = "Data/SubjectInfo.txt"

        with open(info_file_path, 'a') as file:
            file.write(f"Name: {name}\n")
            file.write(f"Age: {age}\n")
            file.write(f"Gender: {gender}\n")
            file.write(f"Disease: {disease}\n")
            file.write(f"Date: {date}\n")
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

    def date_button_clicked(self):
        pass

    def cancel_button_clicked(self):
        self.close()

    def read_handler(self, data):
        # print("Raw data: {0}".format(data))
        sliced_data = data[0:10]
        Packet.append(sliced_data)

    def main(self, experiment_name):
        experiment_time = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        duration = datetime.timedelta(seconds=20)

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

        vendor_num = 0x0f1f
        product_num = 0x0021

        ubpulse = hid.HidDeviceFilter(vendor_id=vendor_num, product_id=product_num)
        devices = ubpulse.get_devices()

        if devices:
            device = devices[0]
            device.open()
            device.set_raw_data_handler(self.read_handler)
            start_time = datetime.datetime.now()

            try:
                while True:
                    ret, frame = cap.read()
                    current_time = datetime.datetime.now()
                    out.write(frame)  # 프레임을 비디오 파일에 기록
                    cv2.imshow("Camera", frame)

                    if current_time - start_time >= duration:  # 지정된 시간이 지나면 종료
                        break

                    if not ret:
                        print("Can't read frame")
                        break

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
