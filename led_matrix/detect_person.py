from ultralytics import YOLO
import serial
import time

serial_port = '/dev/ttyACM0'
baud_rate = 9600
ser = None

model = YOLO('yolov8n.pt')

try:
    ser = serial.Serial(serial_port, baud_rate)
    print("Serial connection established")
    camera = model('tcp://192.168.59.253:8888', stream=True, classes=[0])
    print("Streaming started...")
    right = True

    for frame in camera:
        results = frame.boxes
        
        if len(results) > 0:
            ser.write(b'30')
            print("Turn off the right signal")
        else:
            ser.write(b'31')
            print("Turn on the right signal")


except KeyboardInterrupt:
    print("Keyboard Interrupt. Exiting...")

finally:
    if ser:
        ser.close()
        print("Serial port closed")