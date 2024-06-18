import serial
import time

# serial 라이브러리 설치 필요
# cmd -> pip install pyserial
# 시리얼 포트, 속도 설정
serial_port = 'COM6'  # 아두이노 IDE에서 확인
baud_rate = 9600  # 시리얼 통신 속도에 맞게 설정

ser = None  # 시리얼 통신 객체 초기화
i = True

try:
    # 시리얼 통신 열기
    ser = serial.Serial(serial_port, baud_rate)
    print("Serial connection established")

    while True:
        i = input('t 또는 f 입력하세요: ')

        if i == 't':
            ser.write(b'74')
        elif i == 'f':
            ser.write(b'66')

except KeyboardInterrupt:
    print("Keyboard Interrupt. Exiting...")

finally:
    # 시리얼 통신 객체가 정의되어 있으면 닫기
    if ser:
        ser.close()
