from django.core.management.base import BaseCommand
from traffic_app.models import traffic_system
import csv
from datetime import datetime

class Command(BaseCommand):
    help = 'Import data from CSV file into the traffic_system model'

    def handle(self, *args, **options):
        # CSV 파일 경로
        csv_file_path = 'Q_C_line_system_Data_System_original_copy.csv'

        # CSV 파일 열 헤더와 데이터를 딕셔너리 형태로 읽어옴
        with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # 각 열의 데이터를 가져와서 변수에 할당
                    manufacture_name = row['name']
                    manufacture_calender = row['date']
                    manufacture_number = row['serial_number']
                    manufacture_size = row['size']
                    manufacture_line = row['line']
                    manufacture_judge = row['judgement']
                    manufacture_picture = row['image']
                    
                    # 날짜 형식 변환 및 검증
                    try:
                        manufacture_calender = datetime.strptime(manufacture_calender, '%Y-%m-%d').date()
                    except ValueError:
                        self.stdout.write(self.style.ERROR(f"Invalid date format for entry: {manufacture_calender}"))
                        continue

                    # 데이터베이스에 추가
                    traffic_system.objects.create(
                        name=manufacture_name,
                        date=manufacture_calender,
                        serial_number=manufacture_number,
                        size=manufacture_size,
                        line=manufacture_line,
                        judgement=manufacture_judge,
                        image=manufacture_picture,
                    )
                except KeyError as e:
                    self.stdout.write(self.style.ERROR(f"KeyError: {e} - Check the CSV header names"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error: {e}"))
