import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
ser = serial.Serial()
ser.port = 'COM3'
ser.baudrate = 9600
for i in ports: #COM Port 찾기 하나씩 해보면서 ser.port = 'COM숫자'로 바꿔야함
    print(i.name)
    print(i.description)

ser.open()
while True:

    data = ser.readline()
    print(data)


ser.close()  # serial 사용이 끝나면 닫아줘야 나중에 오류가 생기지 않는다고 한다.