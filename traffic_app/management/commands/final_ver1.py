# -------------------------- library, module, file -------------------------- # 
from django.core.management.base import BaseCommand
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from ultralytics import YOLO
from pymycobot.mycobot import MyCobot
from multiprocessing import Process, Queue
from traffic_app.models import traffic_system
from django.core.files.base import ContentFile
from django.utils import timezone

import numpy as np
import os
import threading
import cv2
import time
import datetime
import random
import pyqtgraph as pg
import csv
import sys
import django


# 최종본
# -------------------------- main scripts -------------------------- # 



class CameraThread(QThread):
    update_frame = pyqtSignal(QImage)
    update_product_info = pyqtSignal(str, str)
    update_bar_graph = pyqtSignal(int, int, int)

    def __init__(self, queue, parent=None):
        super(CameraThread, self).__init__(parent)
        self.queue = queue
        self.running = True

    def run(self):
        total_cnt = 0
        normal_cnt = 0
        defect_cnt = 0
        
        while self.running:
            if not self.queue.empty():
                frame, annotated_frame, product_info, db_update = self.queue.get()
                color_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = color_frame.shape
                bytes_per_line = ch * w
                converted_frame = QImage(color_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.update_frame.emit(converted_frame)

                if product_info:
                    serial_number, qc_status = product_info
                    self.update_product_info.emit(serial_number, qc_status)
                    total_cnt += 1
                    if qc_status == "Passed":
                        normal_cnt += 1
                    else:
                        defect_cnt += 1
                    self.update_bar_graph.emit(total_cnt, normal_cnt, defect_cnt)  # 시그널 방출


                if db_update:
                    self.update_database(db_update)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
        
class Main(QDialog):
    def __init__(self):
        super().__init__()
        self.queue = Queue()
        self.init_ui()

    def init_ui(self):
        global nomal_cnt, detc_cnt, total_cnt
        
        self.setObjectName("Fctory Info")
        main_layout = QVBoxLayout()
        
        self.setLayout(main_layout)
        self.resize(1920, 1000)
        self.show()

        # Frame and Layout Initialization
        frame_1 = QFrame()
        frame_1.setFrameShape(QFrame.Panel | QFrame.Sunken)
        frame_2 = QFrame()
        frame_2.setFrameShape(QFrame.Panel | QFrame.Sunken)
        frame_3 = QFrame()
        frame_3.setFrameShape(QFrame.Panel | QFrame.Sunken)
        frame_4 = QFrame()
        frame_4.setFrameShape(QFrame.Panel | QFrame.Sunken)

        layout_1 = QVBoxLayout()
        layout_2 = QVBoxLayout()
        layout_3 = QVBoxLayout()
        layout_4 = QVBoxLayout()
        
        # Frame 1: Production line number, date, and time
        self.line_label = QLabel("Production Line: #1")
        self.date_label = QLabel("Date: " + datetime.datetime.now().strftime("%Y-%m-%d"))
        self.time_label = QLabel("Time: " + datetime.datetime.now().strftime("%H:%M:%S"))
        
        self.line_label.setFont(QtGui.QFont("고딕",20)) #폰트,크기 조절
        self.line_label.setStyleSheet("Color : black") #글자색 변환
        
        self.date_label.setFont(QtGui.QFont("고딕",20)) #폰트,크기 조절
        self.date_label.setStyleSheet("Color : black") #글자색 변환
        
        self.time_label.setFont(QtGui.QFont("고딕",20)) #폰트,크기 조절
        self.time_label.setStyleSheet("Color : black") #글자색 변환
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # update every second
        layout_1.addWidget(self.line_label)
        layout_1.addWidget(self.date_label)
        layout_1.addWidget(self.time_label)
        
        # Frame 2: Serial number, model name, and QC status
        self.serial_label = QLabel("Serial Number: ")
        self.model_label = QLabel("Model Name: joint")
        self.qc_label = QLabel("QC Status: ")
        
        self.serial_label.setFont(QtGui.QFont("고딕",20)) #폰트,크기 조절
        self.serial_label.setStyleSheet("Color : black") #글자색 변환
        
        self.model_label.setFont(QtGui.QFont("고딕",20)) #폰트,크기 조절
        self.model_label.setStyleSheet("Color : black") #글자색 변환
        
        self.qc_label.setFont(QtGui.QFont("고딕",20)) #폰트,크기 조절
        self.qc_label.setStyleSheet("Color : black") #글자색 변환

        layout_2.addWidget(self.serial_label)
        layout_2.addWidget(self.model_label)
        layout_2.addWidget(self.qc_label)
        
        # Frame 3: USB camera feed
        self.camera_view = QLabel()
        layout_3.addWidget(self.camera_view)

        # Frame 4: Production statistics and graph
        self.stats_label = QLabel("Total Production: 0\nNormal: 0\nDefective: 0")
        self.stats_label.setFont(QtGui.QFont("고딕",15)) #폰트,크기 조절
        self.stats_label.setStyleSheet("Color : black") #글자색 변환
        
        self.plot_widget = pg.PlotWidget()
        self.update_bar_graph(0, 0, 0)
        layout_4.addWidget(self.stats_label)
        layout_4.addWidget(self.plot_widget)
        
        # Set layouts to frames
        frame_1.setLayout(layout_1)
        frame_2.setLayout(layout_2)
        frame_3.setLayout(layout_3)
        frame_4.setLayout(layout_4)

        # Splitters
        spliter_1 = QSplitter(Qt.Orientation.Vertical)
        spliter_1.addWidget(frame_1)
        spliter_1.addWidget(frame_2)
        
        spliter_2 = QSplitter(Qt.Orientation.Horizontal)
        spliter_2.addWidget(spliter_1)
        spliter_2.addWidget(frame_3)
        
        spliter_3 = QSplitter(Qt.Orientation.Vertical)
        spliter_3.addWidget(spliter_2)
        spliter_3.addWidget(frame_4)

        main_layout.addWidget(spliter_3)

        self.setLayout(main_layout)
        self.resize(1920, 1000)
        self.show()

        # Camera Thread
        self.thread = CameraThread(self.queue)  # queue 매개변수를 제공
        self.thread.update_frame.connect(self.set_image)
        self.thread.update_product_info.connect(self.update_product_info)
        self.thread.update_bar_graph.connect(self.update_bar_graph)  # 시그널 연결
        self.thread.start()
        
    def set_image(self, image):
        self.camera_view.setPixmap(QPixmap.fromImage(image))
        
    def update_time(self):
        self.time_label.setText("Time: " + datetime.datetime.now().strftime("%H:%M:%S"))
    
    def update_product_info(self, serial_number, qc_status, txt_color):
        self.serial_label.setText(f"Serial Number: {serial_number}")
        self.qc_label.setText(f"QC Status: {qc_status}")
        self.qc_label.setStyleSheet(txt_color) #글자색 변환

    def update_bar_graph(self, total, normal, defective):
        self.stats_label.setText(f"Total Production: {total}\nNormal: {normal}\nDefective: {defective}")
        bg1 = pg.BarGraphItem(x=[1, 2], height=[normal, defective], width=0.6, brushes=['g','r'])
        self.plot_widget.clear()
        self.plot_widget.addItem(bg1)
        self.plot_widget.getAxis('bottom').setTicks([[(1, 'Normal'), (2, 'Defective')]])

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

def camera_process(queue):
    cap = cv2.VideoCapture(0)
    model = YOLO('Quality_control.pt')

    while True:
        ret, frame = cap.read()
        if ret:
            results = model(frame, conf=0.85)
            annotated_frame = results[0].plot()
            product_info = None
            db_update = None

            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = box.conf[0]
                    cls = box.cls[0]
                    if confidence > 0.85:
                        serial_number = "SN" + str(random.randint(1000000000, 9999999999))
                        qc_status = "Passed" if random.random() > 0.1 else "Failed"
                        product_info = (serial_number, qc_status)
                        db_update = {"serial_number": serial_number, "qc_status": qc_status}

            queue.put((frame, annotated_frame, product_info, db_update))
        time.sleep(0.1)

class Command(BaseCommand):
    help = 'Capture images using webcam, save to CSV, and update database'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_file_path = 'Q_C_line_system_Data_System_original_copy.csv'
        self.serial_number_counter = 0
        # Initialize MyCobot
        self.mc = MyCobot('COM3', 115200)
        self.mc.set_gripper_mode(0)
        self.mc.init_eletric_gripper()
        self.init_robot()
        
    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Starting the script...'))
            
            django.setup() 

            pyqt_thread = threading.Thread(target=self.start_pyqt)
            pyqt_thread.start()
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
            counter = 0
            
            while True:
                current_time = time.time()
                success, img = cap.read()

                if not success:
                    self.stdout.write(self.style.ERROR('Failed to capture image from webcam.'))
                    break

                if current_time - last_capture_time >= 10:
                    last_capture_time = current_time
                    self.stdout.write(self.style.SUCCESS('Capturing image...'))

                    results = model(img, stream=True, conf = 0.92)
                    detected_classes = []
                    boxes_dict = {}

                    for r in results:
                        boxes = r.boxes

                        for box in boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cls = int(box.cls[0])
                            cls_name = classNames[min(cls, len(classNames) - 1)]
                            detected_classes.append(cls_name)
                            boxes_dict[cls_name] = (x1, y1, x2, y2)
                            image_path = ''
                            
                            if 'Product' not in detected_classes:
                                self.stdout.write(self.style.ERROR('No Product detected, skipping this capture.'))
                                break
                            
                            if 'Product' in detected_classes:
                                # image_filename = f'{int(time.time())}_{judgement_cls}.jpg'
                                # image_path = os.path.join(images_dir, image_filename)
                                # self.stdout.write(self.style.SUCCESS('Image saving...'))
                                today_date = datetime.datetime.now().strftime("%Y%m%d")
                                
                                
                                if 'Pass' in detected_classes:
                                    x1, y1, x2, y2 = boxes_dict['Product']
                                    object_img = img[y1:y2, x1:x2]
                                    judgement_cls = 'Pass'
                                    
                                    counter += 1
                                    # image_filename = f'{int(time.time())}_{judgement_cls}.jpg'
                                    image_filename = f'SN{today_date}{counter:03d}.jpg'
                                    image_path = os.path.join(images_dir, image_filename)
                                    self.stdout.write(self.style.SUCCESS('Image saving...'))
                                    cv2.imwrite(image_path, object_img)
                                    
                                    self.stdout.write(self.style.SUCCESS(f'Image saved pass successfully: {image_path}'))
                                    self.update_database(judgement_cls, image_path)
                                    
                                elif 'Grap' in detected_classes:
                                    x1, y1, x2, y2 = boxes_dict['Product']
                                    object_img = img[y1:y2, x1:x2]
                                    judgement_cls = 'Grap'
                                    
                                    counter += 1
                                    image_filename = f'SN{today_date}{counter:03d}.jpg' 
                                    # image_filename = f'{int(time.time())}_{judgement_cls}.jpg'
                                    image_path = os.path.join(images_dir, image_filename)
                                    self.stdout.write(self.style.SUCCESS('Image saving...'))
                                    cv2.imwrite(image_path, object_img)
                                    
                                    
                                    self.stdout.write(self.style.SUCCESS(f'Image saved grap successfully: {image_path}'))
                                    self.update_database(judgement_cls, image_path)
                                    
                                    self.run_robot()
                                    self.stdout.write(self.style.SUCCESS(f'Robot Operating......'))
                                    break
                                    
                                else:
                                    continue
                                
                            
                        detected_classes = []

                        # try:
                        #     if cv2.imwrite(image_path, object_img):
                        #         self.stdout.write(self.style.SUCCESS(f'Image saved successfully: {image_path}'))
                        #         self.update_database(judgement_cls, image_path)
                        #     else:
                        #         self.stdout.write(self.style.ERROR(f'Failed to save image: {image_path}'))
                        #         continue
                        # except Exception as e:
                        #     self.stdout.write(self.style.ERROR(f'Error saving image: {e}'))
                        #     continue

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
                    serial_number = f'SN{timezone.now().strftime("%Y%m%d")}{self.serial_number_counter:03d}'
                    self.serial_number_counter += 1
                    with open(image_path, 'rb') as f:
                        image_content = ContentFile(f.read(), name=os.path.basename(image_path))
                        traffic_system.objects.create(
                            name=name,
                            date=timezone.now().date(),  
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
        self.mc.send_angles([0, 0, 0, 0, 90, 0], 40)
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
    
    def start_pyqt(self):
        app = QApplication(sys.argv)
        main = Main()
        sys.exit(app.exec_())
        
        

    if __name__ == '__main__':
        django.setup()  # Ensure Django setup is called here
        app = QApplication(sys.argv)
        main = Main()
        sys.exit(app.exec_())