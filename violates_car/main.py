from ultralytics import YOLO
import cv2
import sys
from collections import defaultdict
import numpy as np
import os
import requests
import serial
from datetime import datetime

serial_port = '/dev/ttyACM0'
baud_rate = 9600

now = datetime.now()
timestamp = now.timestamp()

url = 'http://13.125.213.163:5000/upload'

try:
    ser = serial.Serial(serial_port, baud_rate)
    print("Serial connection established")
except:
    print("Failed to connect to serial port")
    ser = None

model = YOLO('yolov8n.pt')
video_path = 'videos/video1.MOV'
cap = cv2.VideoCapture(video_path)

# 위반 객체 저장 디렉토리
if not os.path.exists('violations'):
    os.makedirs('violations')

# 신호등 초기 상태 설정
traffic_light = "Green Light"
frame_rate = cap.get(cv2.CAP_PROP_FPS)
time_threshold = 2 * frame_rate  # 2초
change_time = 25 * frame_rate  # 25초

ret, frame = cap.read()
if not ret:
    print("Failed to read video")
    cap.release()
    sys.exit(1)

height, width, _ = frame.shape

# 정지선
stop_line = height - 438

# 차로 영역 설정
area_above_stop_line = (700, 0, width - 1200, stop_line)  # 위쪽
area_below_stop_line = (490, stop_line, width - 1300, height - stop_line)  # 아래쪽

# 횡단보도 영역 설정
rect1 = (300, 775, 1200, 1200)
rect2 = (850, 500, 1700, 740)

# 이전 프레임의 객체 좌표를 저장
previous_centers = {}
# 객체가 위 영역에 머무는 시간
object_times = defaultdict(int)
# 위반 차량 저장
violated_objects = set()
# 캡쳐된 위반 차량 저장
captured_violations = set()
# 객체가 위 영역에 머무는 시간 기록
object_enter_times = {}

frame_count = 0
violation_detected = False

def is_within_area(x, y, area):
    x_min, y_min, x_max, y_max = area
    return x_min <= x <= x_max and y_min <= y <= y_max

skip_frames = 5  # 매 5프레임마다 한 번씩만 처리

def send_violation_to_server(image_path, csv_data, csv_filename):
    if os.path.isfile(image_path):
        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
            data = {'csv_data': ','.join(csv_data), 'csv_filename': csv_filename}
            response = requests.post(url, files=files, data=data)
            print(f"Uploading {image_path} with CSV data: {response.text}")
    else:
        print(f"Image file not found: {image_path}")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # 매 skip_frames 프레임마다 한 번씩만 처리
    if frame_count % skip_frames != 0:
        continue

    # 25초가 되었을 때 신호등을 red light로 변경
    if frame_count >= change_time:
        traffic_light = "Red Light"

    results = model(frame)  # 모델 결과 얻기
    current_centers = {}
    bounding_boxes = {}

    pedestrians_detected = False  # 보행자 감지 여부

    # 바운딩 박스 좌표
    for result in results:
        for r in result.boxes:
            box = r.xyxy[0]
            cls = int(r.cls[0])
            x1, y1, x2, y2 = map(int, box[:4])
            centerX, centerY = (x1 + x2) // 2, (y1 + y2) // 2
            object_id = (centerX, centerY)

            if cls == 0:  # person class
                # 횡단보도 영역 내 보행자 감지 여부 확인
                if is_within_area(centerX, centerY, rect1) or is_within_area(centerX, centerY, rect2):
                    pedestrians_detected = True
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # 보행자는 빨간색 사각형

            # 차량이 지정된 영역 내에 있는지 확인
            if is_within_area(centerX, centerY, (area_above_stop_line[0], area_above_stop_line[1], area_above_stop_line[0] + area_above_stop_line[2], area_above_stop_line[1] + area_above_stop_line[3])) or \
               is_within_area(centerX, centerY, (area_below_stop_line[0], area_below_stop_line[1], area_below_stop_line[0] + area_below_stop_line[2], area_below_stop_line[1] + area_below_stop_line[3])):
                current_centers[object_id] = (centerX, centerY)
                bounding_boxes[object_id] = (x1, y1, x2, y2)

                # 바운딩 박스 시각화
                color = (255, 0, 0) if centerY < stop_line else (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    # 위에서 아래로 이동한 객체 수를 추적
    for prev_obj_id, (prev_x, prev_y) in previous_centers.items():
        if prev_y < stop_line:  # 이전 프레임에서는 위 영역에 있었고
            closest_dist = float('inf')
            closest_id = None
            for cur_obj_id, (cur_x, cur_y) in current_centers.items():
                dist = np.linalg.norm(np.array([prev_x, prev_y]) - np.array([cur_x, cur_y]))
                if dist < closest_dist:
                    closest_dist = dist
                    closest_id = cur_obj_id

            if closest_id and current_centers[closest_id][1] >= stop_line:  # 현재 프레임에서는 아래 영역으로 이동
                if traffic_light == "Red Light" or pedestrians_detected:
                    if object_id in object_enter_times:
                        time_in_area = frame_count - object_enter_times[object_id]
                        if time_in_area < time_threshold:
                            violated_objects.add(closest_id)  # 위반 차량으로 추가
                    else:
                        violated_objects.add(closest_id)
                del current_centers[closest_id]  # 처리한 객체는 제거

    # 객체가 위 영역에 머무는 시간을 기록
    for obj_id, (x, y) in current_centers.items():
        if y < stop_line:
            if obj_id not in object_enter_times:
                object_enter_times[obj_id] = frame_count

    previous_centers = current_centers  # 현재 프레임의 객체를 이전 프레임으로 업데이트

    # 위반 차량 시각화 및 데이터 전송 (한 번만 캡쳐)
    for obj_id in violated_objects:
        if obj_id in bounding_boxes and obj_id not in captured_violations:
            x1, y1, x2, y2 = bounding_boxes[obj_id]
            cv2.putText(frame, "Violation", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            # 바운딩 박스 내부 이미지 저장
            violation_image = frame[y1:y2, x1:x2]
            violation_image_path = f'violations/{timestamp}.jpg'
            cv2.imwrite(violation_image_path, violation_image)
            captured_violations.add(obj_id)
            violation_detected = True  # 위반 객체를 인식했음을 표시

            # 현재 시간 업데이트
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            csv_data = [f'{timestamp}.jpg', current_time]
            csv_filename = now.strftime("%Y-%m-%d") + '.csv'

            # 데이터 전송
            send_violation_to_server(violation_image_path, csv_data, csv_filename)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, f"Traffic Light: {traffic_light}", (10, 30), font, 1, (0, 0, 0), 2, cv2.LINE_AA)

    # 신호 제어 추가
    if ser:
        if pedestrians_detected:
            ser.write(b'30')  # 보행자 감지 시 신호 제어
            print("Pedestrian detected: Turning off the right signal")
        else:
            ser.write(b'31')  # 보행자 감지 안 됨 시 신호 제어
            print("No pedestrian detected: Turning on the right signal")

    cv2.imshow('Frame', frame)

    # 프레임 속도를 영상의 FPS에 맞춤
    if cv2.waitKey(int(1000 / frame_rate)) & 0xFF == ord('q'):
        break

if ser:
    ser.close()
    print("Serial port closed")
cap.release()
cv2.destroyAllWindows()
