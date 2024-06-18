import serial
import time

# serial 라이브러리 설치 필요
# cmd ->
# pip install pyserial
# 시리얼 포트, 속도 설정
serial_port = '/dev/ttyUSB0'  # 시리얼 포트 설정
baud_rate = 9600 # 시리얼 통신 속도에 맞게 설정

ser = None  # 시리얼 통신 객체 초기화
i = True

try:
    # 시리얼 통신 열기
    ser = serial.Serial(serial_port, baud_rate)
    print("Serial connection established")

    while True:
        if i:
            ser.write(b'31')
        else:
            ser.write(b'30')

        time.sleep(5)
        i = not i  # i를 뒤집음

except KeyboardInterrupt:
    print("Keyboard Interrupt. Exiting...")

finally:
    # 시리얼 통신 객체가 정의되어 있으면 닫기
    if ser:
        ser.close()
