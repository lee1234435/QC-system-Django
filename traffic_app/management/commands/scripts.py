# ---------------- modules, libraries, files ---------------- #
from django.core.management.base import BaseCommand
from traffic_app.models import traffic_system
from django.core.files.base import ContentFile
from django.db import transaction
from ultralytics import YOLO
from datetime import datetime

import cv2
import time
import os
import csv

# ---------------- scripts2.py run -> write a table(database) ---------------- #
# python manage.py scripts.py -> command
class Command(BaseCommand):
    help = 'Capture images using webcam, save to CSV, and update database'

    #constructor
    def __init__(self, *args, **kwargs):
        # init
        super().__init__(*args, **kwargs)
        self.csv_file_path = 'Q_C_line_system_Data_System_original_copy.csv'

    #method
    def handle(self, *args, **options):
        try:
            #logging.info
            self.stdout.write(self.style.SUCCESS('Starting the script...'))

            # CSV file path
            csv_file_path = self.csv_file_path

            # Ensure the images directory exists
            images_dir = 'images'
            if not os.path.exists(images_dir):
                # make a directory
                os.makedirs(images_dir)
                self.stdout.write(self.style.SUCCESS(f'Created directory: {images_dir}'))

            # YOLO model load
            model = YOLO('Quality_control.pt')
            classNames = ['Grap', 'Pass', 'Product']
            self.stdout.write(self.style.SUCCESS('YOLO model loaded successfully.'))

            # camera capture start
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.stdout.write(self.style.ERROR('Failed to open webcam.'))
                return
            
            # camera size set
            cap.set(3, 640)
            cap.set(4, 480)
            self.stdout.write(self.style.SUCCESS('Webcam opened successfully.'))

            # timer
            last_capture_time = time.time()

            # main script ---- part1
            while True:
                current_time = time.time()
                success, img = cap.read()

                if not success:
                    self.stdout.write(self.style.ERROR('Failed to capture image from webcam.'))
                    break

                # image capture (using a timer for 10s)
                if current_time - last_capture_time >= 10:
                    last_capture_time = current_time
                    self.stdout.write(self.style.SUCCESS('Capturing image...'))

                    # YOLO => object detecting
                    results = model(img, stream=True)

                    # 
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
                                else:
                                    continue  # Pass나 Grap이 감지되지 않은 경우 계속


                        # image save path
                        image_filename = f'{int(time.time())}_{judgement_cls}.jpg'
                        image_path = os.path.join(images_dir, image_filename)
                        self.stdout.write(self.style.SUCCESS('Image saving...'))

                        
                        try:
                            # image save
                            if cv2.imwrite(image_path, object_img):
                                self.stdout.write(self.style.SUCCESS(f'Image saved successfully: {image_path}'))

                                # datebase update
                                self.update_database(judgement_cls, image_path)

                            else:
                                # error message
                                self.stdout.write(self.style.ERROR(f'Failed to save image: {image_path}'))
                                continue
                        # error message
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Error saving image: {e}'))
                            continue

                # monitoring
                cv2.imshow('Webcam', img)
                if cv2.waitKey(1) == ord('q'):
                    break

            # closing
            cap.release()
            cv2.destroyAllWindows()

        # error
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in handle method: {e}'))

    # method
    def update_database(self, cls_name, image_path):
        # main script ---- part2
        try:
            # open a csv file & encode it
            with open(self.csv_file_path, 'r', encoding='utf-8') as csv_file:
                #
                csv_reader = csv.reader(csv_file)
                #
                next(csv_reader)
                # read a csv file header
                for row in csv_reader:
                    # csv => id, name, serial_number, size, manufacture_line, judgement, image path
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
        # error message
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error saving to database: {e}"))
            self.stdout.write(self.style.ERROR(f"Unexpected row format: {row}"))
