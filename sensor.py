import requests
import datetime
import torch
import time

def detect(pic_path, save_path):
  model = torch.hub.load('ultralytics/yolov5', 'custom', path='leaves/best.pt')
  img = pic_path
  model.iou = 0.5
  model.conf = 0.5
  model.img = 1280
  results = model(img)

#   results.print()
  results.save(save_dir = save_path)

while 1:

    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for i in range(2, 5):

        try:
            img_data = requests.get(
                f'http://219.86.140.31:890{i}/cgi-bin/viewer/video.jpg?streamid=0', auth=('root', 'a7075701'), timeout=10)
            
            pic_path = f'leaves/video{i-1}/video{i-1}_{now_time}.jpg'
            save_path = f'leaves/detect{i-1}/exp'
            with open(pic_path, 'wb') as handler:
                handler.write(img_data.content)
            detect(pic_path, save_path)
        except:
            print(f"video{i-1} Error")
        
    try:
        rt = requests.post('http://220.130.108.181:8866/serviceRTU.asmx/FunNoValueGet', json={
            "FunNo": "SF001_TEMP_No4",
        }, timeout=10)
        rh = requests.post('http://220.130.108.181:8866/serviceRTU.asmx/FunNoValueGet', json={
            "FunNo": "SF001_HUMI_No4",
        }, timeout=10)
        
        sensor = requests.post('http://114.33.145.3/api/test_sensor', json={
            "temp": rt.json()['d'],
            "humi": rh.json()['d'],
            "datetime": now_time,
        }, timeout=10)

    except:
        print(f"Sensor Error")


    time.sleep(3600)
