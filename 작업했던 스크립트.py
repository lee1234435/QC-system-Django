
'''
class Command(BaseCommand):
    help = 'Your custom script description here' # 코드 실행 전 스크립트 내용 작성하라고 확인용으로 만든 부분

    def handle(self, *args, **options):
        # CSV 파일 경로
        csv_file_path = 'Q_C_line_system_Data_System.csv' # 빈 csv 파일

        # CSV 파일을 열고 준비
        csv_file = open(csv_file_path, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['판단']) # CSV 파일에 헤더 추가 (field 7번하고 맞춰야함)

        cap = cv2.VideoCapture(0)
        cap.set(3, 640)
        cap.set(4, 480)

        model = YOLO('Quality.pt')
        classNames = ['O', 'X']

        while True:
            success, img = cap.read()
            results = model(img, stream=True)

            object_count = 0  # 물체 카운트 초기화

            for r in results:
                boxes = r.boxes

                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

                    cls = int(box.cls[0])

                    cls_name = classNames[min(cls, len(classNames)-1)]

                    org = [x1, y1]
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    fontScale = 1
                    thickness = 2

                    cv2.putText(img, cls_name, org, font, fontScale, (255, 0, 0), thickness)

                    if cls_name == 'O':
                        # 초록색 물체의 클래스를 CSV 파일에 저장
                        csv_writer.writerow([cls_name])

                        # 데이터베이스에 바로 추가
                        traffic_system.objects.create(
                            # field1='제조품 이름',
                            field2='제조품 사진',
                            # field3='제조품 생산 날짜',
                            # field4='제조 번호',
                            # field5='규격 및 사양',
                            # field6='생산라인',
                            field7=
                        )

                    object_count += 1  # 물체 카운트 증가

            # 탐지된 물체의 수를 화면에 표시
            cv2.putText(img, f"Objects: {object_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow('Webcam', img)
            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        # CSV 파일 닫기
        csv_file.close()




'''


'''
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

model = YOLO('Quality.pt')
classNames = ['O','X']

# CSV 파일을 열고 준비
csv_file = open('detected_objects.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Class'])  # CSV 파일에 헤더 추가

while True:
    success, img = cap.read()
    results = model(img, stream=True)

    object_count = 0  # 물체 카운트 초기화

    for r in results:
        boxes = r.boxes

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            confidence = math.ceil((box.conf[0]*100))/100
            cls = int(box.cls[0])

            cls_name = classNames[min(cls, len(classNames)-1)]

            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            thickness = 2

            cv2.putText(img, cls_name, org, font, fontScale, (255, 0, 0), thickness)

            if cls_name == 'O':
                # 초록색 물체의 클래스를 CSV 파일에 저장
                csv_writer.writerow([cls_name])

            object_count += 1  # 물체 카운트 증가

    # 탐지된 물체의 수를 화면에 표시
    cv2.putText(img, f"Objects: {object_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# CSV 파일 닫기
csv_file.close()


class Command(BaseCommand):
    def handle(self, *args, **options):
        # CSV 파일 경로
        csv_file = 'Q_C_line_system_Data_System.csv'

        # CSV 파일 열 헤더와 데이터를 딕셔너리 형태로 읽어옴
        with open(csv_file, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # 각 열의 데이터를 가져와서 변수에 할당
                manufacture_name = row['제조품 이름']
                manufacture_picture = row['제조품 사진']
                manufacture_calender = row['제조품 생산 날짜']
                manufacture_number = row['제조 번호']
                manufacture_size = row['규격 및 사양']
                manufacture_line = row['생산라인']
                manufacture_judge = row['판단']
                
                # 데이터베이스에 추가
                traffic_system.objects.create(
                    field1=manufacture_name,
                    field2=manufacture_picture,
                    field3=manufacture_calender,
                    field4=manufacture_number,
                    field5=manufacture_size,
                    field6=manufacture_line,
                    field7=manufacture_judge
                    # 필요한 필드들을 추가합니다.
                )
'''


# from django.core.management.base import BaseCommand
# from traffic_app.models import traffic_system
# from django.core.files.base import ContentFile
# from django.db import transaction
# from ultralytics import YOLO
# import cv2
# import time
# import os
# import csv

# class Command(BaseCommand):
#     help = 'Your custom script description here'

#     def handle(self, *args, **options):
#         # CSV 파일 경로
#         csv_file_path = 'Q_C_line_system_Data_System.csv'

#         # Ensure the images directory exists
#         images_dir = 'images'
#         if not os.path.exists(images_dir):
#             os.makedirs(images_dir)

#         # YOLO 모델 로드
#         model = YOLO('Quality_final.pt')
#         classNames = ['Pass', 'Grap']

#         # CSV 파일을 열고 준비
#         with open(csv_file_path, 'w', newline='') as csv_file:
#             csv_writer = csv.writer(csv_file)
#             csv_writer.writerow(['판단', 'image'])

#             # 카메라 캡처 시작
#             cap = cv2.VideoCapture(0)
#             cap.set(3, 640)
#             cap.set(4, 480)

#             last_capture_time = time.time()

#             while True:
#                 current_time = time.time()
#                 success, img = cap.read()

#                 if not success:
#                     self.stdout.write(self.style.ERROR('Failed to capture image from webcam.'))
#                     break
                
#                 # 타이머를 사용하여 10초마다 이미지 캡처
#                 if current_time - last_capture_time >= 10:
#                     last_capture_time = current_time

#                     # YOLO로 물체 탐지
#                     results = model(img, stream=True)

#                     for r in results:
#                         boxes = r.boxes

#                         for box in boxes:
#                             x1, y1, x2, y2 = box.xyxy[0]
#                             cls = int(box.cls[0])
#                             cls_name = classNames[min(cls, len(classNames)-1)]

#                             if cls_name == 'Pass':
#                                 object_img = img[int(y1):int(y2), int(x1):int(x2)]

#                                 # 이미지 저장 경로
#                                 image_filename = f'{int(time.time())}.jpg'
#                                 image_path = os.path.join(images_dir, image_filename)
                                
#                                 # 이미지 저장 시도 및 오류 처리
#                                 try:
#                                     if cv2.imwrite(image_path, object_img):
#                                         self.stdout.write(self.style.SUCCESS(f'Image saved successfully: {image_path}'))
#                                     else:
#                                         self.stdout.write(self.style.ERROR(f'Failed to save image: {image_path}'))
#                                         continue
#                                 except Exception as e:
#                                     self.stdout.write(self.style.ERROR(f'Error saving image: {e}'))
#                                     continue

#                                 # 데이터베이스에 바로 추가
#                                 try:
#                                     with open(image_path, 'rb') as f:
#                                         image_content = ContentFile(f.read(), name=image_filename)
#                                         with transaction.atomic():
#                                             traffic_system.objects.create(
#                                                 image=image_content,
#                                                 field7='판단'
#                                             )
#                                     csv_writer.writerow(['O', image_path])
#                                 except Exception as e:
#                                     self.stdout.write(self.style.ERROR(f"Error saving to database: {e}"))

#                 # 실시간 화면 표시
#                 cv2.imshow('Webcam', img)
#                 if cv2.waitKey(1) == ord('q'):
#                     break

#             cap.release()
#             cv2.destroyAllWindows()

'''
from django.core.management.base import BaseCommand
from traffic_app.models import traffic_system
from django.core.files.base import ContentFile
from django.db import transaction
from ultralytics import YOLO
import cv2
import time
import os
import csv

class Command(BaseCommand):
    help = 'Your custom script description here'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Starting the script...'))

            # CSV 파일 경로
            csv_file_path = 'Q_C_line_system_Data_System.csv'

            # Ensure the images directory exists
            images_dir = 'images'
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                self.stdout.write(self.style.SUCCESS(f'Created directory: {images_dir}'))

            # YOLO 모델 로드
            model = YOLO('Quality_final.pt')
            classNames = ['Grap', 'Pass']
            self.stdout.write(self.style.SUCCESS('YOLO model loaded successfully.'))

            # CSV 파일을 열고 준비
            with open(csv_file_path, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['판단', 'image'])
                self.stdout.write(self.style.SUCCESS(f'CSV file opened: {csv_file_path}'))

                # 카메라 캡처 시작
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    self.stdout.write(self.style.ERROR('Failed to open webcam.'))
                    return
                
                cap.set(3, 640)
                cap.set(4, 480)
                self.stdout.write(self.style.SUCCESS('Webcam opened successfully.'))

                last_capture_time = time.time()

                while True:
                    current_time = time.time()
                    success, img = cap.read()

                    if not success:
                        self.stdout.write(self.style.ERROR('Failed to capture image from webcam.'))
                        break

                    # 타이머를 사용하여 10초마다 이미지 캡처
                    if current_time - last_capture_time >= 10:
                        last_capture_time = current_time
                        self.stdout.write(self.style.SUCCESS('Capturing image...'))

                        # YOLO로 물체 탐지
                        results = model(img, stream=True)

                        for r in results:
                            boxes = r.boxes

                            for box in boxes:
                                x1, y1, x2, y2 = box.xyxy[0]
                                cls = int(box.cls[0])
                                cls_name = classNames[min(cls, len(classNames)-1)]
                                self.stdout.write(self.style.SUCCESS('Before searching for cls_name: Pass'))

                                if cls_name == 'Pass':
                                    object_img = img[int(y1):int(y2), int(x1):int(x2)]

                                    # 이미지 저장 경로
                                    image_filename = f'{int(time.time())}.jpg'
                                    image_path = os.path.join(images_dir, image_filename)
                                    self.stdout.write(self.style.SUCCESS('image saving......!'))
                                    
                                    # 이미지 저장 시도 및 오류 처리
                                    try:
                                        if cv2.imwrite(image_path, object_img):
                                            self.stdout.write(self.style.SUCCESS(f'Image saved successfully: {image_path}'))
                                        else:
                                            self.stdout.write(self.style.ERROR(f'Failed to save image: {image_path}'))
                                            continue
                                    except Exception as e:
                                        self.stdout.write(self.style.ERROR(f'Error saving image: {e}'))
                                        continue

                                    # 데이터베이스에 바로 추가
                                    try:
                                        with open(image_path, 'rb') as f:
                                            image_content = ContentFile(f.read(), name=image_filename)
                                            with transaction.atomic():
                                                traffic_system.objects.create(
                                                    image=image_content,
                                                    field7=cls_name
                                                )
                                                self.stdout.write(self.style.SUCCESS('Updated Database successfully.'))
                                        # csv_writer.writerow([cls_name, image_path])
                                    except Exception as e:
                                        self.stdout.write(self.style.ERROR(f"Error saving to database: {e}"))

                    # 실시간 화면 표시
                    cv2.imshow('Webcam', img)
                    if cv2.waitKey(1) == ord('q'):
                        break

                cap.release()
                cv2.destroyAllWindows()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in handle method: {e}'))



'''


'''
class Command(BaseCommand):
    help = 'Capture images using webcam, save to CSV, and update database'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_file_path = 'Q_C_line_system_Data_System_original_copy.csv'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Starting the script...'))

            # CSV 파일 경로
            csv_file_path = self.csv_file_path

            # Ensure the images directory exists
            images_dir = 'images'
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                self.stdout.write(self.style.SUCCESS(f'Created directory: {images_dir}'))

            # YOLO 모델 로드
            model = YOLO('Quality_final.pt')
            classNames = ['Grap', 'Pass']
            self.stdout.write(self.style.SUCCESS('YOLO model loaded successfully.'))

            # 카메라 캡처 시작
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.stdout.write(self.style.ERROR('Failed to open webcam.'))
                return

            cap.set(3, 640)
            cap.set(4, 480)
            self.stdout.write(self.style.SUCCESS('Webcam opened successfully.'))

            last_capture_time = time.time()

            while True:
                current_time = time.time()
                success, img = cap.read()

                if not success:
                    self.stdout.write(self.style.ERROR('Failed to capture image from webcam.'))
                    break

                # 타이머를 사용하여 10초마다 이미지 캡처
                if current_time - last_capture_time >= 10:
                    last_capture_time = current_time
                    self.stdout.write(self.style.SUCCESS('Capturing image...'))

                    # YOLO로 물체 탐지
                    results = model(img, stream=True)

                    for r in results:
                        boxes = r.boxes

                        for box in boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cls = int(box.cls[0])
                            cls_name = classNames[min(cls, len(classNames)-1)]
                            self.stdout.write(self.style.SUCCESS('Before searching for cls_name: Pass'))

                            if cls_name == 'Pass':
                                object_img = img[y1:y2, x1:x2]

                                # 이미지 저장 경로
                                image_filename = f'{int(time.time())}.jpg'
                                image_path = os.path.join(images_dir, image_filename)
                                self.stdout.write(self.style.SUCCESS('image saving......!'))

                                # 이미지 저장 및 CSV 파일에 데이터 추가
                                try:
                                    if cv2.imwrite(image_path, object_img):
                                        self.stdout.write(self.style.SUCCESS(f'Image saved successfully: {image_path}'))

                                        # CSV 파일에 데이터 추가
                                        with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
                                            csv_writer = csv.writer(csv_file)
                                            csv_writer.writerow([cls_name, image_path])
                                            self.stdout.write(self.style.SUCCESS(f'CSV file updated with cls_name: {cls_name}, image: {image_path}'))

                                        # 데이터베이스 업데이트
                                        self.update_database(cls_name, image_path)

                                    else:
                                        self.stdout.write(self.style.ERROR(f'Failed to save image: {image_path}'))
                                        continue
                                except Exception as e:
                                    self.stdout.write(self.style.ERROR(f'Error saving image: {e}'))
                                    continue

                # 실시간 화면 표시
                cv2.imshow('Webcam', img)
                if cv2.waitKey(1) == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in handle method: {e}'))

    def update_database(self, cls_name, image_path):
        try:
            with open(image_path, 'rb') as f:
                image_content = ContentFile(f.read(), name=os.path.basename(image_path))
                with transaction.atomic():
                    with open(self.csv_file_path, 'r', encoding='utf-8') as csv_file:
                        csv_reader = csv.reader(csv_file)
                        next(csv_reader)  # Skip the header row
                        traffic_system.objects.create(
                            name=name,
                            date=datetime.now().date(),  # 현재 날짜로 설정
                            serial_number=serial_number,
                            size=size,
                            line=line,
                            judgement=cls_name,
                            image=image_content
                        )
                    self.stdout.write(self.style.SUCCESS('Updated Database successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error saving to database: {e}"))
'''


'''
from django.core.management.base import BaseCommand
from traffic_app.models import traffic_system
from django.core.files.base import ContentFile
from django.db import transaction
from ultralytics import YOLO
from datetime import datetime
from pymycobot.mycobot import MyCobot

import cv2
import time
import os
import csv
import numpy as np

class Command(BaseCommand):
    help = 'Capture images using webcam, save to CSV, and update database'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_file_path = 'Q_C_line_system_Data_System_original_copy.csv'

        # Initialize MyCobot
        self.mc = MyCobot('COM3', 115200)
        self.mc.set_gripper_mode(0)
        self.mc.init_eletric_gripper()
        self.init_robot()

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Starting the script...'))

            # Ensure the images directory exists
            images_dir = 'images'
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                self.stdout.write(self.style.SUCCESS(f'Created directory: {images_dir}'))

            # Load YOLO model
            model = YOLO('Quality_control.pt')
            classNames = ['Grap', 'Pass', 'Product']
            self.stdout.write(self.style.SUCCESS('YOLO model loaded successfully.'))

            # Start capturing from webcam
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.stdout.write(self.style.ERROR('Failed to open webcam.'))
                return

            cap.set(3, 640)
            cap.set(4, 480)
            self.stdout.write(self.style.SUCCESS('Webcam opened successfully.'))

            last_capture_time = time.time()

            while True:
                current_time = time.time()
                success, img = cap.read()

                if not success:
                    self.stdout.write(self.style.ERROR('Failed to capture image from webcam.'))
                    break

                if current_time - last_capture_time >= 10:
                    last_capture_time = current_time
                    self.stdout.write(self.style.SUCCESS('Capturing image...'))

                    results = model(img, stream=True)
                    detected_classes = set()
                    boxes_dict = {}

                    for r in results:
                        boxes = r.boxes

                        for box in boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cls = int(box.cls[0])
                            cls_name = classNames[min(cls, len(classNames) - 1)]
                            detected_classes.add(cls_name)
                            boxes_dict[cls_name] = (x1, y1, x2, y2)

                            if 'Product' in detected_classes:
                                if 'Pass' in detected_classes:
                                    x1, y1, x2, y2 = boxes_dict['Product']
                                    object_img = img[y1:y2, x1:x2]
                                    judgement_cls = 'Pass'
                                elif 'Grap' in detected_classes:
                                    x1, y1, x2, y2 = boxes_dict['Product']
                                    object_img = img[y1:y2, x1:x2]
                                    judgement_cls = 'Grap'
                                    self.run_robot()
                                else:
                                    continue

                        image_filename = f'{int(time.time())}_{judgement_cls}.jpg'
                        image_path = os.path.join(images_dir, image_filename)
                        self.stdout.write(self.style.SUCCESS('Image saving...'))

                        try:
                            if cv2.imwrite(image_path, object_img):
                                self.stdout.write(self.style.SUCCESS(f'Image saved successfully: {image_path}'))
                                self.update_database(judgement_cls, image_path)
                            else:
                                self.stdout.write(self.style.ERROR(f'Failed to save image: {image_path}'))
                                continue
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Error saving image: {e}'))
                            continue

                cv2.imshow('Webcam', img)
                if cv2.waitKey(1) == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in handle method: {e}'))

    def update_database(self, cls_name, image_path):
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)
                for row in csv_reader:
                    _, name, serial_number, size, line, _, _ = row[:7]
                    with open(image_path, 'rb') as f:
                        image_content = ContentFile(f.read(), name=os.path.basename(image_path))
                        traffic_system.objects.create(
                            name=name,
                            date=datetime.now().date(),
                            serial_number=serial_number,
                            size=size,
                            line=line,
                            judgement=cls_name,
                            image=image_content
                        )
            self.stdout.write(self.style.SUCCESS('Updated Database successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error saving to database: {e}"))
            self.stdout.write(self.style.ERROR(f"Unexpected row format: {row}"))

    def init_robot(self):
        self.mc.send_angles([0, 0, 0, 0, 0, 0], 40)
        time.sleep(4)

    def gripper_open(self):
        print("OPEN")
        self.mc.set_eletric_gripper(0)
        self.mc.set_gripper_value(100, 30)
        time.sleep(2)

    def gripper_close(self):
        print("CLOSE")
        self.mc.set_eletric_gripper(1)
        self.mc.set_gripper_value(45, 30)
        time.sleep(2)

    def wait(self):
        self.mc.send_angles([0, -23, -40, -17, 90, 90], 40)
        time.sleep(3)

    def up_release(self):
        self.mc.send_angles([0, 0, 0, 0, 90, 90], 40)
        time.sleep(3)
        self.mc.send_angles([100, 0, 0, 0, 90, 90], 40)
        time.sleep(3)
        self.mc.send_angles([100, -40, -35, -0, 90, 90], 40)
        time.sleep(3)

    def stand(self):
        self.mc.send_angles([100, 0, 0, 0, 90, 90], 40)
        time.sleep(3)
        self.mc.send_angles([0, 0, 0, 0, 90, 90], 40)
        time.sleep(3)

    def run_robot(self):
        self.wait()
        self.gripper_open()
        self.gripper_close()
        self.up_release()
        self.gripper_open()
        self.stand()
        self.wait()

'''