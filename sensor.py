import requests
import datetime
import time
import torch
import cv2
import math
import numpy

def detect(img, video, now_time):
  
  model = torch.hub.load('ultralytics/yolov5', 'custom', path='leaves/best.pt')
  model.iou = 0.5
  model.conf = 0.3

  results = model(img, size=1280)
  results.save(save_dir=f'leaves/detect{video}/exp')
  arr = results.pandas().xyxy[0].to_numpy()

  add_photo = cv2.imread(f'leaves/video{video}_add.png')
  hybrid = numpy.zeros(add_photo.shape)
  total_leaves = 0
  for i in range(0, add_photo.shape[0]):
    for j in range(0, add_photo.shape[1]):
      if (add_photo[i, j] == numpy.array([0, 0, 0])).all():
        total_leaves += 1
      else:
        hybrid[i][j] = numpy.array([255, 255, 255])

  for i in arr:

    flag =0
    for x in range(1,4,2):
      for y in range (0,3,2):
        if (add_photo[math.floor(i[x]), math.floor(i[y])] == numpy.array([255, 255, 255])).all():
          flag = 1
    if flag:
      continue

    for ii in range(math.floor(i[0]), math.floor(i[2])):
      for jj in range(math.floor(i[1]), math.floor(i[3])):
        hybrid[jj][ii] = numpy.array([255, 0, 0])

  blue = 0
  for i in range(0, hybrid.shape[0]):
    for j in range(0, hybrid.shape[1]):
      if (hybrid[i, j] == numpy.array([255, 0, 0])).all():
        blue += 1

  print(f'{(1-blue/total_leaves)*100}%')
  cv2.imwrite(f'leaves/color{video}/color{video}_{now_time}.png', hybrid)
  return (1-blue/total_leaves)*100

account = requests.post('http://114.33.145.3/api/users/login', json={
    "account": "1",
    "password": "1"
}, timeout=5)
accessToken = account.json()['accessToken']
refreshToken = account.json()['refreshToken']

while 1:

    now_time = datetime.datetime.now().strftime('%Y-%m-%d,%H-%M-%S')
    minute_date = datetime.datetime.now().strftime('%Y-%m-%d,%H-%M-%S')[-5:-3]

    if minute_date == '00':
      for i in range(2, 5):

          try:
            err = f'video{i-1}'
            img_data = requests.get(
                f'http://219.86.140.31:890{i}/cgi-bin/viewer/video.jpg?streamid=0', auth=('root', 'a7075701'), timeout=5)
            
            pic_path = f'leaves/video{i-1}/video{i-1}_{now_time}.png'
            with open(pic_path, 'wb') as handler:
                handler.write(img_data.content)
            headers = {'Authorization': f'Bearer {accessToken}'}
            health = requests.post(
                'http://114.33.145.3/api/healthDatas/addHealthData',
                headers=headers,
                json={
                  "value": round(detect(pic_path, i-1, now_time), 1),
                  "smallBlockId": i-1,
                  "sensorId": 3
                }, timeout=5)

            if health.status_code == 403:
              refresh = requests.post('http://114.33.145.3/api/users/token', json={
                "token": refreshToken
              }, timeout=5)
              accessToken = refresh.json()['accessToken']
              refreshToken = refresh.json()['refreshToken']
            headers = {'Authorization': f'Bearer {accessToken}'}
            
            err = 'humidity'
            rh = requests.post('http://220.130.108.181:8866/serviceRTU.asmx/FunNoValueGet', json={
                "FunNo": "SF001_HUMI_No4",
            }, timeout=5)
            humidity = requests.post(
                'http://114.33.145.3/api/humidityDatas/addHumidityData',
                headers=headers,
                json={
                    "value": rh.json()['d'],
                    "smallBlockId": i-1,
                    "sensorId": 2
                }, timeout=5)

            err = 'temperature'
            rt = requests.post('http://220.130.108.181:8866/serviceRTU.asmx/FunNoValueGet', json={
            "FunNo": "SF001_TEMP_No4",
            }, timeout=5)
            temperature = requests.post(
                'http://114.33.145.3/api/temperatureDatas/addtemperatureData',
                headers=headers,
                json={
                    "value": rt.json()['d'],
                    "smallBlockId": i-1,
                    "sensorId": 1
                }, timeout=5)

          except:
            print(f"{err} Error")
      time.sleep(3300)
    else:
        time_aim = str(datetime.datetime.now() + datetime.timedelta(hours=1)
                       )[:13]+':00:00' 
        target_time = datetime.datetime.strptime(time_aim, '%Y-%m-%d %H:%M:%S')   
        delay = (target_time - datetime.datetime.now()
                 ).total_seconds()             
        time.sleep(delay)

