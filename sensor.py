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
  model.conf = 0.5

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

while 1:

    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for i in range(2, 5):

        try:
            err = f'video{i-1}'
            img_data = requests.get(
                f'http://219.86.140.31:890{i}/cgi-bin/viewer/video.jpg?streamid=0', auth=('root', 'a7075701'), timeout=5)
            
            pic_path = f'leaves/video{i-1}/video{i-1}_{now_time}.png'
            with open(pic_path, 'wb') as handler:
                handler.write(img_data.content)

            err = 'sensor'
            rt = requests.post('http://220.130.108.181:8866/serviceRTU.asmx/FunNoValueGet', json={
            "FunNo": "SF001_TEMP_No4",
            }, timeout=5)
            rh = requests.post('http://220.130.108.181:8866/serviceRTU.asmx/FunNoValueGet', json={
                "FunNo": "SF001_HUMI_No4",
            }, timeout=5)
            
            # print(f"{rt.json()['d']} {rh.json()['d']} {now_time} {detect(pic_path, save_path, i-1)}")
            sensor = requests.post('http://114.33.145.3/api/test_sensor', json={
                "temp": rt.json()['d'],
                "humi": rh.json()['d'],
                "datetime": now_time,
                "health": detect(pic_path, i-1, now_time),
                "video": i-1
            }, timeout=5)

        except:
            print(f"{err} Error")

    time.sleep(60)