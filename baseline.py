import cv2
import datetime
import os
import pandas as pd
import pywinusb.hid as hid

experiment_time = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
duration = datetime.timedelta(seconds=10)
# 측정 시작 및 종료 지점 설정 필요 #

Face_data_folder = "Data/Face/"
PPG_data_folder = "Data/PPG/"

cap = cv2.VideoCapture(0)

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


Packet = []
vendor_num = 0x0f1f
product_num = 0x0021


def read_handler(data):
    # print("Raw data: {0}".format(data))
    Packet.append(data[0:10])


def main():
    start_time = datetime.datetime.now()
    ubpulse = hid.HidDeviceFilter(vendor_id=vendor_num, product_id=product_num)
    devices = ubpulse.get_devices()

    if devices:
        device = devices[0]
        device.open()
        device.set_raw_data_handler(read_handler)

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

        df = pd.DataFrame(Packet)
        df.to_csv(PPG_data_folder + experiment_time + '.csv')

        device.close()

    cap.release()
    out.release()  # 비디오 라이터 해제
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
