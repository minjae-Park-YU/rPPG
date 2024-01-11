import pywinusb.hid as hid
import pandas as pd
import time

# # HID Device 찾기 (vID, pID) #
# all_devices = hid.find_all_hid_devices()
# for device in all_devices:
#     print(device)

Packet = []
vendor_num = 0x0f1f
product_num = 0x0021


def read_handler(data):
    print("Raw data: {0}".format(data))
    Packet.append(data[0:10])
    df = pd.DataFrame(Packet)
    df.to_csv('test.csv')


def main():

    ubpulse = hid.HidDeviceFilter(vendor_id=vendor_num, product_id=product_num)
    devices = ubpulse.get_devices()

    if devices:
        device = devices[0]
        device.open()
        device.set_raw_data_handler(read_handler)

        try:
            while True:
                time.sleep(0.5)  # 메인 스레드가 종료되지 않도록 지연
        except KeyboardInterrupt:
            pass  # Ctrl+C를 눌러 프로그램을 종료할 수 있도록 함

        device.close()


if __name__ == "__main__":
    main()
