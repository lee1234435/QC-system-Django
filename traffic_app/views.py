# traffic/views.py

from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from traffic_app.models import traffic_system
import cv2

def database_display(request):
    return render(request, 'traffic_app/graph_template.html')

def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def video_feed(request):
    return StreamingHttpResponse(generate_frames(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def get_data(request):
    data = list(traffic_system.objects.values('id', 'name', 'date', 'serial_number', 'size', 'line', 'judgement', 'image'))
    for item in data:
        item['image'] = request.build_absolute_uri(item['image'].url)
    return JsonResponse(data, safe=False)
