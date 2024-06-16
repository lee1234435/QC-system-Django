from django.db import models
from datetime import date

# Create your models here.
class traffic_system(models.Model):
    # 모델 필드 정의
    name = models.CharField(max_length=100)
    date = models.DateField(default=date.today)  # max_length 제거, 기본값으로 현재 날짜 설정
    serial_number = models.CharField(max_length=100)
    size = models.CharField(max_length=100)
    line = models.CharField(max_length=100)
    judgement = models.CharField(max_length=100, default='')
    image = models.ImageField(upload_to='images/')

class Test1(models.Model):
    # 모델 필드 정의
    test_field1 = models.CharField(max_length=100, default='')
    test_field3 = models.IntegerField(default=0)  # max_length 제거, 기본값을 숫자로 설정

    class Meta:
        managed = False
        app_label = "test1"
        db_table = 'dbtest1'
