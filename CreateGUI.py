import cv2
import datetime
import os
import pandas as pd
import pywinusb.hid as hid
from PyQt5.QtCore import QTimer, Qt, QDateTime, QDate
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QSizePolicy,
                             QDesktopWidget, QMessageBox, QLabel, QHBoxLayout, QDateEdit, QLineEdit,
                             QComboBox, QPlainTextEdit)

Packet = []


class rPPG_GUI(QWidget):
    def __init__(self):
        super().__init__()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_time = 0

        self.init_ui()

    def init_ui(self):
        info_text = ('[실험 안내]'
                     '\n! 이름 입력 시 반드시 ex를 따라 영어로 입력해주세요 !'
                     '\n1) ubpulse 센서에 검지 손가락을 삽입해주세요.'
                     '\n2) 센서의 측정이 종료되면 Start 버튼을 눌러주세요.'
                     '\n * 센서의 측정이 완료되지 않고 도중 Low Blood Perfusion 또는 Abnormal Heartbeart '
                     '\n   문구가 나타나면 바로 Start 버튼을 눌러주세요.'
                     '\n3) \"측정이 완료되었습니다.\" 창이 뜨기 전까지 자세를 유지해주세요.'
                     '\n4) 화면 하단의 타이머에 얼굴이 가려지지 않도록 자세를 유지해주세요.'
                     '\n5) 측정 시간은 약 90초입니다.')

        info_display = QPlainTextEdit(self)
        info_display.setPlainText(info_text)
        info_display.setReadOnly(True)

        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_button_clicked)

        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.clicked.connect(self.cancel_button_clicked)

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
        self.personal_info_layout.addSpacing(15)
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
        self.personal_info_layout.addSpacing(50)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.personal_info_layout)
        main_layout.addWidget(info_display)
        # main_layout.addLayout(timer_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.setWindowTitle('rPPG Test')
        self.setGeometry(1000, 450, 1000, 900)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def start_button_clicked(self):
        name = self.name_edit.text()
        age = self.age_edit.text()
        gender = self.gender_combo.currentText()
        disease = self.disease_combo.currentText()
        date = self.date_edit.text()

        info_folder = "Data/" + name
        info_file_path = info_folder + "/SubjectInfo.txt"

        if not os.path.exists(info_folder):
            os.makedirs(info_folder)

        with open(info_file_path, 'a') as file:
            file.write(f"Name: {name}\n")
            file.write(f"Age: {age}\n")
            file.write(f"Gender: {gender}\n")
            file.write(f"Disease: {disease}\n")
            file.write(f"Date: {date}\n")

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
        # self.timer_label.setText(f'측정 중: {elapsed_time} seconds')
        QApplication.processEvents()

    def date_button_clicked(self):
        pass

    def cancel_button_clicked(self):
        self.close()

    def read_handler(self, data):
        # print("Raw data: {0}".format(data))

        # 시간 확인
        date = str(datetime.datetime.now()).split(' ')
        sliced_data = data[0:10]
        sliced_data.append(date[1])
        Packet.append(sliced_data)

    def main(self, experiment_name):
        experiment_time = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        duration = datetime.timedelta(seconds=5)

        folder = "Data/" + experiment_name + '/'

        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FPS, 30)

        if not cap.isOpened():
            print("Can't open Camera")
            exit()

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
                end_time = start_time + duration
                while end_time >= datetime.datetime.now():
                    ret, frame = cap.read()
                    font = cv2.FONT_HERSHEY_SIMPLEX

                    if not ret:
                        print("Can't read frame")
                        break

                    now = datetime.datetime.now().strftime("%H_%M_%S.%f")
                    real_frame = cv2.putText(frame, f'{self.elapsed_time}s', (580, 460), font, 1, (255, 255, 255), 3, cv2.LINE_4)
                    frame_time = now.split('.')[0] + '_' + now.split('.')[1]

                    frame_filename = folder + f'{frame_time}.png'
                    cv2.imwrite(frame_filename, frame)

                    cv2.imshow("Camera", real_frame)

                    if cv2.waitKey(1) == '27':
                        break

            finally:
                device.close()
                cap.release()
                cv2.destroyAllWindows()

                df = pd.DataFrame(Packet)
                df.to_csv(folder + experiment_time + '.csv')

            self.timer.stop()
            QMessageBox.information(self, 'Experiment Completed',
                                    '측정이 완료되었습니다.')
            self.start_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication([])
    window = rPPG_GUI()
    window.show()
    app.exec_()
