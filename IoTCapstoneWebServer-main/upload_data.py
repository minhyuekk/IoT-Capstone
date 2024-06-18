import requests
import os

#'서버 주소/upload 입력'
url = '[서버 주소]/upload'

# CSV 데이터 전송
# '이미지'를 전송할 이미지 이름으로 변경
# 위반 시간과 csv 파일 이름은 다음 양식을 반드시 지켜야 함. ex) '2024-05-30 10:00:00', '2024-05-30.csv'
csv_data = ['이미지.JPG', '년-월-일 시:분:초']
csv_filename = '년-월-일.csv'

# 이미지 파일 경로
image_file_path = '이미지.JPG'

if os.path.isfile(image_file_path):
    with open(image_file_path, 'rb') as image_file:
        # Create a dictionary with the files and form data
        files = {
            'image': image_file
        }
        data = {
            'csv_data': ','.join(csv_data),
            'csv_filename': csv_filename
        }
        response = requests.post(url, files=files, data=data)
        print(f"Uploading {image_file_path} with CSV data: {response.text}")
else:
    print(f"Image file not found: {image_file_path}")
